import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync } from 'node:fs'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'eval-acceptance' }
const valid = await tools['eval.pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }] } }, exec)
const bad = await tools['eval.pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }, { id: 't1' }] } }, exec)
const grade = await tools['eval.grade'].execute({ actual: { a: 1 }, expected: { a: 1 } }, exec)
const reordered = await tools['eval.grade'].execute({ actual: { a: 1, b: 2 }, expected: { b: 2, a: 1 } }, exec)
const arrayOrder = await tools['eval.grade'].execute({ actual: [1, 2], expected: [2, 1] }, exec)
const summary = await tools['eval.summary'].execute({ results: [{ id: 't1', actual: { a: 1 }, expected: { a: 1 } }, { id: 't2', actual: { a: 2 }, expected: { a: 1 } }] }, exec)
const pak = await tools['eval.pass_at_k'].execute({ k: 1, tasks: [{ task_id: 't1', samples: 10, correct: 3 }] }, exec)
const pak5 = await tools['eval.pass_at_k'].execute({ k: 5, tasks: [{ task_id: 't1', samples: 20, correct: 2 }] }, exec)
const rows = [
  { req_id: 'EVAL-A01', metric: 'valid pack accepted', actual: valid.ok, expected: true },
  { req_id: 'EVAL-A02', metric: 'duplicate task ids rejected', actual: bad.ok === false && bad.errors.some((e) => e.includes('DUPLICATE')), expected: true },
  { req_id: 'EVAL-A03', metric: 'deterministic grade', actual: grade.pass, expected: true },
  { req_id: 'EVAL-A04', metric: 'canonical grading ignores key order', actual: reordered.pass, expected: true },
  { req_id: 'EVAL-A05', metric: 'array order still matters', actual: arrayOrder.pass === false, expected: true },
  { req_id: 'EVAL-A06', metric: 'run summary pass rate', actual: summary.passed === 1 && summary.failed === 1 && summary.pass_rate === 0.5, expected: true },
  { req_id: 'EVAL-A07', metric: 'pass@k estimator', actual: pak.tasks[0].pass_at_k === 0.3 && pak5.tasks[0].pass_at_k > 0.3, expected: true },
]
for (const row of rows) if (row.actual !== row.expected) throw new Error(`failed ${row.req_id}`)

// PS1-QS01: recompute the shipped quickstart and hash its golden file as evidence.
const quickstart = execFileSync(process.execPath, ['samples/quickstart/run.mjs', '--check'], { cwd: process.cwd(), encoding: 'utf8' })
if (!quickstart.includes('quickstart ok')) throw new Error('PS1-QS01 quickstart check did not print ok')
const quickstartSha = createHash('sha256').update(readFileSync('samples/quickstart/expected/result.json')).digest('hex')
const evidenceSha = createHash('sha256').update(JSON.stringify(rows)).digest('hex')

const header = 'req_id,metric,threshold,actual,script,evidence_sha256,pass,source,counted'
const lines = [
  header,
  ...rows.map((r) => `${r.req_id},${r.metric},1/1,${r.actual},scripts/acceptance.mjs,${evidenceSha},true,public/synthetic,false`),
  `PS1-QS01,quickstart 样例与金标一致,1/1,1,scripts/acceptance.mjs,${quickstartSha},true,synthetic/quickstart,true`,
]
writeFileSync('ACCEPTANCE.csv', lines.join('\n') + '\n')
console.log('acceptance ok: 7/7 public/synthetic + PS1-QS01 quickstart')
