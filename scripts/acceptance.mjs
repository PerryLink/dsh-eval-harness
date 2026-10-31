import { writeFileSync } from 'node:fs'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'eval-acceptance' }
const valid = await tools['eval.pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }] } }, exec)
const bad = await tools['eval.pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }, { id: 't1' }] } }, exec)
const grade = await tools['eval.grade'].execute({ actual: { a: 1 }, expected: { a: 1 } }, exec)
const rows = [
  { req_id: 'EVAL-A01', metric: 'valid pack accepted', actual: valid.ok, expected: true },
  { req_id: 'EVAL-A02', metric: 'duplicate task ids rejected', actual: bad.ok === false && bad.errors.some((e) => e.includes('DUPLICATE')), expected: true },
  { req_id: 'EVAL-A03', metric: 'deterministic grade', actual: grade.pass, expected: true },
]
for (const row of rows) if (row.actual !== row.expected) throw new Error(`failed ${row.req_id}`)
const csv = ['req_id,metric,actual,pass,source,counted', ...rows.map((r) => `${r.req_id},${r.metric},${r.actual},true,public/synthetic,false`)].join('\n') + '\n'
writeFileSync('ACCEPTANCE.csv', csv)
console.log('acceptance ok: 3/3 public/synthetic')
