import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
execFileSync(process.execPath, ['scripts/acceptance.mjs'], { stdio: 'inherit' })
const rows = readFileSync('ACCEPTANCE.csv', 'utf8').trim().split('\n').slice(1)
if (rows.length === 0 || rows.some((row) => !row.endsWith(',true,public/synthetic,false'))) process.exit(1)
console.log(`gate ok: ${rows.length} public/synthetic rows`)
