#!/usr/bin/env node
// Check that a theme file declares its colours only in one constant table.
//
//   node check-theme-literals.mjs <theme-file> <TABLE_NAME>
//
// Finds `const TABLE_NAME = {` and its closing brace, then reports every
// colour literal (#hex, rgb(), rgba(), hsl(), hsla()) outside that table.
// Comments are ignored. Exits 1 when the table is missing or a literal is found.

import { readFileSync } from 'node:fs'

const [file, table] = process.argv.slice(2)
if (!file || !table) {
  console.error('usage: node check-theme-literals.mjs <theme-file> <TABLE_NAME>')
  process.exit(2)
}

const source = readFileSync(file, 'utf8')
// Blank out comments but keep offsets and line breaks.
const code = source
  .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
  .replace(/\/\/[^\n]*/g, (m) => ' '.repeat(m.length))

const head = new RegExp(`const\\s+${table}\\s*(?::[^=]+)?=\\s*\\{`).exec(code)
if (!head) {
  console.error(`${file}: no \`const ${table} = {\` found`)
  process.exit(1)
}

let depth = 0
let end = -1
for (let i = head.index + head[0].length - 1; i < code.length; i++) {
  if (code[i] === '{') depth++
  else if (code[i] === '}' && --depth === 0) { end = i; break }
}
if (end < 0) {
  console.error(`${file}: \`${table}\` has no closing brace`)
  process.exit(1)
}

const literal = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(/g
const lineOf = (offset) => source.slice(0, offset).split('\n').length
const found = []
for (const m of code.matchAll(literal)) {
  if (m.index >= head.index && m.index <= end) continue
  found.push(`${file}:${lineOf(m.index)}  ${m[0]}`)
}

if (found.length) {
  console.error(`colour literals outside ${table}:`)
  found.forEach((f) => console.error(`  ${f}`))
  process.exit(1)
}
console.log(`ok: every colour literal in ${file} is inside ${table}`)
