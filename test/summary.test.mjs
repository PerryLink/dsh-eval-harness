import test from 'node:test'
import assert from 'node:assert/strict'
import { canonical, grade, summarize } from '../lib/core/harness.js'
import { createTools } from '../lib/plugin/tools.js'

const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'eval' }

test('canonical grading ignores object key order but keeps array order', () => {
  assert.equal(grade({ a: 1, b: { c: 2, d: 3 } }, { b: { d: 3, c: 2 }, a: 1 }), true)
  assert.equal(grade([1, 2], [2, 1]), false)
  assert.equal(canonical({ b: 2, a: 1 }), '{"a":1,"b":2}')
})

test('summarize reports pass rate and failing ids', () => {
  const s = summarize([
    { id: 't1', actual: { a: 1 }, expected: { a: 1 } },
    { id: 't2', actual: { a: 2 }, expected: { a: 1 } },
    { id: 't3', actual: [1, 2], expected: [1, 2] },
  ])
  assert.equal(s.total, 3)
  assert.equal(s.passed, 2)
  assert.equal(s.failed, 1)
  assert.equal(s.pass_rate, 0.666667)
  assert.deepEqual(s.failures, ['t2'])
})

test('an empty run has a zero pass rate and no failures', () => {
  const s = summarize([])
  assert.equal(s.total, 0)
  assert.equal(s.pass_rate, 0)
  assert.deepEqual(s.failures, [])
})

test('the tool exposes the summary', async () => {
  const r = await tools['eval_summary'].execute({ results: [{ id: 't1', actual: { x: 1, y: 2 }, expected: { y: 2, x: 1 } }] }, exec)
  assert.equal(r.passed, 1)
  assert.equal(r.pass_rate, 1)
})
