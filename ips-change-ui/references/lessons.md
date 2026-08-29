# The two failures, and how the first was recovered

Kept because the evidence is what makes the rules in SKILL.md believable. The
project details are one project's; the shapes are not.

## 1. Transliteration — rated 1/10

> 你没过脑子，原样去翻译老的组件到新组件，原来设计的垃圾，你做出来也垃圾，根本没有领会新
> ui 的设计精神和艺术风格，不敢改 ui，不敢调布局。

The proof was in the work product: 31 route files transformed by regular
expression — `type="body"` → `variant="body"`, `<VStack>` → `<Stack>`,
`gap={2}` → `gap="x6"`. A design migration cannot be performed by `sed`; that
the diff *could* be produced that way is the entire finding.

Four causes, each of which generalises:

- **The input was the old code.** The screenshots were measured pixel by pixel
  while the system was being built, and never reopened during the migration.
  The open file was the old table component, and the question asked of every
  line was "what does this map to" — translating outward instead of building
  back from the design.
- **Old interfaces shaped the new components.** The new table was modelled on
  the old library's API (`columns` / `width` / `renderCell`→`render`) and called
  "generic". It was the shape that let the bulk replacement typecheck. The
  design contained no such table — it had card rows, chips, KPI cards, rails,
  tiles. Status that the design renders as a chip shipped as grey text; a filter
  row the design renders as pills shipped as seven native `<select>`s.
- **The charter was used as a shield.** "老的 UI 功能不变" was read as
  "版式不变". It says 功能. The redline against bending the system to suit an old
  screen had been written by the same agent, then violated by preserving the old
  shapes.
- **Acceptance criteria that could not fail.** Four ACs, none able to go red for
  "this does not look like the new design" — and their green was reported.

The build phase had asked seven design questions; the migration asked two, both
procedural, and showed no layout proposal before coding.

## 2. Overreach, then relapse

The correction overshot. The first prototype reinvented the pages:

> 改动太大了，你这个变成了风格设计，demo 设计，完全脱离我现在每页的定位了。而且我不喜欢
> 那个点点的进度条和 bar，你用 rechart 就行，颜色可以选用当前的鲜亮的。

Blocks were moved, merged and dropped in service of a look, and a private chart
language was invented — dotted meters, hand-drawn bars — in a codebase that
already had a charting library and saturated tints in its registry.

**The relapse**: extending the accepted prototype from three pages to fifteen,
the rest were written from memory of what the pages do. Five sections invented
in place of the five a page actually has; two of four sections lost on another;
a whole "thresholds" section, a fourth breakdown, and a page's closing caveat
dropped. Every page looked finished and looked good. What caught it was
mechanical: extracting every heading and column header from the shipping routes
and comparing item by item — now `scripts/page_blocks.mjs`.

## How the first one was recovered

The nine steps are in SKILL.md. What each looked like in practice:

**The branch was not repaired.** It was complete and handed off, and still the
wrong artifact: every page's shape had been decided by the old call sites. Only
the parts carrying no design decision were kept — dependency removal, build and
plugin config, deleted global CSS imports, route wiring. Everything page-shaped
was discarded.

**The disagreement moved off the product.** A second footer link opened a
`noindex` prototype route: mock data, real distributions, no product page
touched. Behind that door an idea can be shown, rejected and deleted for one
commit. Arguing about layout on pages that ship makes every proposal expensive
and every rejection a rollback.

**Being wrong once was part of it.** The too-bold prototype was rejected in a
sentence — and that rejection carried three constraints never stated before:
keep each page's positioning, use the stack's chart library, use the bright
tints already in the registry. A too-timid pass and a too-bold pass bracket the
range.

**The step that turned it around** was reading every shipping route and writing
the block table before any code:

| Page | Blocks it has (all kept) |
|---|---|
| Home | chip → h1 → lede + two medians → two CTAs → diagnose band → four stat cards |
| Listing | title + lede → full filter row (search + 7 selects + 2 inputs) → six columns → pager |
| Detail | title + action → summary sentence → four metrics → three sections |

That table made the brief statable in one sentence — **块不动、顺序不动、内容
不动，只换视觉语言，图表用现成的图表库** — and made "did anything get dropped?"
mechanically answerable. Accepted first time under that brief, from the same
design system that had been rejected twice. The system was never the problem;
the brief was, and it could not be written until the real pages had been read.
