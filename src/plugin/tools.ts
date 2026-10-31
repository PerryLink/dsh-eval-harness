import { defineTool } from '@deepseek-ai/dsh-tools'
import { grade, lintPack } from '../core/harness.js'
const text = (t: string) => [{ type: 'text' as const, text: t }]
export function createTools() {
  const lint = defineTool({
    name: 'eval.pack_lint',
    description: 'Lint a public/synthetic eval-pack object: name, version, non-empty unique task ids. Read-only; no runner.',
    parameters: { pack: { type: 'object', additionalProperties: true, required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { errors: { type: 'array', items: { type: 'string' }, required: true }, ok: { type: 'boolean', required: true } } }, render: (_a, v) => text(`pack ok=${v.ok}`) },
    async execute(args) { const errors = lintPack(args.pack); return { errors, ok: errors.length === 0 } },
  })
  const gradeTool = defineTool({
    name: 'eval.grade',
    description: 'Deterministic JSON equality grade for one public/synthetic task. Read-only.',
    parameters: { actual: { type: 'json', required: true }, expected: { type: 'json', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { pass: { type: 'boolean', required: true } } }, render: (_a, v) => text(`grade ${v.pass ? 'pass' : 'fail'}`) },
    async execute(args) { return { pass: grade(args.actual, args.expected) } },
  })
  return [lint, gradeTool]
}
