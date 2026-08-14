#!/usr/bin/env python3
"""Product-readiness audit for a deployed site. Read-only.

Answers one question: what still stands between this deployment and a real,
addressable, measurable public web property? Every check is decided from the
live site, never from a repo or from what someone remembers configuring.

    python3 readiness_audit.py https://example.com [--json]

Exit code: 0 when nothing FAILs, 1 when any check FAILs (WARN never fails the
run — it flags something worth a decision, not a defect).

Standard library only. `dig` is used for DNS when available; its absence
degrades those checks to SKIP rather than failing the audit.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

UA = "ips-golive-readiness-audit/1"
TIMEOUT = 15

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"
results: list[dict] = []


def record(section: str, name: str, status: str, detail: str = "") -> None:
    results.append({"section": section, "check": name, "status": status, "detail": detail})


def fetch(url: str, method: str = "GET", redirect: bool = True):
    """Return (status, headers, body_text, final_url) or (None, None, None, err).

    `headers` is urllib's case-insensitive Message, not a plain dict — callers
    look up names like "Location" that servers may send lowercased.
    """

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(*([] if redirect else [NoRedirect]))
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            raw = r.read(600_000)
            # Keep the Message object: it is case-insensitive, and servers send
            # header names in whatever case they like (`location:` is common).
            return r.status, r.headers, raw.decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, "", e.headers.get("Location", "") or url
    except Exception as e:  # noqa: BLE001 - any transport failure is just "unreachable"
        return None, None, None, str(e)


def dig(name: str, rtype: str) -> list[str]:
    """Resolve a record, falling back to public resolvers.

    The local resolver may still be serving a cached negative answer for a
    record that is already live — which shows up as a freshly added
    verification TXT being reported as missing. A public resolver is what the
    verifying service actually queries, so treat it as authoritative here.
    """
    if not shutil.which("dig"):
        return []
    for server in ("", "@8.8.8.8", "@1.1.1.1"):
        cmd = ["dig", "+short", name, rtype] + ([server] if server else [])
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except Exception:  # noqa: BLE001
            continue
        values = [l.strip().strip('"') for l in out.stdout.splitlines() if l.strip()]
        if values:
            return values
    return []


# --------------------------------------------------------------------------- checks
def check_reachability(base: str) -> str | None:
    status, headers, body, final = fetch(base)
    if status is None:
        record("reachability", "site responds", FAIL, f"{base}: {final}")
        return None
    if status >= 400:
        record("reachability", "site responds", FAIL, f"HTTP {status}")
        return None
    record("reachability", "site responds", PASS, f"HTTP {status}")
    server = (headers or {}).get("cf-ray")
    record(
        "reachability",
        "edge",
        PASS,
        "behind Cloudflare (proxied)" if server else "direct to origin (DNS only)",
    )
    return body


def check_tls(host: str) -> None:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
            tzinfo=timezone.utc
        )
        days = (not_after - datetime.now(timezone.utc)).days
        issuer = dict(x[0] for x in cert["issuer"]).get("organizationName", "?")
        if days < 0:
            record("tls", "certificate", FAIL, f"expired {abs(days)}d ago")
        elif days < 15:
            record("tls", "certificate", WARN, f"expires in {days}d (issuer {issuer})")
        else:
            record("tls", "certificate", PASS, f"valid {days}d, issuer {issuer}")
    except Exception as e:  # noqa: BLE001
        record("tls", "certificate", FAIL, str(e))


def check_redirects(host: str) -> None:
    status, headers, _, _ = fetch(f"http://{host}/", redirect=False)
    if status is None:
        record("addressing", "http -> https", WARN, "http did not respond")
    elif status in (301, 308) and (headers or {}).get("Location", "").startswith("https://"):
        record("addressing", "http -> https", PASS, f"{status}")
    elif status in (302, 307) and (headers or {}).get("Location", "").startswith("https://"):
        record("addressing", "http -> https", WARN, f"{status} (prefer a permanent 301/308)")
    else:
        record("addressing", "http -> https", FAIL, f"got {status}")

    apex = host[4:] if host.startswith("www.") else host
    other = apex if host.startswith("www.") else f"www.{apex}"
    if not dig(other, "A") and not dig(other, "CNAME"):
        record("addressing", f"{other} exists", WARN, "no DNS record — one host is unreachable")
        return
    status, headers, _, _ = fetch(f"https://{other}/", redirect=False)
    loc = (headers or {}).get("Location", "")
    if status in (301, 308) and host in loc:
        record("addressing", f"{other} -> canonical host", PASS, f"{status} -> {loc}")
    elif status in (302, 307) and host in loc:
        record("addressing", f"{other} -> canonical host", WARN, f"{status} (prefer 301/308)")
    elif status == 200:
        record(
            "addressing",
            f"{other} -> canonical host",
            FAIL,
            "serves 200 — the same content on two hosts splits ranking signals",
        )
    else:
        record("addressing", f"{other} -> canonical host", WARN, f"status {status}")


def meta(html: str, attr: str, value: str) -> str | None:
    m = re.search(
        rf'<meta[^>]+{attr}=["\']{re.escape(value)}["\'][^>]*content=["\']([^"\']*)["\']',
        html,
        re.I,
    ) or re.search(
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]*{attr}=["\']{re.escape(value)}["\']',
        html,
        re.I,
    )
    return m.group(1) if m else None


def check_identity(base: str, html: str) -> None:
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if title and title.group(1).strip():
        record("identity", "title", PASS, title.group(1).strip()[:70])
    else:
        record("identity", "title", FAIL, "missing")

    desc = meta(html, "name", "description")
    record("identity", "meta description", PASS if desc else FAIL, (desc or "missing")[:70])

    canon = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    if not canon:
        record("identity", "canonical", FAIL, "missing")
    elif urlparse(canon.group(1)).netloc == urlparse(base).netloc:
        record("identity", "canonical", PASS, canon.group(1))
    else:
        record("identity", "canonical", FAIL, f"points off-host: {canon.group(1)}")


def check_share(base: str, html: str) -> None:
    for prop, required in (("og:title", True), ("og:description", True), ("og:image", True),
                           ("og:url", False), ("og:type", False)):
        v = meta(html, "property", prop)
        if v:
            record("share", prop, PASS, v[:60])
        else:
            record("share", prop, FAIL if required else WARN, "missing")

    card = meta(html, "name", "twitter:card")
    record("share", "twitter:card", PASS if card else WARN, card or "missing")

    img = meta(html, "property", "og:image")
    if img:
        status, _, _, _ = fetch(urljoin(base, img))
        record("share", "og:image reachable", PASS if status == 200 else FAIL, f"HTTP {status}")

    icon = re.search(r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    if icon:
        status, _, _, _ = fetch(urljoin(base, icon.group(1)))
        record("share", "favicon reachable", PASS if status == 200 else FAIL, f"HTTP {status}")
    else:
        record("share", "favicon", FAIL, "no icon link")


def check_crawl(base: str) -> None:
    status, _, body, _ = fetch(urljoin(base, "/robots.txt"))
    if status == 200 and body:
        record("crawl", "robots.txt", PASS, f"{len(body.splitlines())} lines")
        if re.search(r"^\s*sitemap:", body, re.I | re.M):
            record("crawl", "robots references sitemap", PASS)
        else:
            record("crawl", "robots references sitemap", WARN, "no Sitemap: line")
        if re.search(r"^\s*disallow:\s*/\s*$", body, re.I | re.M):
            record("crawl", "robots does not block all", FAIL, "Disallow: / blocks every crawler")
    else:
        record("crawl", "robots.txt", FAIL, f"HTTP {status}")
        record("crawl", "robots references sitemap", SKIP)

    status, _, body, _ = fetch(urljoin(base, "/sitemap.xml"))
    if status == 200 and body:
        try:
            root = ET.fromstring(body)
            urls = [e.text for e in root.iter() if e.tag.endswith("loc") and e.text]
            record("crawl", "sitemap.xml", PASS, f"{len(urls)} urls")
        except ET.ParseError as e:
            record("crawl", "sitemap.xml", FAIL, f"not valid XML: {e}")
    else:
        record("crawl", "sitemap.xml", FAIL, f"HTTP {status}")

    status, _, _, _ = fetch(urljoin(base, "/llms.txt"))
    record(
        "crawl",
        "llms.txt (AI-citation base)",
        PASS if status == 200 else WARN,
        f"HTTP {status}",
    )


def check_measurement(host: str, html: str) -> None:
    beacons = {
        "Cloudflare Web Analytics": "static.cloudflareinsights.com/beacon.min.js",
        "Google Analytics (gtag)": "googletagmanager.com/gtag/js",
        "Plausible": "plausible.io/js",
        "Umami": "umami",
    }
    found = [n for n, sig in beacons.items() if sig in html]
    if found:
        record("measurement", "analytics beacon", PASS, ", ".join(found))
    else:
        record("measurement", "analytics beacon", FAIL, "no analytics script in the served HTML")

    txt = " ".join(dig(host, "TXT"))
    if not txt and not shutil.which("dig"):
        record("measurement", "search console verification", SKIP, "dig unavailable")
        return
    checks = {
        "Google Search Console": "google-site-verification",
        "Bing Webmaster": "msvalidate",
    }
    for label, needle in checks.items():
        if needle in txt.lower():
            record("measurement", f"{label} verified", PASS, "DNS TXT present")
        else:
            record(
                "measurement",
                f"{label} verified",
                WARN,
                "no DNS TXT — history only starts once verified, so do it early",
            )


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="the site's canonical https URL, e.g. https://example.com")
    ap.add_argument("--json", action="store_true", help="emit machine-readable results")
    args = ap.parse_args()

    base = args.url if "://" in args.url else f"https://{args.url}"
    host = urlparse(base).netloc

    html = check_reachability(base)
    if html is None:
        print(json.dumps(results, indent=2) if args.json else "site unreachable — nothing else can be judged")
        return 1

    check_tls(host)
    check_redirects(host)
    check_identity(base, html)
    check_share(base, html)
    check_crawl(base)
    check_measurement(host, html)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        icons = {PASS: "PASS", WARN: "WARN", FAIL: "FAIL", SKIP: "SKIP"}
        section = None
        for r in results:
            if r["section"] != section:
                section = r["section"]
                print(f"\n[{section}]")
            detail = f"  — {r['detail']}" if r["detail"] else ""
            print(f"  {icons[r['status']]:<5} {r['check']}{detail}")
        n_fail = sum(1 for r in results if r["status"] == FAIL)
        n_warn = sum(1 for r in results if r["status"] == WARN)
        print(f"\n{len(results)} checks · {n_fail} FAIL · {n_warn} WARN")
        if n_fail:
            print("not product-ready yet — every FAIL is a gap between deployment and a real site")

    return 1 if any(r["status"] == FAIL for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
