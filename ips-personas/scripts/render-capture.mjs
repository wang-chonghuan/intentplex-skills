// Render a LIVE web target in real Chromium (executes JS, renders SPAs) and capture
// what a real user actually sees. WebFetch/curl only return the un-rendered shell, so
// personas must judge from THIS output, not from a fetch of a JavaScript app.
//
// Usage:
//   node scripts/render-capture.mjs <url> <outDir> ["Label A" "Label B" ...]
//
// Writes to <outDir>: NN-<slug>.png (full-page screenshot per state),
// steps.json (verbatim on-screen innerText per state), capture-log.txt (http>=400 / errors).
// Each label is clicked (button > link > any text match) after the landing state, producing one more state.
//
// Prerequisite: Playwright + Chromium. n-autoqa capability 1 provisions it, or run:
//   npx playwright install chromium
//
// GOTCHA (do not "fix"): SPAs with continuous network (maps, polling) never reach
// networkidle, so we wait on domcontentloaded + a stability window, NOT networkidle.

import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';

// Resolve Playwright from the TARGET repo (where n-autoqa cap 1 / npm installs it), not from
// this skill's directory — ESM bare imports would otherwise look next to this file and fail.
function loadPlaywright() {
  for (const base of [process.cwd() + '/', import.meta.url]) {
    try { return createRequire(base)('playwright'); } catch { /* try next */ }
  }
  console.error('Playwright not found. Install it in this repo:  npm i -D playwright && npx playwright install chromium');
  process.exit(3);
}
const { chromium } = loadPlaywright();

const [, , url, outDir, ...labels] = process.argv;
if (!url || !outDir) {
  console.error('usage: node render-capture.mjs <url> <outDir> [clickLabel ...]');
  process.exit(2);
}
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
const steps = [];
const log = [];
page.on('pageerror', (e) => log.push(`[pageerror] ${e.message}`));
page.on('response', (r) => { if (r.status() >= 400) log.push(`[http ${r.status()}] ${r.url()}`); });

const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'step';
let n = 0;
async function snap(label) {
  n += 1;
  const name = `${String(n).padStart(2, '0')}-${slug(label)}`;
  await page.waitForTimeout(1500); // SPA render stability window
  await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: true });
  const text = await page.evaluate(() => document.body?.innerText || '');
  steps.push({ name, label, text: text.replace(/\n{2,}/g, '\n').trim().slice(0, 4000) });
  console.log(`\n===== ${name} — ${label} =====\n${text.slice(0, 800)}`);
}
async function click(label) {
  const tries = [
    () => page.getByRole('button', { name: label, exact: true }).first().click({ timeout: 8000 }),
    () => page.getByRole('link', { name: label, exact: false }).first().click({ timeout: 5000 }),
    () => page.getByText(label, { exact: false }).first().click({ timeout: 5000 }),
  ];
  for (const t of tries) { try { await t(); return true; } catch { /* next */ } }
  log.push(`[click fail] ${label}`);
  return false;
}

try {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('body *', { timeout: 30000 }).catch(() => log.push('[warn] body slow to populate'));
  await page.waitForTimeout(2500);
  await snap('landing');
  for (const label of labels) { if (await click(label)) await snap(label); }
} catch (e) {
  log.push(`[fatal] ${e.message}`);
}

fs.writeFileSync(path.join(outDir, 'steps.json'), JSON.stringify(steps, null, 2));
fs.writeFileSync(path.join(outDir, 'capture-log.txt'), log.join('\n'));
console.log(`\n=== ${steps.length} state(s) captured to ${outDir} ===\n` + steps.map((s) => `${s.name}.png — ${s.label}`).join('\n'));
if (log.length) console.log('\n[log]\n' + log.join('\n'));
await browser.close();
