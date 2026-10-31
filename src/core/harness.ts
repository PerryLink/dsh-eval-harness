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
export function grade(actual: unknown, expected: unknown): boolean {
  return JSON.stringify(actual) === JSON.stringify(expected)
}
