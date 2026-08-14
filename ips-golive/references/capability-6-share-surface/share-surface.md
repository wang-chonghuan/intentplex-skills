# Capability 6: Share Surface

Make a pasted link render as a card instead of as bare text, and give the site a
recognisable tab icon. This is the cheapest distribution work there is: every
share into Slack, X, WeChat, LinkedIn or iMessage either shows a title, a
description and an image, or shows a naked URL.

This capability **changes shipped HTML**, so it goes through the repo's
development loop — see Handoff.

## When To Use

- cap1 reports `og:*`, `twitter:card`, `og:image` or favicon as FAIL
- before any launch or promotion push
- after a repositioning — the OG image and description are copy, and stale copy
  ships to every future share

## What A Complete Share Surface Is

**Per-page, varying:**

| Tag | Notes |
|---|---|
| `<title>` | unique per page |
| `<meta name="description">` | unique per page |
| `<link rel="canonical">` | absolute, canonical host |
| `og:title`, `og:description` | mirror the page's own title/description |
| `og:url` | absolute, matches canonical |

**Site-wide, constant:**

| Tag | Notes |
|---|---|
| `og:type` | `website` |
| `og:site_name` | the product name |
| `og:image` + `og:image:width`/`height` | **1200×630**, absolute URL |
| `twitter:card` | `summary_large_image` |
| `twitter:image` | same image |
| `rel="icon"` / `rel="apple-touch-icon"` | favicon + 180×180 touch icon |

Split them exactly this way in code: constants declared once in the root
document, variable tags produced per route. Emitting the variable ones in both
places is the usual cause of duplicate `og:title` tags, and scrapers pick
unpredictably between duplicates.

## Rules That Actually Matter

- **Absolute URLs.** `og:image` and `og:url` must be `https://…`. A relative
  path silently yields no preview on most platforms — this is the single most
  common failure.
- **1200×630.** Under ~600px wide, platforms fall back to a small square card or
  drop the image.
- **The image must be publicly reachable, unauthenticated, and not behind a
  redirect chain.** Scrapers are less patient than browsers.
- **No duplicate tags.** If the framework merges head fragments, verify the
  rendered HTML has exactly one of each.
- **Keep the favicon stable.** Users find a tab by its icon; changing it reads
  as a different site.

## Producing The OG Image Without New Dependencies

An OG image is just a 1200×630 screenshot of a static HTML page. If the repo
already has a browser automation tool (Playwright is common, often already
present for tests), render it:

1. Write a self-contained HTML file at 1200×630 with the product name, the
   headline and a one-line subtitle.
2. Screenshot it at `viewport 1200×630, deviceScaleFactor 1`.
3. Commit the PNG to the app's public assets.

Do not add an image library for this. Do not generate the image per request at
runtime unless the content genuinely varies per page — a static image is faster,
cacheable, and cannot break in production.

Design constraints that survive contact with reality: very large type (it is
viewed as a thumbnail), high contrast, **no small text**, and keep the safe area
clear of the bottom-right corner where some platforms overlay a domain label.
Check the layout after any copy change — long headlines overlap decorations, and
that only shows up in the rendered PNG.

## Verify

Rendered HTML first:

```bash
python3 <skill-dir>/scripts/readiness_audit.py https://example.com | sed -n '/share/,/crawl/p'
```

The audit checks each tag, fetches `og:image` and the favicon, and fails when
either is unreachable.

Then confirm there are no duplicates and the image is the right size:

```bash
curl -s https://example.com/ | grep -c 'og:title'          # expect 1
curl -sI https://example.com/og.png | grep -i content-type  # expect image/png
```

Finally, if the user cares about a specific platform, have them paste the URL
into a private message there. Platforms cache aggressively: **a preview seen
before the fix may persist**. Both X and Facebook offer a card/debug tool that
forces a re-scrape; use that rather than concluding the fix failed.

## Traps

- **Cached previews.** After fixing tags, the old card can persist for days on
  some platforms. Force a re-scrape before debugging further.
- **Relative `og:image`.** Renders fine in the browser, invisible to scrapers.
- **A framework's head merge** producing two `og:title` tags — one from the root,
  one from the route.
- **An OG image behind a CDN rule that requires a session** — unauthenticated
  scrapers get a redirect or a 403.

## Handoff

These tags live in the application's root document and route heads. In an
n-prodfarm repo file a ticket (type **enabler**), develop and verify it through
the normal loop, and close it there.
