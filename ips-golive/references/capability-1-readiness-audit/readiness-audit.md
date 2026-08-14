# Capability 1: Readiness Audit

Read-only. Look at a live site and report exactly what still stands between it
and being a real public product. Changes nothing, so it is always safe to run
first — and it should be run first, because it decides which other capabilities
this site needs.

## When To Use

- "这个站上线还差什么" / "what's missing before launch"
- before running any other ips-golive capability, to scope the work
- after running one, to confirm the gap actually closed in production
- periodically on a live site — things rot (a certificate lapses, a redirect
  regresses, a deploy drops a file)

## Command

```bash
python3 <skill-dir>/scripts/readiness_audit.py https://example.com
python3 <skill-dir>/scripts/readiness_audit.py https://example.com --json
```

Pass the site's **canonical** host — the one you intend people and search
engines to use. The audit judges the other host (`www` vs apex) relative to it.

Exit code is 0 when nothing FAILs, 1 otherwise, so it works as a gate.

## What It Checks, And Why Each Matters

| Section | Checks | Why it belongs in "product-ready" |
|---|---|---|
| reachability | responds; proxied vs direct-to-origin | the proxied/DNS-only fact decides cap3's install mode and constrains cap2 |
| tls | certificate validity, issuer, days left | an expiring managed cert is silent until it is fatal |
| addressing | `http`→`https`; the other host → canonical | two hosts serving 200 split ranking signals and confuse analytics |
| identity | title, meta description, canonical | how the page names itself to search engines |
| share | OG title/description/image/url/type, twitter:card, og:image reachable, favicon | whether a pasted link renders as a card or as bare text |
| crawl | robots.txt (+ Sitemap line, not blocking all), sitemap.xml (valid XML, url count), llms.txt | whether crawlers and AI answer engines can enumerate the site |
| measurement | analytics beacon in the served HTML; Google/Bing verification TXT in DNS | **the one that cannot be backfilled** |

## Reading The Result

- **FAIL** — a real gap. The site is not product-ready.
- **WARN** — a decision, not a defect. A `302` where a `301` is better; no
  `llms.txt`; Search Console not verified yet. Judge in context and say so.
- **SKIP** — the check could not run (e.g. no `dig`). Never report a SKIP as a
  pass.

Two results deserve a sentence of interpretation rather than a bare status:

1. **`edge: direct to origin (DNS only)`** is not a defect. It is often
   mandatory — an origin-issued managed certificate (Azure Container Apps,
   many PaaS) requires the served host to stay unproxied. Its consequence is
   that Cloudflare's own traffic dashboard will be permanently empty for this
   host, which is exactly why cap3 uses a manual beacon. Explain that instead of
   proposing the orange cloud.
2. **Search Console `WARN`** understates the cost. History starts at
   verification; the weeks before it are gone for good. Treat it as urgent-but-
   cheap rather than optional.

## Limits Of The Audit

It checks **one page** — the URL you pass. Per-page facts (title, description,
canonical) are verified only for that page; a site whose home page is perfect
and whose detail pages share one title still passes. When the site has templated
sub-pages, run it against a representative one too.

It cannot see: whether analytics is actually *receiving* data (that is cap3's
RUM query), whether the sitemap's URLs are correct or indexed (cap4), or
anything about content quality.

It probes exactly one sitemap path, `/sitemap.xml`. Several common generators
publish under a different name — `@astrojs/sitemap` and Gatsby's plugin both
emit `sitemap-index.xml` — so a correctly configured site can produce a
`sitemap.xml FAIL` while its sitemap is fine and `robots.txt` points at it
correctly. Before treating that FAIL as a gap, read the `Sitemap:` line the
audit already found in `robots.txt` and fetch that URL. If it is valid, the
remaining question is a cap5 decision (whether to also publish at
`/sitemap.xml`, the name crawlers probe first), not an audit failure.

It is not a security audit and not a performance audit.

## After The Audit

Map each FAIL to the capability that closes it, then report to the user in that
order — cheapest and most time-sensitive first:

| Finding | Capability |
|---|---|
| no custom domain / cert / redirect problems | cap2 |
| no analytics beacon | cap3 |
| Search Console or Bing unverified | cap4 |
| robots.txt / sitemap.xml missing | cap5 |
| OG tags, og:image, favicon missing | cap6 |

Do not fix anything inside cap1 — it is read-only by contract, and a capability
that silently changes what it measures cannot be trusted as a gate.
