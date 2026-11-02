export interface EvalTask { id: string; expected?: unknown }
export interface EvalPack { name: string; version: string; tasks: EvalTask[] }
export type EvalErrorCode =
  | 'E_PACK_NOT_OBJECT'
  | 'E_PACK_NAME'
  | 'E_PACK_VERSION'
  | 'E_PACK_TASKS_EMPTY'
  | 'E_TASK_ID'
  | 'E_TASK_DUPLICATE'
  | 'E_EVAL_SAMPLES'
  | 'E_EVAL_CORRECT'
  | 'E_EVAL_K'
/**
 * Human-facing wording for every code this package can surface.
 * Renderer: `<一句人话>（E_CODE）｜下一步：<一个动作>` (Package Standard v1 §4).
 */
const EVAL_HUMAN: Record<EvalErrorCode, { text: string; next: string }> = {
  E_PACK_NOT_OBJECT: { text: '这不是一个评测包对象，读不出名称、版本和任务', next: '传一个包含 name / version / tasks 的 JSON 对象' },
  E_PACK_NAME: { text: '评测包缺少名称', next: '给评测包加一个非空的 name 再跑 lint' },
  E_PACK_VERSION: { text: '评测包缺少版本号', next: '给评测包加一个非空的 version（例如 "1.0.0"）' },
  E_PACK_TASKS_EMPTY: { text: '评测包里一个任务都没有', next: '往 tasks 里至少放一个带 id 的任务' },
  E_TASK_ID: { text: '有一个任务没有 id', next: '给每个任务补一个非空且唯一的 id' },
  E_TASK_DUPLICATE: { text: '评测包里有重复的任务 id', next: '把重复的 id 改成唯一值再跑 lint' },
  E_EVAL_SAMPLES: { text: '采样数必须是正整数', next: '把 samples 改成 ≥1 的整数' },
  E_EVAL_CORRECT: { text: '正确的样本数超过了采样数', next: '确认 correct ≤ samples 再算 pass@k' },
  E_EVAL_K: { text: 'k 超过了采样数', next: '把 k 改成 1 到 samples 之间的整数' },
}
export function evalErrorMessage(code: EvalErrorCode): string {
  const human = EVAL_HUMAN[code]
  return `${human.text}（${code}）｜下一步：${human.next}`
}
export function lintPack(input: unknown): string[] {
  const errors: string[] = []
  if (!input || typeof input !== 'object') return ['E_PACK_NOT_OBJECT']
  const pack = input as Partial<EvalPack>
  if (!pack.name || typeof pack.name !== 'string') errors.push('E_PACK_NAME')
  if (!pack.version || typeof pack.version !== 'string') errors.push('E_PACK_VERSION')
  if (!Array.isArray(pack.tasks) || pack.tasks.length === 0) errors.push('E_PACK_TASKS_EMPTY')
  else {
    const ids = new Set<string>()
    for (const task of pack.tasks) {
      if (!task || typeof task.id !== 'string' || !task.id) { errors.push('E_TASK_ID'); continue }
      if (ids.has(task.id)) errors.push(`E_TASK_DUPLICATE:${task.id}`)
      ids.add(task.id)
    }
  }
  return errors
}
/** Stable serialisation: object keys sorted at every level, arrays kept in order. */
export function canonical(value: unknown): string {
  const walk = (input: unknown): unknown => {
    if (Array.isArray(input)) return input.map(walk)
    if (input && typeof input === 'object') {
      const out: Record<string, unknown> = {}
      for (const key of Object.keys(input as Record<string, unknown>).sort()) out[key] = walk((input as Record<string, unknown>)[key])
      return out
    }
    return input
  }
  return JSON.stringify(walk(value))
}
export function grade(actual: unknown, expected: unknown): boolean {
  return canonical(actual) === canonical(expected)
}
export interface EvalResult { id: string; actual: unknown; expected: unknown }
export interface EvalSummary {
  total: number
  passed: number
  failed: number
  pass_rate: number
  failures: string[]
}
export function summarize(results: EvalResult[]): EvalSummary {
  const failures: string[] = []
  let passed = 0
  for (const r of results) {
    if (grade(r.actual, r.expected)) passed += 1
    else failures.push(r.id)
  }
  const total = results.length
  return { total, passed, failed: total - passed, pass_rate: total ? Math.round((passed / total) * 1e6) / 1e6 : 0, failures }
}

function comb(n: number, k: number): bigint {
  if (k < 0 || k > n) return 0n
  let result = 1n
  for (let i = 1n; i <= BigInt(k); i += 1n) result = (result * (BigInt(n) - BigInt(k) + i)) / i
  return result
}
export interface PassAtKInput { task_id: string; samples: number; correct: number }
export interface PassAtKResult { task_id: string; k: number; n: number; c: number; pass_at_k: number }
/**
 * Unbiased pass@k estimator: 1 - C(n-c, k) / C(n, k).
 * Clean-room from the published estimator definition; exact binomials via BigInt.
 */
export function passAtK(task: PassAtKInput, k: number): PassAtKResult {
  const { samples, correct } = task
  if (!Number.isInteger(samples) || samples < 1) throw new Error(evalErrorMessage('E_EVAL_SAMPLES'))
  if (!Number.isInteger(correct) || correct < 0 || correct > samples) throw new Error(evalErrorMessage('E_EVAL_CORRECT'))
  if (!Number.isInteger(k) || k < 1 || k > samples) throw new Error(evalErrorMessage('E_EVAL_K'))
  const denominator = comb(samples, k)
  const numerator = comb(samples - correct, k)
  const value = 1 - Number(numerator) / Number(denominator)
  return { task_id: task.task_id, k, n: samples, c: correct, pass_at_k: Math.round(value * 1e6) / 1e6 }
}
export function passAtKMean(tasks: PassAtKInput[], k: number): { k: number; tasks: PassAtKResult[]; mean: number } {
  const results = tasks.map((t) => passAtK(t, k))
  const mean = results.length ? Math.round((results.reduce((sum, r) => sum + r.pass_at_k, 0) / results.length) * 1e6) / 1e6 : 0
  return { k, tasks: results, mean }
}
