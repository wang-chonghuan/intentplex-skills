# Research prompt

The prompt below is the artefact this skill exists to carry. It was arrived at
by running an earlier version, reading the output, and finding it had failed —
twice. Both failures are encoded in it now, as the two tests. Send it to a
subagent that has web search and file read.

Substitute the `{{...}}` placeholders. Everything else goes verbatim: the
illustration, the two tests and the empty-string rule are the parts that do the
work, and paraphrasing them loosens exactly the constraints that make the output
usable.

## Placeholders

| placeholder | what to put in it | example |
|---|---|---|
| `{{SITE}}` | the site the card is for. Names the audience the researcher is writing to | `whichtouse.com` |
| `{{TODAY}}` | today's date, ISO | `2026-08-02` |
| `{{YEAR}}` | the year, so the search is anchored to now rather than to training data | `2026` |
| `{{CATEGORY}}` | the category name as a reader would say it | `Coding` |
| `{{CATEGORY_BLURB}}` | one clause naming what is in scope | `AI coding tools and agents (IDE assistants, terminal agents, autonomous cloud agents, agent skills)` |
| `{{PRODUCT_COUNT}}` | how many products the reader is choosing between | `roughly fifteen products` |
| `{{PRIOR_ART_STEP}}` | step 1 — see below. Use variant A when there is an existing corpus of entries, variant B when there is not |
| `{{PRACTITIONERS}}` | who actually buys in this category. Naming the role changes which sources get searched | `experienced practitioners` · `founders, controllers and accountants` |
| `{{DOMAIN_HINT}}` | one sentence on what is unusually decisive here, or empty. Use it when a category has a known load-bearing axis | `Pricing units and rights/licensing are unusually decisive in this category; find out how they work as a class, not per vendor.` |

### `{{PRIOR_ART_STEP}}` variant A — a corpus exists

> 1. Read `<path to the category's entries>` — every ranked entry with `pros`, `cons`, `pricing`, `rankBasis`, and a category-level `notes`. Read the `cons` across all entries especially: a complaint that recurs across many products is a property of the category, which is exactly what you are looking for. A complaint about one product is not.

### `{{PRIOR_ART_STEP}}` variant B — no corpus

> 1. Build your own sample first: find ten to fifteen products that a buyer in this category would actually shortlist, and read what their users complain about. A complaint that recurs across many products is a property of the category, which is exactly what you are looking for. A complaint about one product is not.

---

## The prompt

```text
You are writing a three-line "Before you pick" callout for one category of {{SITE}}, a hand-checked comparison site. Today is {{TODAY}}.

CATEGORY: **{{CATEGORY}}** — {{CATEGORY_BLURB}}.

## Who reads this

Someone is about to choose one of {{PRODUCT_COUNT}} in this category. They will scroll past your three lines into the ranked lists. They will not remember any product name you write. What they need from you is **the lens** — how to tell these products apart, where this class of product commonly fails its buyers, and which way the whole class is moving.

## The three lines

  weigh   — the consideration that actually decides the choice in this category, and that a feature comparison would not reveal.
  avoid   — the pitfall specific to this class of product. What buyers here regret.
  moving  — how the capabilities of these products are changing right now. Direction of the category, not a corporate event.

## Two tests, and every line must pass both

**Test 1 — the news test.** If the line names a product, a vendor, a version number or a date, it is a news bulletin and it fails. Write about how this *class* of product works, not about what one company did.

**Test 2 — the substitution test.** If the line would read perfectly well on a different category's page, it is generic filler and it fails. It must be rooted in the specific mechanics of this category.

The register you are aiming for sits between them. An illustration from an unrelated category — email clients:

- ✗ news: "Superhuman raised its price to $30/month in June."
- ✗ generic: "Think about your team size and your budget."
- ✓ right: "Search quality over years of archived mail decides this; every one of them demos well on an empty inbox."

That third line names no product, could not be moved to another category, and hands the reader a test they can run themselves.

## Method

{{PRIOR_ART_STEP}}
2. Search the web for what {{PRACTITIONERS}} say about choosing in this category in {{YEAR}} — what decides it, what they regret, what is becoming table stakes. {{DOMAIN_HINT}} Ignore vendor marketing.
3. Generalise. A specific finding is your evidence; the line you write is the pattern behind it.

## Constraints

- 25 words maximum per line. Shorter is better.
- Plain declarative English. No marketing adjectives. No "it depends", no "consider your needs".
- Every line must be defensible from a source, even though the line itself is a generalisation. Keep the sources.
- If you cannot support one of the three from evidence, return an empty string for it. An empty slot is honest; filler is not.

## Return

ONLY this JSON, nothing else:
{"category":"{{CATEGORY}}","weigh":"...","avoid":"...","moving":"...","sources":["url",...]}
```

## Why each part is load-bearing

**The two tests exist because two earlier versions failed in opposite
directions.** The first asked only for a good short conclusion and produced a
news bulletin — "Udio disabled all downloads after its UMG settlement",
"QuickBooks Online raised prices August 1". True, sourced, and useless to
someone choosing, because it is about one vendor on one date. Adding only "be
more general" then produced the opposite failure: lines that would sit equally
well on any page. The tests are a pair; neither alone holds the register.

**The email-client illustration is deliberately from an unrelated category.**
An example drawn from the category being researched hands the subagent its
answer and it will echo the shape back. The example teaches register, not
content, so it must come from somewhere the researcher is not working.

**The empty-string rule is not politeness.** Without it a subagent that cannot
find evidence for `moving` will write something anyway, and that sentence will
be the one nobody checks.

**`{{PRACTITIONERS}}` changes the search, not the tone.** "Founders, controllers
and accountants" pulls up switching-cost and close-process material that
"practitioners" does not.
