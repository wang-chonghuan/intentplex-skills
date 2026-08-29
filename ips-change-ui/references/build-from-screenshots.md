# cap1 — Building the system from screenshots

Input: a handful of images and "我想让整个 app 都用这个 UI". Output: not a page
that resembles them, but a **design system** — one token registry, atoms through
templates — plus a demo that proves it and an inventory that names it.

## Ask before you build

Open **every** screenshot before saying anything about approach. Questions, in
order of how much rework they prevent:

1. **Coverage** — which of my pages does each screenshot correspond to, and
   which of my pages has no screenshot at all?
2. **Design vs source app** — the screenshots are usually of *another* product.
   Which parts are the language (type, spacing, colour, component shapes) and
   which are that product's brand, nav and information architecture, which must
   not come along?
3. **Fidelity** — pixel-level, or the spirit of it?
4. **Demo depth** — static reproduction, or clickable?
5. **Type** — is the typeface available and licensed? If not, what substitutes?
6. **Theme** — dark mode now, later, or never? It decides whether colour tokens
   are semantic or literal from day one.
7. **Responsive floor** — the narrowest width that must work.

## Measure, do not eyeball

Recover the render scale from an element whose real size is knowable — an icon,
a control height, a known type size — and divide every measurement by it. One
project's screenshots came out at 0.598. Eyeballed values look fine, cannot be
checked, and invite the next one beside them.

## One registry

A single file holding `color`, `font`, `space` (one scale), `radius`, `shadow`,
`size`, `layout`, `motion`, breakpoints.

- **Breakpoint bands must be mutually exclusive** — overlapping `max-width`
  queries resolve by emission order, not specificity.
- **Brand and accent live in a theme file**, never as overrides of registry
  names in `:root`.
- **A value the screenshots do not show is derived from the system's own
  principles**, never borrowed from the app being replaced.
- Anything the registry cannot express is a request to extend it, put to the
  user — not a one-off literal.

## Structure

```
<system>/
  tokens.*        the registry — the only place values live
  atoms/ molecules/ organisms/ templates/
  demo/           the proof
```

Two atoms earn their place first because everything leans on them: a **Text**
primitive owning every type decision, and a **Pressable** keeping the `<button>`
as the control while an inner element carries the paint. Both also survive a
foreign reset (see `stack-traps.md`).

## The demo covers every content shape, not every screenshot

**This is what decides whether cap6 succeeds.** The demo naturally reproduces
the screenshots; the product also contains shapes they never showed — a dense
sortable table, a long filter row, a page of prose, a chart, an empty state, a
paginated listing. When the migration reaches one with no precedent in the
system, the path of least resistance is to keep the old shape. That is how a
transliteration begins.

So list the product's content shapes first and make the demo render each one at
least once. Where the design has no obvious answer, that is a design question
for the user now, while it costs nothing.

## Write the inventory

One line per component: what it is, and what content it carries.

```
Chip        a state or verdict, one word
Badge       a count, never a state
KPI card    one number that matters, with its label and direction
Card row    one record, when the record has a face
Table row   one record, when density beats identity
Rail        secondary context beside the main answer
```

Without it, "which part of the language carries this block?" has no answer at
migration time and the honest fallback is the old component. With it, cap3 is a
lookup and a missing entry is a visible finding.

## Prove it, then freeze it

- Demo behind a small footer link, own route, no product page touched.
- Responsive integrity verified with `scripts/overflow_probe.mjs` across every
  demo page × every width down to the agreed floor — and the probe proven able
  to fail once.
- Read your own captures at desktop and phone before handing over.
- On approval, cut the frozen copy (`<system>-REF-ONLY`, byte-identical,
  read-only, redlined). Everything after edits the working copy; the frozen one
  is what "did we drift?" is answered against.
