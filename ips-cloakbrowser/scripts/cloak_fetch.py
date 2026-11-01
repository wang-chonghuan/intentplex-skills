"""Print a web page as the CloakBrowser stealth Chromium renders it.

cloak-fetch URL                  title, final URL, HTTP status, visible text
cloak-fetch URL --html           rendered HTML
cloak-fetch URL --screenshot F   full-page PNG written to F
"""

import argparse
import os
import sys

# cloak-update owns downloads; a one-shot fetch never starts one.
os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")

from cloakbrowser import launch_context  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(prog="cloak-fetch", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--html", action="store_true", help="print the rendered HTML instead of text")
    output.add_argument("--screenshot", metavar="PATH", help="save a full-page PNG to PATH")
    parser.add_argument("--headed", action="store_true", help="open a real window (some sites block headless)")
    parser.add_argument("--wait", type=float, default=1.5, metavar="SEC", help="settle time after load; raise to ~8 for challenge pages (default 1.5)")
    parser.add_argument("--timeout", type=float, default=60, metavar="SEC", help="navigation timeout (default 60)")
    args = parser.parse_args()

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
