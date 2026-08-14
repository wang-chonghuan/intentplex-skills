---
name: ips-xhistory
description: Pull the user's own X (Twitter) Bookmarks and Likes into a local JSON/JSONL archive over a given date range, using the Claude in Chrome extension against their logged-in session. Load when the user says "ips-xhistory", "把我的 X 收藏拉下来", "导出我的推特书签", "抓一下我的点赞", "export my X bookmarks/likes", or asks to search/index what they saved on X. Do not load for reading other people's timelines, for posting to X, or for anything requiring the paid X API.
---

# ips-xhistory

Export the signed-in user's **Bookmarks** and **Likes** to local files — no paid API, no clicking in the browser.

## Why this exists

X's official API charges $200/month minimum for the bookmarks endpoint, and the free data archive omits bookmarks entirely. The workable path is the user's own logged-in session through the Claude in Chrome extension.

Do **not** scrape the rendered timeline. X's web client fetches every page from a cursor-paginated GraphQL endpoint, and that request can be replayed from the page: ~100 items per call, no virtualized list, no scrolling, no UI throttle. It also yields better data than the DOM — full text of long posts, and already-expanded URLs instead of `t.co` shorteners.

Measured 2026-08-14: **5,019 items (2,522 bookmarks + 2,497 likes, back past January) in four calls.** An earlier DOM-scrolling implementation managed 98 items across several dozen calls before X throttled it dead. That approach is abandoned; it is not a fallback worth trying.

Before improvising an alternative, read `references/dead-ends.md` — it lists what was tried against a live session and verifiably failed, including several things that look obviously workable and are not.

**This is bulk collection and the host may gate it.** It reads only the user's own saved items and writes nothing — no likes, follows, posts, or deletions. If a permission prompt appears, stop and let the user decide; never route around a denial.

## URLs and layout (as of 2026-08)

X replaced the standalone bookmarks page with a combined **History** page; both old URLs redirect there.

| List | Page | GraphQL operation |
|---|---|---|
| Bookmarks | `https://x.com/i/history` | `/i/api/graphql/<queryId>/Bookmarks` — variables `{count, cursor, includePromotedContent}` |
| Likes | `https://x.com/i/history/likes` | `/i/api/graphql/<queryId>/Likes` — variables `{userId, count, cursor, …}` |

## Procedure

### 1. Preconditions

`list_connected_browsers` — an empty array means the Claude in Chrome extension is not connected; stop and ask the user to sign in to the extension side panel. The in-app browser pane has no X session and will hit the login wall.

Ask for the date range if not given.

### 2. Capture the endpoint

`read_network_requests` starts tracking on its first call, so call it once, then click the tab you want and scroll a little to make the app fire its query, then read it back with `urlPattern: "Bookmarks"` or `"Likes"`.

**Injecting a `window.fetch` hook does not work** — X captures its own `fetch` reference before any injected code runs, so nothing is recorded. The network tool is the only way in.

The `queryId` changes between X builds. Always capture it fresh; never hardcode it.

### 3. Harvest

Inject `scripts/harvest.js` (defines `__H`, `__parse`, `__extract`, `__harvest`, `__gCopy`), then run one list at a time, resetting the cursor between them:

```
window.__G.cursor = null;
await window.__harvest(<captured url>, 'bookmark', 12)
```

Twelve pages fits inside the 45-second CDP timeout. Repeat until `stop` is `no-cursor`, or until deep enough for the requested range.

### 4. Export after every call

1. `computer` `left_click` on the "History" heading (~`[305, 36]`) to give the document focus — `navigator.clipboard.writeText` throws `NotAllowedError: Document is not focused` without it.
2. `await window.__gCopy()`
3. Host side: `pbpaste > <outdir>/raw/<YYYY-MM-DD>-x-api-NN.json`

The map holds both sources, so every export is a complete superset — overwriting the same file is correct and loses nothing.

### 5. Normalize

```
python3 scripts/normalize.py --raw <outdir>/raw --out <outdir> [--since 2026-07-13]
```

Merges all raw files, dedupes on `source:id`, extracts domains, filters by date, and writes `archive.jsonl` (searchable master), `index.md` (human list), `domains.tsv` (frequency, most-saved first). Run it twice — once unfiltered for the full archive, once with `--since` into a subdirectory for the requested window.

### 6. Search

```
rg -i "seo" archive.jsonl
jq -r 'select(.domains[]? | contains("github")) | .url' archive.jsonl
jq -r .handle archive.jsonl | sort | uniq -c | sort -rn | head        # who you save most
head -30 domains.tsv                                                  # what you save most
```

## Traps

All four are already handled in `harvest.js`, but they explain why it looks the way it does.

1. **Take only top-level entries.** A recursive hunt for `__typename === 'Tweet'` also collects quoted and retweeted posts nested inside each entry. Those can be years old and will wreck any date logic — an early run reported "oldest 2022-04-04" on page one. Match `entryId` starting with `tweet-` instead, and read the bottom cursor from `entryId` starting with `cursor-bottom`.
2. **Post date is not monotonic.** Both lists are ordered by *save* time, and something saved yesterday may have been posted in 2022. Never stop paginating on "the oldest post is older than X" — run to `no-cursor` (or a generous page cap) and filter by date afterwards.
3. **Escape non-ASCII before copying.** `pbpaste` corrupted a raw UTF-8 payload at byte 621 and destroyed every Chinese character. `harvest.js` emits `\uXXXX` escapes, which are valid JSON, so the host parses it back losslessly. `normalize.py` warns if no CJK survives.
4. **Clipboard needs document focus** — see step 4.

## Limits to state up front

- **Save time is not exposed.** Records carry the *post* timestamp only; `order` preserves list position, which is the closest stand-in for save order. Date filtering is therefore by post date — say so rather than implying the window is exact.
- Bookmark folders exist; this reads `All Bookmarks`, the default.

## Record shape

```json
{
  "id": "2088246847093534868",
  "source": "bookmark",
  "url": "https://x.com/GoSailGlobal/status/2088246847093534868",
  "handle": "@GoSailGlobal",
  "name": "Jason Zhu",
  "posted_at": "2026-08-14T12:50:20.000Z",
  "text": "full text, including long-form posts",
  "truncated": false,
  "links": [{"href": "https://github.com/…", "text": "github.com/…"}],
  "domains": ["github.com"],
  "has_media": true,
  "order": 0
}
```

## Scope

Reads only the signed-in user's own Bookmarks and Likes. It does not post, like, follow, or unbookmark; it cannot read other accounts' saved items; it never touches the paid X API.
