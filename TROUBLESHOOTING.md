# Troubleshooting — dsh-eval-pack

每条按「症状 / 原因 / 动作」写。报错原文都是 `<一句人话>（E_XXX）｜下一步：<动作>`，
把 `E_XXX` 和这句话一起发到 issue 即可定位；不要把客户评测数据贴进 issue。

## 1. 评测包本身不合格（E_PACK_TASKS_EMPTY / E_TASK_DUPLICATE / E_PACK_NAME）

- **症状**：`评测包里一个任务都没有（E_PACK_TASKS_EMPTY）｜下一步：往 tasks 里至少放一个带 id 的任务`
- **原因**：`pack.json` 缺少 `name` / `version`，或 `tasks` 为空、任务 id 重复。
- **动作**：先跑 `eval_pack_lint`；按返回的错误码补齐字段、把重复 id 改成唯一值，再评分。

## 2. 正确样本数超过采样数（E_EVAL_CORRECT）

- **症状**：`正确的样本数超过了采样数（E_EVAL_CORRECT）｜下一步：确认 correct ≤ samples 再算 pass@k`
- **原因**：`sampling[]` 里 `correct` 填得比 `samples` 大，通常是两次运行的计数拼错了。
- **动作**：确认每个任务的 `samples` 和 `correct` 来自同一次运行；`correct` 最多等于 `samples`。

## 3. k 超过采样数（E_EVAL_K）

- **症状**：`k 超过了采样数（E_EVAL_K）｜下一步：把 k 改成 1 到 samples 之间的整数`
- **原因**：拿 10 次采样的数据去算 pass@20，估计量没有定义。
- **动作**：把 `k` 改成不超过该任务 `samples` 的整数；不同任务采样数不同时，先取最小值再统一 `k`。

## Install or activation fails

- DSH must satisfy `>=0.2.1-rc.3 <0.4.0`; Node must be `>=24.9 <25`.
- Run `dsh --version` and `node --version`, then retry with a fresh `DSH_HOME`:

```sh
export DSH_HOME="$(mktemp -d)"
dsh plugin --profile <profile> add dsh-eval-pack
dsh --profile <profile> --dump-config | grep dsh-eval-pack
```

## The tool cannot find an input

- All paths are local. Pass the pack, case and run JSON as arguments; the shipped quickstart lives in `samples/quickstart/`.
- Supported material: eval-pack JSON, per-case sample JSON and one run-result JSON.

## Parse or encoding failures

- All inputs must be UTF-8 JSON; remove a UTF-8 BOM if the parser rejects the first key.
- Check the pack name/version and unique task ids; grading is deterministic JSON equality, not a benchmark.

## Permission or write failures

- All four tools are read-only (`R0`); they do not write files.
- For tests, run against the shipped synthetic sample; no `DSH_HOME` writes are involved.

## The result looks wrong

- Check the tool boundary in the README first. These are public/synthetic alpha tools, not a production or customer-validated benchmark.
- Compare the reported task ids with the input tasks; the output is deliberately explicit about which case failed.

## Run the tests

```sh
pnpm install --frozen-lockfile
pnpm test
```

## Report

Open an issue on <https://github.com/PerryLink/dsh-eval-pack/issues> with the package version, a minimal synthetic input, and the exact tool call. Do not attach customer data.
