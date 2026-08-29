---
name: ips-change-ui
description: Load when a product's interface is being built from a designer's screenshots and then applied to the whole app — turning screenshots into a token registry and component library with a demo, restyling every existing page in that language, prototyping the new look before committing to it, or judging whether a finished migration actually adopted the design. Triggers include "ips-change-ui", "这几张截图先实现出来", "把整个 app 换成这套 UI", "换一套设计系统", "按设计稿重做界面", "迁移到新的组件库", "restyle the product", "migrate the UI to the new design system". Do not load to set up styling architecture (n-stylex), to tweak one component, or to run functional regression (n-autoqa).
---

# ips-change-ui

Changing a product's UI is a **design** job wearing an engineering costume. It
fails in two opposite directions, and each one is the other's virtue, so neither
is catchable by self-inspection:

```
transliteration            ← the target →            redesign
逐个把旧组件译成新组件                              重新发明每一页
"faithful", regex-able                              "bold", demo-flavoured
新皮肤下还是旧设计                                  每页的定位丢了
                        块不动 · 材料换
```

The default job is the middle one: **每页的定位、块、顺序、内容不动，只把视觉
语言换掉。** The only reliable correction is external — settle the job before
coding (cap2), put the mapping and the prototype in front of a human early
(cap3, cap4).

```
几张截图 → cap1 建系统+demo → cap2 立场 → cap3 对照表 → cap4 原型 → cap5 验收 → cap6 迁移
```

Start at cap2 if the system already exists and is approved. Start at
**Recovery** if a migration has already been done and rejected.

## Capabilities

Stable user-facing numbers. Do not renumber.

1. **cap1 从截图建系统.** Look at every screenshot before proposing anything,
   ask the design questions, recover the screenshots' scale factor, measure
   values into **one token registry**, build atoms → molecules → organisms →
   templates, prove it with an interactive demo behind a footer link. Two
   outputs matter downstream as much as the code: the registry, and a written
   **design-language inventory** — each component paired with the kind of
   content it carries. Read `references/build-from-screenshots.md`.
2. **cap2 立场校准.** Name the job in writing, in the ticket's acceptance
   criteria: **restyle** (default — blocks, order, content and copy invariant),
   **redesign** (blocks may move or go, only when commissioned, page by page
   against approved layouts), or **new surface**. Ambiguous wording gets one
   question now instead of a rejected pass later.
3. **cap3 页面清单与对照表.** Per page, extract the blocks from the **running
   old page or its route file** — heading order, column sets, filter controls,
   empty states, footnotes. Map each block to a component from cap1's
   inventory. A block with no entry is a finding to raise, never a licence to
   keep the old shape. Show one or two mapped pages before writing the rest.
4. **cap4 原型先行.** Build **all** pages on a `noindex` route behind a small
   footer link, touching no product page. Mock data is fine; mock
   *distributions* are not — the layout must survive the extreme value, the
   forty-character string and the null. Disagreement here costs one commit.
5. **cap5 会失败的验收.** Three checks, each able to go red: **block parity**
   (`scripts/page_blocks.mjs` on old and new, diffed), **overflow**
   (`scripts/overflow_probe.mjs`, every page × every width down to the agreed
   floor), and **your own eyes on your own captures**, desktop and phone, every
   page. A diff line is either a **drop** (fix it) or a **deliberate
   deviation** (record it and say so).
6. **cap6 迁移.** Only after the prototype is approved. Page by page, running
   cap5 after each. Deleting the old library is the last step and its own
   commit.

## Recovery: rejected as transliteration

The likely first outcome, and the response has a shape. Evidence in
`references/lessons.md`.

1. **Stop; do not patch the rejected work.** Its shape was decided by the old
   call sites, so every local fix negotiates with the wrong parent.
2. **Diagnose from your artifact, not your intent.** Ask of the diff: *could
   `sed` have produced this?* Name causes by quoting your own output.
3. **Move the disagreement off the product** — a second, disposable surface
   where an idea can be shown, rejected and deleted for one commit.
4. **Budget two swings, take the first early.** The correction to a too-timid
   pass overshoots. That is how the range gets bracketed, not waste.
5. **Mine the rejection for literal constraints** and quote them back as the
   brief before writing anything.
6. **Go read the real pages** and write the block table — page, and every block
   it has. Show the table before the code; agreement is cheapest there.
7. **State the brief in one sentence and get it acknowledged.** The same design
   system that was rejected twice passes first time under a correct brief. The
   system is rarely the problem; the brief is.
8. **Rebuild from the design plus the table**, never by editing the rejected
   code. Then extend page by page with the parity check running.
9. **Salvage mechanically, not visually.** Keep what carries no design decision
   — dependency removal, build config, deleted global CSS, route wiring — and
   discard every translated page. Rewrite the ACs so they can fail.

The urge to rescue the finished work is the same urge that produced the
failure: it values work already done over the thing being asked for.

## Scripts

Run from the project root (they resolve Playwright from the working directory).

- `page_blocks.mjs <url> [--click "Nav name"] [--json]` — a page's block list:
  heading order, column headers, controls. Old vs new; the diff is the parity
  check.
- `overflow_probe.mjs --url <url> [--paths a,b] [--clicks A,B] [--widths …]` —
  horizontal-overflow scan, ignoring deliberate scrollers, naming the innermost
  offender, exit 1 on any overflow. **Prove once per project that it can go
  red**; a probe that has never failed is not evidence.

## Working Rules

- **Look at every screenshot before proposing anything**, and ask the design
  questions while they are still free.
- **Measure, do not eyeball.** Values nothing can check are values nobody can
  maintain.
- **Design in, not old code out.** Each page starts from what it answers and
  which part of the design language carries that. The old code tells you *what
  blocks exist*, never *what they should look like*.
- **块不动，材料换.** Copy is quoted from the route, never paraphrased from
  memory — "I know what this page says" is exactly the confidence that drops a
  section.
- **New components take their shape from the design, not the old call sites.**
  An API that exists so a bulk replacement will typecheck is the tell-tale.
- **Every content shape needs a precedent in the system before it is needed in
  anger** — a dense table, a long filter row, a prose page, an empty state. If
  the demo never rendered one, the migration will keep the old one.
- **Use the charting library the stack already has**, with the registry's own
  tints. Never hand-draw a meter, a dot matrix or a bar.
- **A check must be able to fail.** If you cannot say what turns it red, it is
  decoration; never report its green.
- **Report what was not verified** — pages behind a sign-in wall, a component
  that will not mount locally — instead of letting passing checks imply
  coverage.

## Redlines

- No bulk regex/sed replacement of old components with new ones.
- Never modify or import the frozen `*-REF-ONLY` copy of the system.
- Never bend the system to suit an old screen: no hardcoded colour or pixel, no
  preserved old control shape.
- In a restyle, never move, merge or delete a block, and never rewrite page
  copy. If a block should go, that is a question for the user, asked first.
- Never read "功能不变" as "版式不变".

## Boundaries

Covers the whole arc from screenshots to a shipped product wearing them. Not
styling architecture (n-stylex), not behaviour testing (n-autoqa), not the
ticket workflow (intentfold / n-prodfarm), not brand or identity design.

Stack-specific traps met while two styling systems coexisted are in
`references/stack-traps.md` — verify before trusting.
