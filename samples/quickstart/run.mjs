#!/usr/bin/env node
/**
 * dsh-eval-pack quickstart — lints the bundled synthetic eval pack, grades the shipped
 * reference run, and reports pass@k. `expected/result.json` is the stdout of
 * `node samples/quickstart/run.mjs --json`, so it is a real run over the sample.
 *
 *   node samples/quickstart/run.mjs            # human-readable summary
 *   node samples/quickstart/run.mjs --json     # the golden result on stdout
 *   node samples/quickstart/run.mjs --check    # recompute and diff against the golden file
 *
 * Everything is local and synthetic: no model call, no network, no customer data.
 */
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createTools } from '../../lib/plugin/tools.js'

const here = path.dirname(fileURLToPath(import.meta.url))
const inputDir = path.join(here, 'input')
const expectedPath = path.join(here, 'expected', 'result.json')
const mode = process.argv.includes('--check') ? 'check' : process.argv.includes('--json') ? 'json' : 'summary'
const readJson = async (name) => JSON.parse(await readFile(path.join(inputDir, name), 'utf8'))

async function run() {
  const pack = await readJson('pack.json')
  const reference = await readJson('run.json')
  const cases = []
  for (const task of pack.tasks) cases.push(await readJson(path.join('cases', `${task.id}.json`)))

  const tools = Object.fromEntries(createTools().map((tool) => [tool.name, tool]))
  const call = (name, args) => tools[name].execute(args, { callId: 'quickstart' })
  const actualById = new Map(reference.results.map((result) => [result.id, result.actual]))

  const lint = await call('eval.pack_lint', { pack })
  const results = []
  const grades = []
  for (const testCase of cases) {
    const actual = actualById.get(testCase.id)
    assert.notEqual(actual, undefined, `run.json has no result for ${testCase.id}`)
    const graded = await call('eval.grade', { actual, expected: testCase.expected })
    grades.push({ id: testCase.id, pass: graded.pass })
    results.push({ id: testCase.id, actual, expected: testCase.expected })
  }
  const summary = await call('eval.summary', { results })
  const pass1 = await call('eval.pass_at_k', { k: 1, tasks: reference.sampling })
  const pass3 = await call('eval.pass_at_k', { k: 3, tasks: reference.sampling })
  const compact = (result) => ({ mean: result.mean, tasks: result.tasks.map((task) => ({ task_id: task.task_id, pass_at_k: task.pass_at_k })) })

  return {
    sample: 'samples/quickstart/input',
    synthetic: true,
    pack: { name: pack.name, version: pack.version, tasks: pack.tasks.length },
    lint: { ok: lint.ok, errors: lint.errors },
    grades,
    summary,
    pass_at_1: compact(pass1),
    pass_at_3: compact(pass3),
  }
}

function printSummary(result) {
  console.log('dsh-eval-pack quickstart - synthetic eval pack (not a benchmark)')
  console.log(`pack ${result.pack.name}@${result.pack.version}: lint ${result.lint.ok ? 'ok' : result.lint.errors.join(', ')}, ${result.pack.tasks} tasks`)
  console.log(`grades: ${result.grades.map((grade) => `${grade.id} ${grade.pass ? 'pass' : 'fail'}`).join(', ')}`)
  console.log(`summary: ${result.summary.passed}/${result.summary.total} passed (${result.summary.pass_rate})${result.summary.failures.length ? `, failures: ${result.summary.failures.join(', ')}` : ''}`)
  console.log(`pass@1 mean ${result.pass_at_1.mean}; pass@3 mean ${result.pass_at_3.mean}`)
}

const result = await run()

if (mode === 'json') {
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
} else if (mode === 'check') {
  const expected = JSON.parse(await readFile(expectedPath, 'utf8'))
  assert.deepEqual(result, expected)
  printSummary(result)
  console.log('golden samples/quickstart/expected/result.json matches')
  console.log('quickstart ok')
} else {
  printSummary(result)
}
