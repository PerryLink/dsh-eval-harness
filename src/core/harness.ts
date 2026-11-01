export interface EvalTask { id: string; expected?: unknown }
export interface EvalPack { name: string; version: string; tasks: EvalTask[] }
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
