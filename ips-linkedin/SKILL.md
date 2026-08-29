---
name: ips-linkedin
description: Pull the signed-in user's own LinkedIn posts and Pulse articles into a local JSON archive, with images, using the Claude in Chrome extension against their logged-in session. Load when the user says "ips-linkedin", "把我的 LinkedIn 帖子拉下来", "导出我的领英文章", "export my LinkedIn posts/articles", or wants their own LinkedIn writing mirrored somewhere else. Do not load for reading other people's profiles, for posting to LinkedIn, for scraping company pages, or for anything requiring the paid LinkedIn API.
---

# ips-linkedin

Export the signed-in user's **posts** and **Pulse articles** to local JSON — no paid API, no clicking through the feed.

## Why this exists

LinkedIn's official data export takes hours to prepare and its article bodies come back as bare HTML dumps. The profile UI is worse: the activity feed is virtualized, so **only ~5 items exist in the DOM at any moment** no matter how far you scroll.

Do **not** scrape the rendered feed. LinkedIn's own SPA fetches every page from the **Voyager GraphQL API**, and that request can be replayed from the page: 50 items per call, cursor-paginated, no virtualized list, no scrolling.

Measured 2026-08-15 against a live account: **231 activities in 5 calls, spanning 21 months — 156 of them original posts, 73 reposts correctly rejected** — plus 11 full article bodies and 143 images. The DOM route yielded 5. LinkedIn's own UI counter claimed "20 Posts".

Before improvising, read `references/dead-ends.md` — six things that look obviously workable and are not, including three separate ways of getting data out of the page that all fail.

**This reads only the user's own account and writes nothing** — no posts, connections, reactions or deletions. If a permission prompt appears, stop and let the user decide.

## Preconditions

`tabs_context_mcp` — if the Claude in Chrome extension is not connected, stop and ask the user to sign in to the extension side panel. The in-app browser pane has no LinkedIn session.

## Procedure

### 1. Find the profile and capture the endpoint

Navigate to `https://www.linkedin.com/in/me/` — it redirects to the user's own profile and the URL gives you the handle.

`read_network_requests` **starts tracking on its first call**, so call it once, *then* navigate to
`https://www.linkedin.com/in/<handle>/recent-activity/all/`, then read it back with
`urlPattern: "graphql"`. Look for:

```
/voyager/api/graphql?includeWebMetadata=true
  &variables=(count:20,start:0,profileUrn:urn:li:fsd_profile:<ID>)
  &queryId=voyagerFeedDashProfileUpdates.<hash>
```

Both the `profileUrn` and the `queryId` hash are needed. **The hash changes between LinkedIn builds — always capture it fresh, never hardcode it.**

### 2. Harvest posts

Inject `scripts/harvest.js` (defines `__LI`, `__imgUrls`, `__toMd`, `__grabFrame`, `__harvestPosts`), then:

```js
await window.__harvestPosts(profileUrn, queryId, 'Their Display Name')
```

It paginates on `metadata.paginationToken` until a page comes back empty. Requests need
`accept: application/vnd.linkedin.normalized+json+2.1` and the `csrf-token` header read from the
`JSESSIONID` cookie.

**Filter for original posts**: `actor.name.text` equals the account holder's display name, there is
no `header` (that is the "X reposted this" context line), and there is no `*resharedUpdate`. All
three are needed — `MEMBER_SHARES` appears on reposts too, and the reshare reference carries a `*`
prefix so the unprefixed key is always `undefined`. Getting this wrong let a third of one account's
feed through as "original". See dead-ends.

The return value reports `activities`, `original`, `rejected` and `rejectedActors` — check the split
rather than trusting the count.

**Dates come free.** A LinkedIn activity id encodes its creation time in the top 41 bits:

```js
new Date(Number(BigInt(activityId) >> 22n)).toISOString()
```

No per-post page visit, and it is exact to the millisecond.

### 3. Harvest article bodies

Articles are Pulse pages and are **not** in the feed API. Enumerate them from
`/in/<handle>/recent-activity/articles/` with `a[href*="/pulse/"]` — that list is not virtualized,
so all of them are in the DOM at once.

Bodies need rendering: `fetch()` on a Pulse URL returns a 1.6MB SPA shell with no article text, no
`ld+json` and no `og:` tags. Load each one in a **same-origin hidden iframe** instead — LinkedIn
allows same-origin framing, so `contentDocument` is readable and the page renders normally. Poll for
`.reader-article-content` to exceed ~200 characters, then convert with `__toMd`.

`__grabFrame` does all of this and takes about 3 seconds per article; **batch 4 at a time** to stay
inside the 45-second CDP timeout.

### 4. Get the data out — the window.name bridge

Three obvious routes all fail (see dead-ends). The one that works:

1. In the LinkedIn page: `window.name = escapeNonAscii(JSON.stringify(rows))`
2. Start `scripts/receiver.py <outdir> <port>` on the host
3. Navigate the tab to `http://127.0.0.1:<port>/#<name>`
4. That page reads `window.name` — which **survives cross-origin navigation** — and POSTs it back
   same-origin, so no CORS and no mixed content

Escape non-ASCII to `\uXXXX` before stashing: it is valid JSON, and it survives every transport
losslessly.

### 5. Images

Post images live in `content` as `{rootUrl, artifacts:[{width, fileIdentifyingUrlPathSegment}]}`.
`__imgUrls` walks the tree and takes the widest artifact per image.

`media.licdn.com` serves them **without authentication**, so a plain `curl` on the host works.
Name each file from a hash of its URL so re-runs are idempotent.

> The widest artifact is often 800KB+. 143 images came to 57MB. If the destination is a git repo,
> take a mid-width artifact instead — `artifacts` is sorted and the 480–800px entries are usually
> a tenth of the size.

## Record shapes

```json
{ "activityId": "7494340417589669889",
  "url": "https://www.linkedin.com/feed/update/urn:li:activity:7494340417589669889/",
  "date": "2026-08-15T10:33:13.665Z",
  "text": "full post text",
  "articleTitle": null, "articleUrl": null,
  "images": ["https://media.licdn.com/dms/image/..."] }
```

```json
{ "url": "https://www.linkedin.com/pulse/...",
  "title": "Where Did the Secondary Colour Go?",
  "dateText": "July 31, 2026",
  "cover": "https://media.licdn.com/...",
  "md": "### Heading\n\nParagraph with [a link](https://...)\n\n- bullet" }
```

Article dates are **display strings** (`"July 31, 2026"`), not ISO — LinkedIn renders no `datetime`
attribute on Pulse pages. Parse them host-side; they carry no time of day.

## Scope

Reads only the signed-in user's own posts and articles. It does not post, react, connect, or delete;
it cannot read other members' private activity; it never touches the paid LinkedIn API.
