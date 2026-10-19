---
name: ips-design-to-antd
description: Load when the user likes a reference website's look (its buttons, colours, tags, cards) and wants their product restyled in that style while Ant Design stays the base. Covers measuring the site's real styles, settling which colour plays which role with the user, declaring every custom value in one table, mapping it to Ant theme tokens, finding code that bypasses the theme, and verifying the result. Triggers include "ips-design-to-antd", "我喜欢这个网站的设计风格", "按这个网站的风格定制 antd", "照着 xx.com 改我们的主题", "把网站风格换成这个", "抽取这个网站的样式", "restyle our Ant theme like this site", "make our antd look like <url>". Do not load to migrate an app onto Ant Design or for ordinary Ant component work (ips-antdesign), to rebuild a UI from designer screenshots (ips-change-ui), or to copy a site's layout or pages.
---

# ips-design-to-antd

Take the visual language of a site the user likes and express it as an Ant Design theme. Ant stays the component library. The job changes theme values: no `.ant-*` selectors, no second styling system, and no wrapper components where a token does the job.

The output is one declaration table of custom values, an Ant theme that reads only from it, a few charter sentences the user approved, and a delivery report.

## Inputs

- The reference URL. Required.
- What the user likes about it. Default: buttons, colours, tags and cards. Layout, page structure and copy are out of scope unless the user names them.
- From the target repo, found by reading its agent instructions and UI rules: the theme file (the single Ant `ThemeConfig`, e.g. `src/theme/ant-theme.ts`), the UI rules document (the charter, e.g. `.intentfold/charter/ui.md`), the brand asset pipeline if there is one, and the UI and full check commands.

When the repo's UI work is governed by ips-antdesign, follow its contract as well. This skill only decides what the theme values are and where they live.

`SKILL_ROOT` below means the directory holding this `SKILL.md`.

## Workflow

Do the steps in order. Steps 2 and 7 wait for the user.

### 1. Measure the reference site

