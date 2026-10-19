// Measure a reference site's visual language from the live DOM.
//
// Evaluate this whole file as one expression in the page:
//   - a browser tool's JavaScript eval: paste the file contents;
//   - Playwright: await page.evaluate(fs.readFileSync(path, 'utf8')).
// It returns JSON: body and h1 type, button-like, tag-like and card-like
// elements, and background and text colours ranked by how often they occur.
// Scroll lazy-loaded sections into view first; elements that have not
// rendered cannot be measured.
(() => {
  const hex = (rgb) => {
    const m = rgb.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/)
    if (!m) return rgb
    const h = [m[1], m[2], m[3]].map((n) => Math.round(+n).toString(16).padStart(2, '0')).join('')
    const a = m[4] === undefined ? '' : ` a=${m[4]}`
    return `#${h.toUpperCase()}${a}`
  }
  const transparent = (c) => c === 'rgba(0, 0, 0, 0)' || c === 'transparent'
  const noBorder = (c) => c.borderStyle === 'none' || /^0px( 0px)*$/.test(c.borderWidth) || transparent(c.borderColor)
  const text = (el) => (el.innerText || '').trim().replace(/\s+/g, ' ')
  const pick = (el) => {
    const c = getComputedStyle(el)
    const r = el.getBoundingClientRect()
    return {
      text: text(el).slice(0, 50),
      tag: el.tagName.toLowerCase(),
      bg: hex(c.backgroundColor),
      color: hex(c.color),
      border: noBorder(c) ? 'none' : `${c.borderWidth} ${c.borderStyle} ${hex(c.borderColor)}`,
      radius: c.borderRadius,
      font: c.fontFamily.slice(0, 60),
      size: c.fontSize,
      weight: c.fontWeight,
      letterSpacing: c.letterSpacing,
      padding: c.padding,
      w: Math.round(r.width),
      h: Math.round(r.height),
      shadow: c.boxShadow === 'none' ? 'none' : c.boxShadow.slice(0, 90),
    }
  }
  const dedupe = (items) => {
    const seen = new Set()
    return items.filter((i) => {
      const key = [i.bg, i.color, i.border, i.radius, i.h, i.weight].join('|')
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }
  const all = [...document.querySelectorAll('body *')]

  const buttons = [...document.querySelectorAll('a, button, [role="button"], input[type="submit"]')].filter((e) => {
    const c = getComputedStyle(e)
    const r = e.getBoundingClientRect()
    const t = text(e) || e.value || ''
    return r.height > 28 && r.height < 80 && t.length > 0 && t.length < 40 &&
      (!transparent(c.backgroundColor) || !noBorder(c))
  })

  const tagLike = all.filter((e) => {
    const c = getComputedStyle(e)
    const r = e.getBoundingClientRect()
    const t = text(e)
    return r.height > 18 && r.height < 44 && parseFloat(c.borderRadius) >= 10 &&
      !transparent(c.backgroundColor) && t.length > 0 && t.length < 30 && e.children.length < 4 &&
      e.tagName !== 'BUTTON' && e.tagName !== 'A'
  })

  const cards = all.filter((e) => {
    const c = getComputedStyle(e)
    const r = e.getBoundingClientRect()
    return r.width > 250 && r.height > 150 && parseFloat(c.borderRadius) >= 12 &&
      (!transparent(c.backgroundColor) || c.boxShadow !== 'none' || !noBorder(c))
  })

  const rank = (values) => {
    const counts = {}
    values.forEach((v) => { counts[v] = (counts[v] || 0) + 1 })
    return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 12)
  }
  const backgrounds = rank(all.map((e) => getComputedStyle(e).backgroundColor).filter((c) => !transparent(c)).map(hex))
  const textColours = rank(all.filter((e) => e.children.length === 0 && text(e)).map((e) => hex(getComputedStyle(e).color)))

  const body = getComputedStyle(document.body)
  const h1 = document.querySelector('h1')
  return {
    url: location.href,
    viewport: `${innerWidth}x${innerHeight}`,
    body: { bg: hex(body.backgroundColor), color: hex(body.color), font: body.fontFamily, size: body.fontSize },
    h1: h1 ? pick(h1) : null,
    buttons: dedupe(buttons.map(pick)).slice(0, 14),
    tagLike: dedupe(tagLike.map(pick)).slice(0, 10),
    cards: dedupe(cards.map(pick)).slice(0, 10),
    backgrounds,
    textColours,
  }
})()
