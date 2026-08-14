# Capability 5: Crawl Surface

Publish the three files that let machines enumerate the site: `robots.txt`,
`sitemap.xml`, and `llms.txt`. Without them a crawler must discover pages by
following links, and an AI answer engine has nothing authoritative to read.

This capability **changes shipped files**, so it goes through the repo's
development loop — see Handoff.

## When To Use

- cap1 reports `robots.txt` or `sitemap.xml` as FAIL
- before cap4 (Search Console wants a sitemap to submit)
- after adding a new family of pages that should be discoverable

## Preconditions

- You can enumerate the site's public URLs from the repo — a route list, a
  content index, a category list. If URLs are only knowable at runtime from a
  database, generate the sitemap at build time from the same source, never by
  hand.
- The site is on its canonical custom domain (cap2). A sitemap full of
  platform-hostname URLs is worse than none.

## What To Publish

### robots.txt

Minimal and permissive is correct for a site that wants to be found:

```
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

Rules:

- The `Sitemap:` line must be an **absolute URL** on the canonical host.
- Never ship `Disallow: /` to production. It is the single most damaging line in
  this capability — it removes the site from every search engine, silently, and
  the audit checks for it explicitly.
- Only disallow paths that are genuinely useless to crawlers (internal previews,
  duplicated print views). Do not disallow an API that AI engines could cite.

### sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc><lastmod>2026-07-25</lastmod></url>
  <url><loc>https://example.com/c/coding</loc><lastmod>2026-07-25</lastmod></url>
</urlset>
</urlset>
```

Rules:

- **Generate it, never hand-maintain it.** A hand-written sitemap goes stale the
  first time a page is added, and a stale sitemap is a crawl-budget leak. Derive
  it from the same source the router uses.
- Absolute URLs, canonical host, and **exactly the form the canonical tag
  points at** — if canonical is `https://example.com/x`, the sitemap must not
  say `https://www.example.com/x/`.
- Only include URLs that return 200 and are indexable. Never list a redirect, a
  404, or a page carrying `noindex`.
- `lastmod` should be real. A file that claims every page changed today teaches
  crawlers to ignore the field.
- Ignore `changefreq`/`priority` — search engines effectively do.

### llms.txt (the AI-citation base)

A short Markdown file at `/llms.txt` describing what the site is and where its
machine-readable data lives. This is the GEO groundwork: it costs one file and
makes the site legible to answer engines.

```markdown
# Site Name

> One sentence on what this site is and what makes its data trustworthy.

## Machine-readable
- Index: /api/index.json
- Per item: /api/<slug>.json

## Sections
- Section name: /section-path
```

Keep it honest and current. A `llms.txt` that describes an aspiration rather
than the site as it is will be quoted back at you — this file is read by systems
that cite. If the site's data is provisional, say so here.

## Where To Put The Generator

If the framework's server-route API is unambiguous, a route that renders these
from the live content source is the cleanest answer. **If it is not — do not
guess.** Generate the files into the app's static/public directory as part of
the build, and wire that step into the build command itself so it re-runs on
every deploy and cannot be forgotten. A static file served by the existing
static handler has no framework-version risk, and "regenerated on every build"
already delivers the freshness guarantee that matters.

Whichever way, the origin (`https://example.com`) must be read from wherever the
app already defines it. A second copy of the canonical origin inside the
generator is exactly the kind of duplicate that drifts after a domain change.

## Verify

From production, not from the repo:

```bash
curl -s https://example.com/robots.txt
python3 <skill-dir>/scripts/readiness_audit.py https://example.com | sed -n '/crawl/,/measurement/p'
```

The audit parses the sitemap as XML and counts `<loc>` entries, so a malformed
file fails there rather than silently in a search console weeks later.

Then two checks the audit cannot make, both worth doing every time:

**1. Every URL in the sitemap is really fetchable, and is not a redirect.** A
sitemap of redirects burns crawl budget and is the usual symptom of a
trailing-slash or host mismatch. Check them all — the list is small and the
failure is silent:

```python
import re, urllib.request
xml = urllib.request.urlopen("https://example.com/sitemap.xml").read().decode()
bad = []
for u in re.findall(r"<loc>([^<]+)</loc>", xml):
    with urllib.request.urlopen(u, timeout=20) as r:
        if r.status != 200 or r.geturl() != u:      # geturl() differs => redirected
            bad.append((u, r.status, r.geturl()))
print(len(bad), "bad urls", bad[:5])
```

**2. The sitemap is genuinely generated, not hand-written.** Perturb the source
(add one entry), regenerate, confirm the count moved, then restore and confirm
it moved back. This is the only check that distinguishes a real generator from a
list someone happened to write out once — and it catches a generator that reads
a stale copy of the source. Restore the source before doing anything else.

## Traps

- **Serving these from the wrong place.** In a framework with a catch-all route,
  `/robots.txt` can be swallowed by the app router and return HTML with a 200
  status. Check the actual bytes, not just the status code.
- **A sitemap that lists the deploy hostname** while canonical points at the
  custom domain. Every URL is then a redirect, and the crawl budget is wasted.
- **Trailing-slash inconsistency** between sitemap, canonical, and what the
  server actually serves. Pick one form and make all three agree.
- **Forgetting to regenerate.** If the sitemap is generated at build time, a
  content-only change that does not trigger a build leaves it stale. Prefer
  generating from the live content source at request time or on every deploy.

## Handoff

These are files inside the application. In an n-prodfarm repo file a ticket
(type **enabler** — it adds a user-invisible capability to shipped code), let
the normal loop develop and verify it, and close it there. Do not commit the
files directly from this skill.
