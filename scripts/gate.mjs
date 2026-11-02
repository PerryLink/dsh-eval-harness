import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
execFileSync(process.execPath, ['scripts/acceptance.mjs'], { stdio: 'inherit' })
const rows = readFileSync('ACCEPTANCE.csv', 'utf8').trim().split('\n').slice(1)
const publicRows = rows.filter((row) => row.endsWith(',true,public/synthetic,false'))
const quickstartRows = rows.filter((row) => row.startsWith('PS1-QS01,') && row.endsWith(',true,synthetic/quickstart,true'))
if (rows.length === 0 || publicRows.length + quickstartRows.length !== rows.length || quickstartRows.length !== 1) process.exit(1)
console.log(`gate ok: ${publicRows.length} public/synthetic rows + ${quickstartRows.length} quickstart row`)
