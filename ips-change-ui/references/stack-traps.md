# Traps when two styling systems coexist

Met while a StyleX design system overlapped a legacy component library. Names
are stack-specific; the mechanisms generalise. Verify before trusting.

- **Cascade layers beat specificity.** StyleX emits `@layer priority1..9`
  declared *before* the old library's `@layer reset`, so `:where(*){border-width:0}`,
  `:where(h1..h6){font-size:inherit}` and `:where(button){padding:0;font:inherit}`
  defeat every StyleX class. What held: inset `box-shadow` hairlines instead of
  borders; a `Pressable` whose `<button>` is the control and whose inner span is
  the paint; heading tags wrapping a span that carries the type.
- **A flex item will not shrink below its content** without `min-width: 0` — a
  scroller without it pushes the page wide instead of scrolling.
- **One long unbreakable word** (a domain as a 44px heading) is wider than a
  320px screen. `overflow-wrap: break-word` on the text primitive.
- **Overlapping `max-width` bands resolve by emission order**, so responsive
  bands must be mutually exclusive.
- **StyleX's babel plugin does not know Vite aliases** — declare `aliases` in
  the unplugin config or token imports silently fail to resolve.
- **Recharts**: pin `domain` / `tickCount` / `tickFormatter` when an axis draws
  ticks out of order; an absolutely positioned tooltip adds document scroll on
  phones — fix it to a bottom strip there.
