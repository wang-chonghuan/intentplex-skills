---
name: ips-product-sources
description: Load when the work is finding, judging, re-checking or replacing the directories a product corpus is crawled from — "找数据源", "这些源还能用吗", "加几个源", "源的质量怎么样", "ips-product-sources", or when a crawl's yield drops and nobody knows which source broke. Holds the measured register of known sources, the admission bar, and the traps that cost real time. Do not load to write a crawler for a source already admitted, or for one-off scraping unrelated to corpus building.
---

# ips-product-sources

Finding a data source is not a search problem. Every candidate looks fine from
the outside, and the ones that fail do it **quietly** — a directory with 6,000
entries that never publishes the product's own address still returns 6,000
happy-looking rows.

So this skill is built around one rule:

> **A source is admitted by a measured sample, never by looking at it.**

Everything below exists to make that rule cheap to follow.

## The bar

Sample **30 entry pages, spread across the sitemap** (not the first 30 — the
top of a sitemap is often nav, archives, or the oldest entries). Measure the
share of pages that yield each field. Admit only when:

| Field | Threshold | Why this one |
|---|---|---|
| product name | ≥ 97% | Cheap to get; a source failing it is broken, not stingy |
| product intro | ≥ 97% | Same |
| **product URL** | **≥ 97%** | **This is the field that decides it** |

**The URL is where sources die.** Every candidate rejected so far scored 100%
on name and intro. A directory entry with no address is a row nobody can join
to anything — not to traffic, not to keywords, not to the product itself.

Record the numbers **and the date** next to the configuration. A quality number
with no date is a number nobody can act on.

## The seven traps

Each of these cost real time. They are ordered by how much.

**1. One page is not a sample.** Two sources were nearly admitted on the
strength of one clean-looking entry page. Measured over 30: futuretools.io
published the product URL on **3%** of pages, exploreai.tools on **30%**. Both
looked perfect on the page that was checked. *Never generalise from one page.*

**2. "Big and open" is usually neither.** Every large review site — G2,
Capterra, Crunchbase, AlternativeTo, SaaSHub, Product Hunt, Toolify — answers
with an empty sitemap, a 403, or a bot challenge. That is not an accident:
their catalogue is their moat. What stays open is the long tail. Budget for
that before promising anyone a big-name source.

**3. Permission is not enumerability.** `robots.txt` saying `Allow: /` means
nothing about whether you can *list* what a site holds. AIbase allows its tool
pages and is still unreachable: no sitemap, `?page=2` returns page one, a real
browser scrolling forty screens sees the same 49 tools, no category index. Test
enumeration separately from permission, and test it **before** writing a
collector.

**4. Category links are mostly nav.** A directory links to its top-level
categories from every page, and in the markup those look exactly like the
entry's own categories. Test it in one command: pull the category slugs from
two *unrelated* products. If the lists match, they are furniture. The fix that
survives a redesign is to learn the furniture from the crawl itself — sample N
pages, treat a slug appearing on ≥90% of them as chrome, subtract it — rather
than hard-coding a list that goes stale silently.

**5. One catalogue, ten languages.** aiseekify publishes its whole catalogue
once per language across ten sitemaps. Reading two would land every product
twice as two products. **Check `robots.txt` for sibling sitemaps before picking
one**, and take exactly one locale.

**6. A 403 is the site's answer.** Sources rate-limit even when `robots.txt`
asks for nothing. Being blocked means going slower or going away — never
arriving from a different address. Set per-source concurrency and delay, and
treat "no `Crawl-delay` published" as "unknown", not as "unlimited". Probe
politely from the first request: the block usually arrives during *research*,
when nobody is being careful yet, and then the source is unusable for hours.

**7. Sources overlap far less than they look.** The instinct is that
directories copy each other and a second source is redundant. Measured on two
of them: **20.1% overlap by domain** — 10,181 rows gave 8,708 unique domains.
Adding sources is worth it. *Measure the overlap rather than assuming it, in
either direction.*

## Where candidates come from

In rough order of yield:

1. **The corpus's own backlink table.** Sites that link to products already in
   the corpus are, by construction, directories of those products — and they
   come pre-ranked by how many they link to. This beat every list found by
   searching. If the product records referring domains, start there.
2. **Sitemaps of admitted sources.** Directories link to each other.
3. **Web search.** Weakest. Returns listicles about directories rather than
   directories, and the named ones are the closed ones.

## Judging a candidate, in order

Stop at the first failure — each step is cheaper than the one after it.

1. `robots.txt` — reachable, no bot challenge, entry paths not disallowed.
2. **Enumerable** — a sitemap listing entry pages, and it is the *entry* pages,
   not categories or tags. Check the path distribution; a headline count of
   24,621 was 23,823 products and 798 categories in one case, and *only*
   category pages in another.
3. **Structured** — `ld+json` or `og:` tags present. A source emitting neither
   forces the frequency heuristic for the URL, and that guess lands rows that
   look complete and name the wrong company.
4. **Sample 30** — the bar above.
5. **Overlap** — how many of its domains are new against what is already held.

## What to record

Both halves, together, or the record is useless: **how to read it** and **what
it measured, and when**. The shape that worked:

```
name, own domain, sitemap URL, entry-path filter,
url strategy, category strategy, concurrency, delay,
measured { date, pages, name %, intro % , url % },
note
```

Keep the **rejected** candidates in the same file, with their numbers and the
reason. Without it, the next person spends an afternoon rediscovering that
mifar.net publishes no product URLs. A rejection is a measurement, and it is
worth as much as an admission.

See `references/register.md` for the current register — the sources admitted,
the ones turned down, and what each measured.

## Re-checking an existing register

Directories restyle, change frameworks, add bot protection, and go quiet.
Re-run the same 30-page sample against every admitted source and compare with
its recorded numbers.

- **Any field dropped below its threshold** → the collector is now producing
  rows with a hole in them. Fix or retire it; do not leave it running.
- **Entry count fell sharply** → the sitemap path or filter changed.
- **403 / challenge appeared** → the source added protection. Slow down or
  retire; do not route around it.
- **Nothing changed** → update the date anyway. A confirmed date is the point.

A drifted source is worse than a missing one: the crawl still succeeds, the row
count still looks right, and the holes are only visible to whoever reads the
data months later.
