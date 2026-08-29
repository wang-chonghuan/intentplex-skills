#!/usr/bin/env node
/**
 * Horizontal-overflow scan across pages x viewport widths.
 *
 *   node overflow_probe.mjs --url http://localhost:3000 --paths /,/keywords
 *   node overflow_probe.mjs --url http://localhost:3000/proto --clicks "Home,Products"
 *   node overflow_probe.mjs --url ... --widths 320,390,768,1024,1280,1440
 *
 * --paths visits real routes; --clicks drives one prototype route whose pages
 * are behind nav buttons. Give one or the other; with neither, the URL alone is
 * probed.
 *
 * Elements inside a deliberate scroller (overflow-x: auto|scroll) are clipped,
 * not spilling, and are ignored — without that exclusion a scrolling nav row
 * reports its own off-screen children and buries the real offender.
 *
 * Exits non-zero on any overflow. PROVE IT CAN FAIL once per project: widen
 * something on purpose and watch it go red. A probe that has never failed is
 * not evidence.
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
const flag = (name, fallback = null) => {
  const i = args.indexOf(`--${name}`)
  return i === -1 ? fallback : args[i + 1]
}
const url = flag('url')
if (!url) {
  console.error('usage: overflow_probe.mjs --url <url> [--paths a,b] [--clicks A,B] [--widths ...]')
  process.exit(2)
}
const widths = (flag('widths', '320,390,768,1024,1280,1440')).split(',').map(Number)
const paths = flag('paths') ? flag('paths').split(',') : null
const clicks = flag('clicks') ? flag('clicks').split(',') : null

const browser = await chromium.launch({ headless: process.env.HEADED !== '1' })
const bad = []
let checks = 0

for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 900 } })
  const targets = paths ?? clicks ?? [null]

  for (const target of targets) {
    if (paths) await page.goto(new URL(target, url).href, { waitUntil: 'networkidle' })
    else if (page.url() === 'about:blank') await page.goto(url, { waitUntil: 'networkidle' })

    if (clicks && target) {
      await page.getByRole('button', { name: target, exact: true }).click()
      await page.waitForTimeout(250)
    }

    const result = await page.evaluate((vw) => {
      const doc = document.documentElement
      const over = doc.scrollWidth - doc.clientWidth
      const spills = []
      const inScroller = (el) => {
        for (let p = el.parentElement; p; p = p.parentElement) {
          const ox = getComputedStyle(p).overflowX
          if (ox === 'auto' || ox === 'scroll') return true
        }
        return false
      }
      if (over > 1) {
        for (const el of document.querySelectorAll('body *')) {
          const cs = getComputedStyle(el)
          if (cs.display === 'none' || cs.overflowX === 'auto' || cs.overflowX === 'scroll') continue
          if (inScroller(el)) continue
          const box = el.getBoundingClientRect()
          const spillsHere = Math.round(box.right - vw) > 1
          const childSpills = [...el.children].some(
            (c) => Math.round(c.getBoundingClientRect().right - vw) > 1,
          )
          // Name the innermost offender, not every ancestor of it.
          if (spillsHere && !childSpills) {
            spills.push(`${el.tagName.toLowerCase()} ${(el.textContent || '').trim().slice(0, 40)}`)
          }
        }
      }
      return { over, spills: spills.slice(0, 4) }
    }, width)

    checks += 1
    if (result.over > 1) bad.push({ width, target: target ?? url, ...result })
  }

  await page.close()
}

await browser.close()

if (!bad.length) {
  console.log(`OK: no horizontal overflow — ${checks} checks (${(paths ?? clicks ?? [url]).length} pages x ${widths.length} widths)`)
} else {
  for (const b of bad) {
    console.log(`${b.width}px  ${b.target} — ${b.over}px`)
    for (const s of b.spills) console.log(`    ${s}`)
  }
  process.exitCode = 1
}
