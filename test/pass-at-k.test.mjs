import test from 'node:test'
import assert from 'node:assert/strict'
import { passAtK, passAtKMean } from '../lib/core/harness.js'
import { createTools } from '../lib/plugin/tools.js'

const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'pak' }

test('pass@1 equals the empirical success rate', () => {
  assert.equal(passAtK({ task_id: 't', samples: 10, correct: 3 }, 1).pass_at_k, 0.3)
})

test('all-correct and none-correct are the boundaries', () => {
  assert.equal(passAtK({ task_id: 't', samples: 5, correct: 5 }, 3).pass_at_k, 1)
  assert.equal(passAtK({ task_id: 't', samples: 5, correct: 0 }, 3).pass_at_k, 0)
})

test('the estimator is monotonic in k and above the empirical rate', () => {
  const task = { task_id: 't', samples: 20, correct: 2 }
  const p1 = passAtK(task, 1).pass_at_k
  const p5 = passAtK(task, 5).pass_at_k
  const p10 = passAtK(task, 10).pass_at_k
  assert.ok(p1 < p5 && p5 < p10)
  assert.ok(Math.abs(p1 - 0.1) < 1e-9)
  // exact value for n=20,c=2,k=5: 1 - C(18,5)/C(20,5)
  assert.ok(Math.abs(p5 - (1 - 8568 / 15504)) < 1e-6)
})

test('invalid inputs are rejected and the mean is reported', () => {
  assert.throws(() => passAtK({ task_id: 't', samples: 3, correct: 4 }, 1), /E_EVAL_CORRECT/)
  assert.throws(() => passAtK({ task_id: 't', samples: 3, correct: 1 }, 4), /E_EVAL_K/)
  const mean = passAtKMean([{ task_id: 'a', samples: 4, correct: 2 }, { task_id: 'b', samples: 4, correct: 4 }], 2)
  assert.equal(mean.tasks.length, 2)
  assert.ok(mean.mean > 0.5 && mean.mean <= 1)
})

test('the tool exposes the per-task and mean values', async () => {
  const r = await tools['eval_pass_at_k'].execute({ k: 1, tasks: [{ task_id: 'a', samples: 4, correct: 1 }] }, exec)
  assert.equal(r.k, 1)
  assert.equal(r.tasks[0].pass_at_k, 0.25)
  assert.equal(r.mean, 0.25)
})
