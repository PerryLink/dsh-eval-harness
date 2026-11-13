import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'eval' }
test('valid pack', async () => {
  const r = await tools['eval_pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }] } }, exec)
  assert.equal(r.ok, true); assert.deepEqual(r.errors, [])
})
test('duplicate/empty pack', async () => {
  const r = await tools['eval_pack_lint'].execute({ pack: { name: 'demo', version: '1', tasks: [{ id: 't1' }, { id: 't1' }] } }, exec)
  assert.equal(r.ok, false); assert.ok(r.errors.some((e) => e.includes('DUPLICATE')))
})
test('deterministic grade', async () => {
  assert.equal((await tools['eval_grade'].execute({ actual: { a: 1 }, expected: { a: 1 } }, exec)).pass, true)
  assert.equal((await tools['eval_grade'].execute({ actual: { a: 1 }, expected: { a: 2 } }, exec)).pass, false)
})
