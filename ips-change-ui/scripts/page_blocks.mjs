#!/usr/bin/env node
/**
 * The block list of a running page: headings in document order, table column
 * headers, and form controls.
 *
 * Run it against the old page and the new one; the diff is the parity check.
 * A restyle whose two lists differ has dropped, added or renamed a block —
 * which is the failure this exists to catch, because the eye does not catch it.
 *
 *   node page_blocks.mjs http://localhost:3000/keywords
 *   node page_blocks.mjs http://localhost:3000/prototype --click "Keywords"
 *   node page_blocks.mjs <url> --json > new.json
 *
 * --click drives a single-route prototype whose pages are behind nav buttons.
 * Exits non-zero when the page yields no headings at all — usually a wrong URL
 * or a page that never finished rendering, which must not read as "no blocks".
 */
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'

// The skill lives outside the project, so `import 'playwright'` would resolve
// against ~/.claude and fail. Resolve it from the working directory instead —
// run these scripts from the project root.
const requireFromCwd = createRequire(pathToFileURL(`${process.cwd()}/`))
let chromium
try {
  ;({ chromium } = requireFromCwd('playwright'))
} catch {
  try {
    ;({ chromium } = requireFromCwd('playwright-core'))
  } catch {
    console.error('playwright not resolvable from ' + process.cwd() + ' — run from the project root, or npm i -D playwright')
    process.exit(2)
  }
}

const args = process.argv.slice(2)
const url = args.find((a) => !a.startsWith('--'))
const flag = (name) => {
  const i = args.indexOf(`--${name}`)
  return i === -1 ? null : args[i + 1]
}
if (!url) {
  console.error('usage: page_blocks.mjs <url> [--click "Nav name"] [--json]')
  process.exit(2)
}

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } })
await page.goto(url, { waitUntil: 'networkidle' })

const click = flag('click')
if (click) {
  await page.getByRole('button', { name: click, exact: true }).click()
  await page.waitForTimeout(400)
}

const blocks = await page.evaluate(() => {
  const seen = []
  const text = (el) => (el.textContent || '').replace(/\s+/g, ' ').trim()

  for (const el of document.querySelectorAll('h1, h2, h3, h4, h5, h6')) {
    if (!text(el)) continue
    seen.push({ kind: `h${el.tagName[1]}`, text: text(el) })
  }

  const columns = []
  for (const el of document.querySelectorAll('th, [role="columnheader"]')) {
    if (text(el)) columns.push(text(el))
  }

  const controls = []
  for (const el of document.querySelectorAll('select, input, textarea')) {
    const label =
      el.getAttribute('aria-label') ||
      el.getAttribute('placeholder') ||
      el.getAttribute('name') ||
      el.type ||
      el.tagName.toLowerCase()
    controls.push(`${el.tagName.toLowerCase()}: ${label}`)
  }

  return { headings: seen, columns, controls }
})

await browser.close()

if (args.includes('--json')) {
  console.log(JSON.stringify({ url, click, ...blocks }, null, 2))
} else {
  console.log(`# ${url}${click ? ` — ${click}` : ''}`)
  console.log('\n## headings')
  for (const h of blocks.headings) console.log(`${h.kind}  ${h.text}`)
  console.log('\n## columns')
  for (const c of blocks.columns) console.log(`- ${c}`)
  console.log('\n## controls')
  for (const c of blocks.controls) console.log(`- ${c}`)
}

if (!blocks.headings.length) {
  console.error('\nNo headings found — wrong URL, or the page never rendered.')
  process.exit(1)
}