1. Open the URL at 1440 px wide. Decline non-essential cookies. Screenshot the first screen and two or three sections that have cards and tags.
2. Evaluate `SKILL_ROOT/scripts/measure-style.js` in the page (paste it into the browser tool's JavaScript eval, or `page.evaluate(source)` in Playwright). It returns body and h1 type, every button-like, tag-like and card-like element with its background, text colour, border, radius, padding, height, weight and shadow, and the page's background and text colours ranked by count, all in hex. Scroll lazy-loaded sections into view and run it again if they hold cards or tags.
3. Write a palette: each colour, its hex value, and where the site uses it (buttons, links, highlighted words, tags, page background, cards, dividers).

Measure; do not describe the site from memory or from a screenshot alone. Screenshots shift colours and hide radii and weights.

### 2. Settle colour roles with the user

Show swatches and ask role by role. Give a recommendation and a reason for each.

| Role | Where it lands in Ant |
| --- | --- |
| Theme colour | links, selected tabs and menu items, focus rings, the logo |
| Button colour | primary buttons only |
| Text, secondary text, faint text | body copy, captions, placeholders |
| Tag background and text | `Tag` |
| Page background, card background | `Layout`, `Card` |

The button colour is often not the theme colour. Ask about them as two questions. On adsy.com the buttons are navy `#112C3E` and the theme colour is indigo `#3E4FEA`; this skill was written after an agent made navy the theme colour and the user had to correct it. Frequency is no guide either: indigo was 6 of about 230 painted backgrounds there, navy 12, white 174. The theme colour is usually the one used for emphasis (highlighted words in the headline, links, an accent card), not the most common one.

Ask whether to change the font and weights. Default: keep the product's own.

Check contrast before proposing anything: `node SKILL_ROOT/scripts/contrast.mjs '#FG:#BG' ...` for every text and background pair in the palette, including secondary text on the page background. Body text needs 4.5:1, large text and control borders 3:1. When a pair fails, darken or lighten it and report the original and adjusted values. adsy's secondary text `#677F9B` gets 4.13:1 on white; it was darkened to `#556D88` (5.34:1).

Write no code until the user has confirmed the roles.

### 3. Declare every custom value once

- Put every custom value (colours, card radius, pill radius) in one constant table at the top of the theme file, e.g. `export const BRAND_STYLE = { … } as const`, with a one-line comment on each entry saying what it is for. The theme reads its values only from this table.
- After editing, run `node SKILL_ROOT/scripts/check-theme-literals.mjs <theme-file> <TABLE_NAME>`. It fails on any colour literal in the theme file outside the table.
- The UI rules document names this table as the only place for custom values. That is a charter edit (step 7).
- Use tokens wherever they reach. When an Ant component must be overridden, it goes in one dedicated directory (e.g. `src/components/ant-overrides/`), one component per file, each listed in the UI rules document. Nothing goes anywhere else.

### 4. Map the table to Ant tokens

Read [token mapping](references/token-mapping.md). It lists the global and component tokens to set, and the defaults Ant keeps when a token is left out.

### 5. Find code that bypasses the theme

Changing the theme does nothing where a component paints its own colour. Search for:

- Shell and layout components (frame, header, content, footer) with inline backgrounds taken from `token.colorBgContainer`, and CSS rules that paint backgrounds. The page background should come from `colorBgLayout`; the header usually stays white.
- Hex and `rgb()` literals in components and stylesheets outside the theme file.
- Variants that depend on the primary colour, such as `color="primary" variant="filled"`, and preset-coloured `Tag`s. Look at each with the new colours and fix the ones that look wrong.

```bash
rg -n "colorBgContainer|background" src/components src/styles
rg -n "#[0-9a-fA-F]{6}\b|rgba?\(" src --glob '!src/theme/**'
rg -n 'variant="filled"|<Tag[^>]*color=' src
```

### 6. Leave the logo alone unless asked

Change the logo only when the user asks.

- If the brand assets are generated from a config (e.g. `src/theme/brand.json` and a `brand:build` script), change only the colours there and regenerate. Do not change the shapes or the typeface.
- If a guard pins asset hashes, update the pinned hashes after the approved change, in the same commit.
- If the charter forbids recolouring the logo, the rule must be reworded with the user's approval first (step 7).

### 7. Ask before editing the charter

The UI rules document belongs to the user. For each clause about colour, type, logo, wrapping Ant components or the declaration table, show the current sentence and the proposed one, and wait for a yes.

### 8. Do not copy marketing-page proportions

Reference sites are often marketing pages: tall buttons, 40 px card radii, big type. A data-dense product keeps Ant's default control heights and its own type scale, and uses a card radius around 16–20 px. The mobile browser theme colour stays the same as the header colour. Keep a list of everything not copied and why; it goes in the report.

### 9. Verify

1. Build for production and serve locally. Use Playwright at 1440 and 375 px on the product's main pages: the home page, a list or results page, a detail page, and any saved or settings page.
2. Read the computed colours of the key elements and compare them with the palette: a primary button, a default button, a link, a selected tab, body text, a tag, the page background, a card.
3. At 375 px, `document.documentElement.scrollWidth` must equal `innerWidth`.
4. Run the repo's UI check (refresh any UI mapping it reports as drifted) and its full check.
5. Write the delivery report: the palette with roles, the contrast results with any adjusted colours, what was not copied and why, the charter sentences changed, and the files touched.

## Done when

- The user confirmed the colour roles before any code changed.
- Every custom value is in the one table, and `check-theme-literals.mjs` passes.
- Links, info states and focus rings use the theme colour, not Ant's default blue `#1677FF`.
- Measured colours on the main pages match the palette at both widths, and the 375 px pages do not scroll sideways.
- The UI check and full check pass.
- Charter edits were approved by the user, and the report lists everything above.
