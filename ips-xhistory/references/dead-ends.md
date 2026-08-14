# Dead ends — verified not to work

Everything here was actually tried against a live logged-in X session on 2026-08-14 and failed.
Recorded so nobody spends the hours again. The working method is in SKILL.md.

## Getting the data

**X's official data archive does not include bookmarks.** Likes are in it, bookmarks are not — a gap
that has existed for years. Requesting an archive to get bookmarks is a multi-day wait for nothing.

**X API Basic works but costs $200/month minimum.** The bookmarks endpoint has never been on the free
tier. It is a real option, just an unnecessary one now.

## Scraping the rendered timeline — abandoned entirely

The DOM approach topped out at **98 items across several dozen tool calls**. The GraphQL replay in
SKILL.md got **5,019 in four**. Do not revive any of this.

- **`window.scrollBy` / `scrollTo` / synthetic `WheelEvent` do not paginate.** They move `scrollY` and
  X loads nothing. Only real CDP input (the `computer` tool's `scroll`) triggers the next page. A loop
  written in page JS looks like it reaches the bottom after a handful of items — that is this, not the
  end of the list.
- **`document.body.style.zoom` to fit more items per screen breaks the virtualized list.** The timeline
  renders blank and collection stalls.
- **A wheel event over a post's image carousel is swallowed by the carousel.** `scrollY` freezes while
  the page looks fine. Vary the scroll coordinate between rounds.
- **The throttle ends the session by resetting scroll position, not by erroring.** `scrollY` jumps
  *backwards* to ~1700–4000 while `docH` stays large, and the count freezes. It appeared after roughly
  250 loaded posts. Nothing recovers it; the list re-renders from the top every time.
- **There is no resume.** No cursor is exposed to the DOM, so each new session re-walks from the newest
  item. Cost to reach a given depth grows with depth already captured while the per-session budget
  stays fixed, so the archive converges a few days back and stops. Reaching a month is not feasible.

## Instrumentation

**Hooking `window.fetch` or `XMLHttpRequest` from an injected script captures nothing.** X grabs its
own `fetch` reference at bundle init, before any injection can run. Use `read_network_requests`
instead — but note it only starts recording on its first call, so call it, *then* trigger a request.

## Getting data out of the page

**A programmatic `<a download>` does not land a file.** Chrome holds it as a temp file
(`~/Downloads/.com.google.Chrome.XXXXXX`) pending a user confirmation that never comes, then reaps it.
It also defeats the point if the user asked not to click anything.

**`pbpaste` on a raw UTF-8 payload corrupts CJK.** A 14,605-character JSON came back with an invalid
byte at offset 621 and every Chinese character destroyed. Escape non-ASCII to `\uXXXX` in the page
first — valid JSON, pure ASCII, lossless.

**`navigator.clipboard.writeText` throws `NotAllowedError: Document is not focused`** unless something
on the page is clicked first.

## Parsing the GraphQL response

**Recursively collecting every `__typename === 'Tweet'` also collects quoted and retweeted posts.**
Those are nested inside entries and can be years old — page one reported "oldest 2022-04-04" this way.
Match on `entryId` starting with `tweet-`.

**Stopping when the oldest post predates the target date terminates immediately and wrongly.** Both
lists are ordered by *save* time; a post saved yesterday may have been written in 2022. Paginate to
`no-cursor` and filter locally.

## URLs

`/i/bookmarks` and `/<handle>/likes` both **redirect to `/i/history`**, a combined page with Bookmarks
and Likes tabs. The old standalone pages are gone.
