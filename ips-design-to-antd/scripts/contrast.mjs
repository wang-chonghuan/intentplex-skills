#!/usr/bin/env node
// WCAG 2.x contrast ratio for text/background pairs.
//
//   node contrast.mjs '#112C3E:#F5F8FA' '#556D88:#FFFFFF' ...
//
// Each argument is foreground:background in #RGB or #RRGGBB. Prints the
// ratio and whether it passes 4.5:1 (body text) and 3:1 (large text, icons,
// control borders). Exits 1 when any pair is below 4.5:1.

const parse = (value) => {
  let h = value.trim().replace(/^#/, '')
  if (h.length === 3) h = [...h].map((c) => c + c).join('')
  if (!/^[0-9a-fA-F]{6}$/.test(h)) throw new Error(`not a hex colour: ${value}`)
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
}

const luminance = (rgb) => {
  const [r, g, b] = rgb.map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

const ratio = (fg, bg) => {
  const [a, b] = [luminance(parse(fg)), luminance(parse(bg))].sort((x, y) => y - x)
  return (a + 0.05) / (b + 0.05)
}

const pairs = process.argv.slice(2)
if (pairs.length === 0) {
  console.error("usage: node contrast.mjs '#FG:#BG' ['#FG:#BG' ...]")
  process.exit(2)
}

let failed = false
for (const pair of pairs) {
  const [fg, bg] = pair.split(':')
  if (!fg || !bg) {
    console.error(`skip ${pair}: expected foreground:background`)
    failed = true
    continue
  }
  const r = ratio(fg, bg)
  const body = r >= 4.5
  const large = r >= 3
  if (!body) failed = true
  console.log(`${fg.toUpperCase()} on ${bg.toUpperCase()}  ${r.toFixed(2)}:1  body ${body ? 'pass' : 'FAIL'}  large ${large ? 'pass' : 'FAIL'}`)
}
process.exit(failed ? 1 : 0)
