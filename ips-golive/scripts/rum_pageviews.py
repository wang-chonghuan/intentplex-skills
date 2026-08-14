#!/usr/bin/env python3
"""Read Cloudflare Web Analytics (RUM) page views for one site.

This is the *verification* half of capability 1: the dashboard is not evidence a
beacon works, a non-zero row in this dataset is. Prints one line per request
path plus a total, and exits non-zero when the total is 0 so a caller can treat
"no data yet" as a failed check.

    python3 rum_pageviews.py --site-tag <tag> --account <id> [--hours 2]

Credentials come from the environment (never passed on the command line):
    CLOUDFLARE_API_TOKEN                    (preferred)
    CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY   (Global API Key)

Note the ingestion delay: a page view typically lands within ~1-2 minutes. A 0
right after a visit usually means "wait and re-run", not "the beacon is broken".

But a 0 that PERSISTS past ~5 minutes, while the browser really did fetch
/cdn-cgi/rum, is not a timing problem. The usual cause on a DNS-only (grey
cloud) host is the RUM site sitting at auto_install=true: the beacon fires
correctly and Cloudflare records nothing. See capability-3-analytics.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request

GRAPHQL = "https://api.cloudflare.com/client/v4/graphql"

QUERY = """
query($acct:String!,$site:String!,$since:Time!,$until:Time!){
  viewer{
    accounts(filter:{accountTag:$acct}){
      rumPageloadEventsAdaptiveGroups(
        limit:100,
        filter:{siteTag:$site, datetime_geq:$since, datetime_leq:$until},
        orderBy:[count_DESC]
      ){ count dimensions{ requestPath } }
    }
  }
}
"""


def auth_headers() -> dict[str, str]:
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    email = os.environ.get("CLOUDFLARE_EMAIL")
    key = os.environ.get("CLOUDFLARE_API_KEY")
    if email and key:
        return {"X-Auth-Email": email, "X-Auth-Key": key}
    sys.exit(
        "ips-golive: no credential. Set CLOUDFLARE_API_TOKEN, or "
        "CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY, in ~/.zshrc"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-tag", required=True, help="RUM site_tag from site_info")
    ap.add_argument("--account", required=True, help="Cloudflare account id")
    ap.add_argument("--hours", type=float, default=2.0, help="look-back window")
    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    since = (now - dt.timedelta(hours=args.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    until = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    body = json.dumps(
        {
            "query": QUERY,
            "variables": {
                "acct": args.account,
                "site": args.site_tag,
                "since": since,
                "until": until,
            },
        }
    ).encode()

    headers = auth_headers() | {"Content-Type": "application/json"}
    with urllib.request.urlopen(urllib.request.Request(GRAPHQL, data=body, headers=headers)) as fh:
        payload = json.load(fh)

    if payload.get("errors"):
        print("GraphQL errors:", json.dumps(payload["errors"], ensure_ascii=False))
        return 2

    accounts = payload["data"]["viewer"]["accounts"]
    rows = accounts[0]["rumPageloadEventsAdaptiveGroups"] if accounts else []
    total = sum(r["count"] for r in rows)

    print(f"window {since} -> {until}")
    for r in rows:
        print(f"  {r['count']:>5}  {r['dimensions']['requestPath']}")
    print(f"total page views: {total}")

    if total == 0:
        print("  (0 — if you just visited the site, wait ~1-2 min and re-run)")
        print("  (still 0 after ~5 min? stop polling. Check auto_install on this")
        print("   site: on a grey-cloud host, auto_install=true silently drops")
        print("   manual-beacon data. See capability-3-analytics.md)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
