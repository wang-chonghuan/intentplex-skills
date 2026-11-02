"""Print a web page as the CloakBrowser stealth Chromium renders it.

cloak-fetch URL                  title, final URL, HTTP status, visible text
cloak-fetch URL --html           rendered HTML
cloak-fetch URL --screenshot F   full-page PNG written to F
cloak-fetch URL --redirect-only  JSON response headers, without following redirects
cloak-fetch --redirect-session   JSON Lines on stdin/stdout, one browser for the session

With no usable license key it starts the keyless local browser on Colima and reads through that.

Exit codes: 0 page read, 75 no license seat free in time, 1 anything else.
"""

import argparse
import json
import math
import os
import re
import signal
import socket
import subprocess
import sys
import time

# cloak-update owns downloads; a one-shot fetch never starts one.
os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")

import httpx  # noqa: E402
from cloakbrowser import CloakBrowserLicenseError, launch_context  # noqa: E402
from cloakbrowser.license import VALIDATE_URL, resolve_license_key  # noqa: E402
from playwright.sync_api import Error as PlaywrightError, sync_playwright  # noqa: E402

SEAT_RETRY_SEC = 15
EXIT_NO_SEAT = 75
LOCAL_PORT = 19222
LOCAL_READY_SEC = 90


def read_redirect(page, args: argparse.Namespace) -> dict:
    """Use Chromium's response interception, not an APIRequestContext."""
    session = page.context.new_cdp_session(page)
    frame_id = session.send("Page.getFrameTree")["frameTree"]["frame"]["id"]
    result = {}
    redirect_seen = False

    def response_paused(event):
        nonlocal result, redirect_seen
        request_id = event["requestId"]
        status = event.get("responseStatusCode")
        # Late script-initiated navigation may schedule the redirect's next
        # request before the aborted response is observed by Playwright.
        if status is None:
            if (
                event.get("frameId") == frame_id
                and event["request"]["url"] != args.url
                and (redirect_seen or event.get("redirectedRequestId"))
            ):
                session.send("Fetch.failRequest", {"requestId": request_id, "errorReason": "Aborted"})
                return
            session.send("Fetch.continueRequest", {"requestId": request_id})
            return
        if event.get("frameId") == frame_id and status is not None:
            headers = {
                header["name"].lower(): header["value"]
                for header in event.get("responseHeaders", [])
                if header["name"].lower() in {"location", "cf-mitigated", "retry-after"}
            }
            result = {"url": event["request"]["url"], "status": status, "headers": headers}
            if 300 <= status < 400 and "location" in headers:
                redirect_seen = True
                session.send("Fetch.failRequest", {"requestId": request_id, "errorReason": "Aborted"})
                return
        session.send("Fetch.continueRequest", {"requestId": request_id})

    session.on("Fetch.requestPaused", response_paused)
    session.send("Fetch.enable", {"patterns": [
        {"urlPattern": "*", "resourceType": "Document", "requestStage": "Request"},
        {"urlPattern": "*", "resourceType": "Document", "requestStage": "Response"},
    ]})
    try:
        page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
    except PlaywrightError:
        if not redirect_seen:
            raise
    # Pump browser events while a challenge finishes; a redirect ends the wait early.
    deadline = time.monotonic() + args.wait
    while not redirect_seen and time.monotonic() < deadline:
        page.wait_for_timeout(min(100, max(0, (deadline - time.monotonic()) * 1000)))
    if not result:
        raise RuntimeError("no document response received")
    return result


def serve_redirects(context, args: argparse.Namespace, source=None, output=None) -> int:
    source = sys.stdin if source is None else source
    output = sys.stdout if output is None else output

    def emit(value):
        print(json.dumps(value), file=output, flush=True)

    emit({"event": "ready", "protocol": 1, "capabilities": ["item-errors"]})
    for line in source:
        try:
            request = json.loads(line)
            if not isinstance(request, dict) or not isinstance(request.get("url"), str):
                raise ValueError("invalid request")
        except (ValueError, TypeError):
            emit({"event": "error", "reason": "invalid-request"})
            return 1
        page = None
        try:
            page = context.new_page()
            navigation = argparse.Namespace(url=request["url"], timeout=args.timeout, wait=args.wait)
            emit(read_redirect(page, navigation))
        except CloakBrowserLicenseError:
            emit({"event": "error", "reason": "license-denied"})
            return EXIT_NO_SEAT
        except PlaywrightError as exc:
            # Never emit the exception text: Playwright includes URLs and call logs.
            code = re.search(r"net::ERR_[A-Z_]+", str(exc))
            broken = "has been closed" in str(exc) or (
                context.browser is not None and not context.browser.is_connected()
            )
            emit({
                "event": "error",
                "scope": "session" if broken else "item",
                "url": request["url"],
                "reason": code.group(0) if code else (
                    "browser-closed" if broken else type(exc).__name__
                ),
            })
            if broken:
                return 1
        except Exception:
            emit({"event": "error", "scope": "session", "reason": "navigation-failed"})
            return 1
        finally:
            if page is not None:
                try:
                    page.close()
                except PlaywrightError:
                    pass  # a failed browser is already being retired by the caller
    return 0


