# dsh-eval-pack

Public/synthetic eval-pack lint and deterministic JSON grader for DeepSeek Harness.

> **Status: alpha / public-synthetic / partial / not counted / not GA.** No customer evidence, customer data, or production-readiness claim. All acceptance rows are `counted=false`.

> **Renamed:** this project was previously `dsh-eval-harness` / `@perrylink/dsh-eval-harness`. The bare npm name `dsh-eval-harness` is owned by another publisher, so the project is now **`dsh-eval-pack`**. The old scoped package is deprecated and points here.

## Install

```sh
dsh plugin --profile <profile> add dsh-eval-pack
dsh --profile <profile> --dump-config | grep dsh-eval-pack
```

Requires DSH `>=0.2.1-rc.3 <0.3.0` and Node `>=24.9 <25`.

<details>
<summary>中文摘要</summary>

公开/合成 eval-pack lint 与确定性 JSON 评分。 安装：`dsh plugin --profile <profile> add dsh-eval-pack`。公开/合成、alpha、非 GA。

</details>

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `eval.pack_lint` | Validate eval-pack name/version and unique task ids | R0 |
| `eval.grade` | Deterministic JSON equality grade | R0 |

## Input / output

**Input:** an eval pack (JSON) and a candidate JSON answer. **Output:** pack lint findings or a deterministic pass/fail grade. No model is called.

## Limits / non-claims

- Not a validated Proofbench, not a benchmark runner, and not a replacement for SKU-11.
- No partner failure sessions, customer data, or model/provider execution.
- Deterministic JSON equality only; no semantic or LLM judge.
- No customer evidence, customer data, or production-readiness claim; all fixtures are public/synthetic.

## Public sample

Public/synthetic eval packs; `ACCEPTANCE.csv` lists 3 public checks.

## Development

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test && pnpm gate
```

## License

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
