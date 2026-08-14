#!/usr/bin/env python3
"""ips-xhistory normalizer.

Merge raw captures from the browser collector into a searchable local archive.

    python3 normalize.py --raw <dir> --out <dir> [--since 2026-07-15] [--until 2026-08-14]

Writes archive.jsonl (master), index.md (human list), domains.tsv (frequency).
Fails loudly if CJK text did not survive clipboard transport.
"""
import argparse
import json
import pathlib
import re
import sys
from collections import Counter
from urllib.parse import urlparse

SHORTENERS = {"t.co", "bit.ly", "buff.ly", "lnkd.in", "dlvr.it", "ift.tt"}
CJK = re.compile(r"[一-鿿]")
# Display text of a link, e.g. "github.com/ReScienceLab/opc-skills"
DISPLAY_DOMAIN = re.compile(r"^(?:https?://)?([a-z0-9.-]+\.[a-z]{2,})(?:/|$)", re.I)


def domains_of(rec):
    out = []
    for link in rec.get("links") or []:
        href, text = link.get("href") or "", (link.get("text") or "").strip()
        host = (urlparse(href).hostname or "").lower().lstrip("www.")
        # t.co hides the real target; the anchor's display text carries it.
        # X renders that text across several spans, so it arrives with newlines
        # embedded mid-URL ("https://\nmp.weixin.qq.com/s/..."). Strip all
        # whitespace and the elision marker before matching.
        if not host or host in SHORTENERS:
            flat = re.sub(r"\s+", "", text).replace("…", "")
            m = DISPLAY_DOMAIN.match(flat)
            host = m.group(1).lower() if m else ""
        if host and host not in out and host != "x.com":
            out.append(host)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--since")
    ap.add_argument("--until")
    args = ap.parse_args()

    raw_dir, out_dir = pathlib.Path(args.raw), pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    merged, files = {}, sorted(raw_dir.glob("*.json"))
    if not files:
        sys.exit(f"no raw capture files in {raw_dir}")
    for f in files:
        for rec in json.loads(f.read_text(encoding="utf-8")):
            merged[f"{rec['source']}:{rec['id']}"] = rec

    records = list(merged.values())
    if not records:
        sys.exit("raw files contained no records")

    # Transport check: the collector escapes non-ASCII, so CJK must come back intact.
    if not any(CJK.search(r.get("text", "") or "") for r in records):
        print(
            "WARNING: no CJK found in any record. If the source posts were Chinese, "
            "the clipboard transport corrupted the payload — re-export before trusting this.",
            file=sys.stderr,
        )

    kept = []
    for r in records:
        ts = r.get("posted_at") or ""
        if args.since and ts[:10] < args.since:
            continue
        if args.until and ts[:10] > args.until:
            continue
        r["domains"] = domains_of(r)
        kept.append(r)
    kept.sort(key=lambda r: r.get("posted_at") or "", reverse=True)

    archive = out_dir / "archive.jsonl"
    with archive.open("w", encoding="utf-8") as fh:
        for r in kept:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    counts = Counter(d for r in kept for d in r["domains"])
    (out_dir / "domains.tsv").write_text(
        "".join(f"{n}\t{d}\n" for d, n in counts.most_common()), encoding="utf-8"
    )

    lines = ["# X 收藏与点赞归档", ""]
    span = f"{kept[-1]['posted_at'][:10]} — {kept[0]['posted_at'][:10]}" if kept else "空"
    n_bm = sum(1 for r in kept if r["source"] == "bookmark")
    lines += [f"共 {len(kept)} 条（书签 {n_bm}，点赞 {len(kept) - n_bm}），发帖日期跨度 {span}。", ""]
    for r in kept:
        mark = " …(原文被折叠)" if r.get("truncated") else ""
        head = (r.get("text") or "").strip().split("\n")[0][:70]
        lines.append(f"- `{r['posted_at'][:10]}` **{r['handle']}** [{head}{mark}]({r['url']})")
        if r["domains"]:
            lines.append(f"  - 链接：{', '.join(r['domains'])}")
    (out_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"raw files      : {len(files)}")
    print(f"merged unique  : {len(records)}")
    print(f"after date fltr: {len(kept)}  -> {archive}")
    print(f"truncated posts: {sum(1 for r in kept if r.get('truncated'))}")
    print(f"distinct domains: {len(counts)}  top: {', '.join(d for d, _ in counts.most_common(5))}")


if __name__ == "__main__":
    main()