def read_with(context, args: argparse.Namespace) -> int:
    try:
        if args.redirect_session:
            return serve_redirects(context, args)
        page = context.new_page()
        if args.redirect_only:
            print(json.dumps(read_redirect(page, args)))
            return 0
        response = page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
        try:
            page.wait_for_load_state("load", timeout=min(args.timeout, 15) * 1000)
        except Exception:
            pass  # slow subresources; the DOM is already there
        page.wait_for_timeout(args.wait * 1000)

        if args.screenshot:
            page.screenshot(path=args.screenshot, full_page=True)
            print(os.path.abspath(args.screenshot))
        elif args.html:
            print(page.content())
        else:
            status = response.status if response else "unknown"
            print(f"# {page.title()}\nURL: {page.url}\nStatus: {status}\n")
            print(page.inner_text("body"))
        return 0
    finally:
        context.close()
        if args.redirect_session:
            print(json.dumps({"event": "closed"}), flush=True)


def fetch(args: argparse.Namespace) -> int:
    return read_with(launch_context(headless=not args.headed), args)


def local_running() -> bool:
    try:
        socket.create_connection(("127.0.0.1", LOCAL_PORT), timeout=1).close()
        return True
    except OSError:
        return False


def key_usable() -> bool:
    # Ask the server: the wrapper's own answer is cached for a day.
    key = resolve_license_key()
    if not key:
        return False
    try:
        response = httpx.post(VALIDATE_URL, json={"license_key": key}, timeout=5)
        response.raise_for_status()
        return response.json().get("valid") is True
    except (httpx.HTTPError, ValueError):
        return False


def start_local() -> None:
    env = {**os.environ, "PATH": f"{os.environ.get('PATH', '')}:/opt/homebrew/bin:/usr/local/bin"}
    # `colima start` switches the current docker context; another project's profile must not lose it.
    context = subprocess.run(["docker", "context", "show"], env=env, capture_output=True, text=True).stdout.strip()
    # stdout carries the --redirect-session protocol.
    subprocess.run(["colima", "start", "cloakbrowser"], env=env, stdout=sys.stderr, check=True, timeout=300)
    if context:
        subprocess.run(["docker", "context", "use", context], env=env, capture_output=True)
    deadline = time.monotonic() + LOCAL_READY_SEC
    while not local_running():
        if time.monotonic() >= deadline:
            raise RuntimeError(f"the local browser did not open port {LOCAL_PORT} within {LOCAL_READY_SEC}s")
        time.sleep(1)


def fetch_local(args: argparse.Namespace) -> int:
    print("cloak-fetch: no usable license key, using the local browser on Colima", file=sys.stderr)
    if not local_running():
        start_local()
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{LOCAL_PORT}")
        return read_with(browser.new_context(no_viewport=True), args)


def main() -> int:
    parser = argparse.ArgumentParser(prog="cloak-fetch", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", nargs="?")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--html", action="store_true", help="print the rendered HTML instead of text")
    output.add_argument("--screenshot", metavar="PATH", help="save a full-page PNG to PATH")
    output.add_argument("--redirect-only", action="store_true", help="print JSON status and Location/cf-mitigated/Retry-After headers; stop before following an HTTP redirect")
    output.add_argument("--redirect-session", action="store_true", help="read one JSON {url} per stdin line and flush one response per line; reuse one browser until EOF")
    parser.add_argument("--headed", action="store_true", help="open a real window (some sites block headless)")
    parser.add_argument("--wait", type=float, default=1.5, metavar="SEC", help="settle time after load; raise to ~8 for challenge pages (default 1.5)")
    parser.add_argument("--timeout", type=float, default=60, metavar="SEC", help="navigation timeout (default 60)")
    parser.add_argument("--seat-wait", type=float, default=90, metavar="SEC", help="how long to wait for a free license seat (default 90)")
    args = parser.parse_args()
    if args.redirect_session and args.url:
        parser.error("--redirect-session reads URLs from stdin, not a positional URL")
    if not args.redirect_session and not args.url:
        parser.error("a URL is required")
    for name in ("wait", "timeout", "seat_wait"):
        value = getattr(args, name)
        if not math.isfinite(value) or value < 0 or (name == "timeout" and value == 0):
            parser.error(f"--{name.replace('_', '-')} must be finite and {'positive' if name == 'timeout' else 'non-negative'}")

    # A killed browser keeps its license seat for minutes, so let `finally` close it on SIGTERM.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))

    if not key_usable():
        return fetch_local(args)

    deadline = time.monotonic() + args.seat_wait
    while True:
        try:
            return fetch(args)
        except CloakBrowserLicenseError as exc:
            if "session limit" not in str(exc):
                return fetch_local(args)
            if time.monotonic() >= deadline:
                print("cloak-fetch: another browser holds the only license seat; retry later or pass --seat-wait 300", file=sys.stderr)
                return EXIT_NO_SEAT
            print(f"cloak-fetch: license seat busy, retrying in {SEAT_RETRY_SEC}s", file=sys.stderr)
            time.sleep(SEAT_RETRY_SEC)


if __name__ == "__main__":
    sys.exit(main())
