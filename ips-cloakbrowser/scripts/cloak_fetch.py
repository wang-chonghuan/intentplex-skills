"""Print a web page as the CloakBrowser stealth Chromium renders it.

cloak-fetch URL                  title, final URL, HTTP status, visible text
cloak-fetch URL --html           rendered HTML
cloak-fetch URL --screenshot F   full-page PNG written to F

Exit codes: 0 page read, 75 no license seat free in time, 1 anything else.
"""

import argparse
import os
import signal
import sys
import time

# cloak-update owns downloads; a one-shot fetch never starts one.
os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")

from cloakbrowser import CloakBrowserLicenseError, launch_context  # noqa: E402

SEAT_RETRY_SEC = 15
EXIT_NO_SEAT = 75


def fetch(args: argparse.Namespace) -> None:
    context = launch_context(headless=not args.headed)
    try:
        page = context.new_page()
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
    finally:
        context.close()


def main() -> int:
    parser = argparse.ArgumentParser(prog="cloak-fetch", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--html", action="store_true", help="print the rendered HTML instead of text")
    output.add_argument("--screenshot", metavar="PATH", help="save a full-page PNG to PATH")
    parser.add_argument("--headed", action="store_true", help="open a real window (some sites block headless)")
    parser.add_argument("--wait", type=float, default=1.5, metavar="SEC", help="settle time after load; raise to ~8 for challenge pages (default 1.5)")
    parser.add_argument("--timeout", type=float, default=60, metavar="SEC", help="navigation timeout (default 60)")
    parser.add_argument("--seat-wait", type=float, default=90, metavar="SEC", help="how long to wait for a free license seat (default 90)")
    args = parser.parse_args()

    # A killed browser keeps its license seat for minutes, so let `finally` close it on SIGTERM.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))

    deadline = time.monotonic() + args.seat_wait
    while True:
        try:
            fetch(args)
            return 0
        except CloakBrowserLicenseError as exc:
            if "session limit" not in str(exc):
                print(f"cloak-fetch: {exc}", file=sys.stderr)
                return 1
            if time.monotonic() >= deadline:
                print("cloak-fetch: another browser holds the only license seat; retry later or pass --seat-wait 300", file=sys.stderr)
                return EXIT_NO_SEAT
            print(f"cloak-fetch: license seat busy, retrying in {SEAT_RETRY_SEC}s", file=sys.stderr)
            time.sleep(SEAT_RETRY_SEC)


if __name__ == "__main__":
    sys.exit(main())
