# @perrylink/dsh-eval-harness

**PUBLIC/SYNTHETIC DEMO — PARTIAL — NOT COUNTED — NOT A VALIDATED PROOFBENCH.**

A small eval-pack lint and deterministic JSON grader for DeepSeek Harness. It does **not** run a real `dsh headless` benchmark, does not include partner failure sessions, and is not a substitute for the commercial SKU-11 Proofbench.

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `eval.pack_lint` | Validate name/version/unique task ids | R0 |
| `eval.grade` | Deterministic JSON equality grade | R0 |

## Install

```sh
dsh plugin --profile <profile> add @perrylink/dsh-eval-harness
```

No customer data, partner session, or validated benchmark claim is included.
