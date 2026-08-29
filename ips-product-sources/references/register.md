# The register

Every source measured so far, admitted or not. Percentages are the share of a
**30-page sample** that yielded that field. All measured **2026-08-26**.

The live configuration this mirrors is `src/lib/df-sources/registry.ts` in the
TroveStep repository. **That file is the authority**; this one is the reasoning
and the rejections, which do not belong in shipped code.

## Admitted

| Source | Entry pages | Name | Intro | **URL** | Categories | How the URL is read | Notes |
|---|---:|---:|---:|---:|---|---|---|
| tinylaunch.com | 14,943 | 100% | 100% | **100%** | none | `"url"` field | Launch board. Entries skew to indie micro-products. |
| uneed.best | 9,434 | 100% | 100% | **100%** | nav only | `"url"` field | Its `/categories/` links are the same five on every page. |
| aiseekify.com | 8,738 | 100% | 100% | 97% | `/category/` | `"url"` field | **English sitemap only** — ten language sitemaps exist. |
| dang.ai | 6,712 | 100% | 100% | 96% | `/category/` | `"url"` field | URLs carry `?ref=dangai`. Left on in the landing layer. |
| opentools.ai | 6,424 | 100% | 100% | 98% | none | `"url"` field | No taxonomy. 242 entries → openai.com, 175 → github.com. |
| aimostall.com | 4,714 | 100% | 100% | **100%** | `/category/` | `"url"` field | |
| aitoolslist.tools | 3,173 | 100% | 100% | 97% | `/category/` | `"url"` field | |
| baira.ai | 2,418 | 100% | 100% | 97% | `/category/` | `"url"` field | |
| futurepedia.io | 1,508 | 100% | 100% | **100%** | `/ai-tools/` | **frequency heuristic** | 4 pages in 5 have no `SoftwareApplication`; name comes from the breadcrumb. |

**Total ≈ 58,000 entry pages.** Measured overlap between two of them was
**20.1% by domain** — sources are far less redundant than they look.

## Rejected, and why

Ordered by size, because size is what tempts.

| Candidate | Pages | Rejected because |
|---|---:|---|
| aiseekify (other 9 languages) | 78,642 | The same catalogue restated per language. Duplicates, not entries. |
| aidb.cc | 23,823 | No `ld+json`, no `og:description`. A traffic-analytics clone, not a catalogue. |
| huggingface.co | 33,244 | Models, datasets, spaces, papers — not products with a business. Wrong shape. |
| aitop365.com | 11,279 | No product-URL field; Chinese copy. Would need the frequency heuristic. |
| shrug.ai | 11,200 | No `ld+json`, no `og:description`. |
| aibase.com | ~11,000 | **No enumeration path of any kind** — see trap 3. |
| inouts.com | 8,282 | Name on only **73%** of sampled pages. |
| best-ai.org | 7,450 | Product URL on **57%**. |
| mifar.net | 7,330 | Product URL on **0%**. |
| exploreai.tools | 6,126 | Product URL on **30%** — one entry page looked perfect. |
| aixploria.com | 4,911 | French; routes outbound links through `/out/`, which its own robots disallows; then began answering 403. |
| futuretools.io | 4,215 | Product URL on **3%** — one entry page looked perfect. |
| rankmyai.com | 440 | Ranking pages not in the sitemap; site decaying. |
| G2, Capterra, Crunchbase, AlternativeTo, SaaSHub, SourceForge, Product Hunt, Toolify, TAAFT, topai.tools, IndieHackers, StackShare | — | Empty sitemap, 403, or bot challenge. Their catalogue is their moat. |

## The two that nearly got in

Worth naming separately, because they are the argument for the whole bar.

**futuretools.io** and **exploreai.tools** were both checked by opening one
entry page. Both showed a name, a blurb, and a working outbound link. Both were
about to be written into the configuration. The 30-page sample put them at
**3%** and **30%** — on most of their pages the product's address is simply not
published.

Neither would have failed loudly. Both would have landed thousands of rows with
an empty URL column, and the hole would have surfaced weeks later in whatever
tried to join on domain.

## Where these candidates came from

Roughly two-thirds came from the corpus's **own referring-domain table** —
13,205 domains that link to products already held, ranked by how many they link
to. A site that links to fifty products in the corpus is a directory of those
products, by construction.

Web search produced almost nothing usable: it returns articles *about* AI
directories, and the directories those articles name are the closed ones.
