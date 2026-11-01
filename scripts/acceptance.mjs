import { writeFileSync } from 'node:fs'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'eval-acceptance' }
const valid = await tools['eval.pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }] } }, exec)
const bad = await tools['eval.pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }, { id: 't1' }] } }, exec)
const grade = await tools['eval.grade'].execute({ actual: { a: 1 }, expected: { a: 1 } }, exec)
const reordered = await tools['eval.grade'].execute({ actual: { a: 1, b: 2 }, expected: { b: 2, a: 1 } }, exec)
const arrayOrder = await tools['eval.grade'].execute({ actual: [1, 2], expected: [2, 1] }, exec)
const summary = await tools['eval.summary'].execute({ results: [{ id: 't1', actual: { a: 1 }, expected: { a: 1 } }, { id: 't2', actual: { a: 2 }, expected: { a: 1 } }] }, exec)
const rows = [
  { req_id: 'EVAL-A01', metric: 'valid pack accepted', actual: valid.ok, expected: true },
  { req_id: 'EVAL-A02', metric: 'duplicate task ids rejected', actual: bad.ok === false && bad.errors.some((e) => e.includes('DUPLICATE')), expected: true },
  { req_id: 'EVAL-A03', metric: 'deterministic grade', actual: grade.pass, expected: true },
  { req_id: 'EVAL-A04', metric: 'canonical grading ignores key order', actual: reordered.pass, expected: true },
  { req_id: 'EVAL-A05', metric: 'array order still matters', actual: arrayOrder.pass === false, expected: true },
  { req_id: 'EVAL-A06', metric: 'run summary pass rate', actual: summary.passed === 1 && summary.failed === 1 && summary.pass_rate === 0.5, expected: true },
]
for (const row of rows) if (row.actual !== row.expected) throw new Error(`failed ${row.req_id}`)
const csv = ['req_id,metric,actual,pass,source,counted', ...rows.map((r) => `${r.req_id},${r.metric},${r.actual},true,public/synthetic,false`)].join('\n') + '\n'
writeFileSync('ACCEPTANCE.csv', csv)
console.log('acceptance ok: 6/6 public/synthetic')
