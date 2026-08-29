# Dead ends — verified not to work

Everything here was actually tried against a live logged-in LinkedIn session on 2026-08-15 and
failed. Recorded so nobody spends the hours again. The working method is in SKILL.md.

## Reading the feed

**The activity list is virtualized and holds ~5 items.** `/in/<handle>/recent-activity/all/` reports
"Loaded 20 Posts posts" in its own UI while `document.querySelectorAll` finds five. The five recycle;
they are not a window onto a longer list you can walk.

**Page-JS scrolling does not paginate.** A loop calling `window.scrollTo(0, scrollHeight)` sixty
times, waiting 1.4s each round, left the DOM count at 5 and `scrollHeight` unchanged at 4307. It
looks exactly like reaching the end of a short list. It is not — it is this. (Same failure X has;
ips-xhistory records it too.) Only real CDP input — the `computer` tool's `scroll` — moves the app,
and even that did not fire a feed request here.

**`/in/<handle>/recent-activity/posts/` is unreachable.** Both `navigate` and `location.replace`
land back on `/articles/`. Posts are only reachable through `/all/` or the API.

**LinkedIn's SPA swallows URL navigation.** Changing the URL often leaves the previous view mounted,
so a probe reads the wrong page and reports nonsense. Use a hard reload, and assert on
`location.pathname` before trusting anything you read.

## Paginating the API

**`start` is a no-op on this endpoint.** `count:50` with `start:50/100/150/200/250` returned the same
50 updates every time — five extra round trips, zero new items, and it looks like the account only
has 50. Paginate on `metadata.paginationToken` instead; that produced 231.

## Telling originals from reposts

**`MEMBER_SHARES` in `entityUrn` does not mean "the account holder wrote this".** Reposts carry it
too. Filtering on it alone let 73 of 231 activities through as originals — a third of the corpus was
other people's writing.

**`!u.resharedUpdate` passes every repost.** The normalized response marks references with a `*`
prefix, so the field is `*resharedUpdate`; the unprefixed key is `undefined`, which is falsy, so the
check silently succeeds on exactly the items it exists to reject. (`*socialDetail` is the same shape
and is the tell — if a field is a reference, it has a star.)

**Some reposts have no reshare reference at all.** Resharing a company page's post produces an Update
whose `actor.name.text` is the *company*, with `header.text.text` = `"<name> reposted this"` and no
`*resharedUpdate`. Nothing about its own fields says "repost" except the actor and the header.

What actually works — all three, together:

```js
actorName === selfName && !headerText && !u['*resharedUpdate']
```

`header` is the context line LinkedIn renders above a card ("X reposted this"). An original post has
none. Pass the account holder's display name in; it is not derivable from the feed response.

**Report the split.** A filter that silently drops a third of what it collected looks identical to
one that drops nothing.

## Article bodies

**`fetch()` on a `/pulse/` URL returns an empty SPA shell.** 1.6MB of HTML with no article text, no
`<script type="application/ld+json">`, no `og:title`, no `article:published_time`. Parsing it with
`DOMParser` yields nothing. The body only exists after the page runs its JS.

## Getting data out of the page

All three of these were tried before the `window.name` bridge in SKILL.md:

**`navigator.clipboard.writeText` hangs.** On a 245KB payload it never resolves and the CDP
`Runtime.evaluate` call dies at its 45-second timeout. `document.hasFocus()` was `true` and a real
CDP click had been issued first, so this is not the focus problem ips-xhistory hit on X. Chunking to
60 rows did not help — same hang.

**`document.execCommand('copy')` returns `false`.** Even with a real click first, `document.hasFocus()`
true, and a focused, selected `<textarea>` carrying the payload. LinkedIn appears to block it.

**A `no-cors` POST to `http://127.0.0.1` is blocked as mixed content.** `TypeError: Failed to fetch`,
immediately, from the https LinkedIn origin. The "simple request, opaque response" trick works from
http pages, not from https ones.

## Images

Nothing failed here, but two things are worth knowing:

**`media.licdn.com` needs no authentication** — plain `curl` on the host retrieves them, so images do
not have to come out through the page.

**The widest artifact is big.** Taking `artifacts` sorted by width descending gave an average of
400KB per image; 143 images came to 57MB. Fine for a scratch archive, heavy for a git repo.
