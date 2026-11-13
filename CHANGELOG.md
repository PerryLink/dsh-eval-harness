# Changelog

## [0.2.0] — 2026-11-13

### Breaking

- **Tool names no longer contain a dot.** The provider validates `tools[].name`
  against `^[a-zA-Z0-9_-]+$`; the 0.1.x names joined `eval` and the verb with a
  dot, so the provider rejected the whole `tools` array with
  `Invalid 'tools[N].name'` — the plugin registered, but no request carrying its
  tools could succeed. Rename on upgrade:

  | 0.1.x (two parts, dot) | 0.2.0 |
  |---|---|
  | `eval` + `pack_lint` | `eval_pack_lint` |
  | `eval` + `grade` | `eval_grade` |
  | `eval` + `summary` | `eval_summary` |
  | `eval` + `pass_at_k` | `eval_pass_at_k` |

- No aliases: the dotted names are gone, so prompts, scripts and permission
  rules must move to the underscore names from 0.1.x to 0.2.0. Nothing else
  changes — arguments, results and error codes are identical.
- Minor bump rather than a patch, per the compatibility promise that tool names
  are a stable API and breaking changes require a minor bump.

### Added

- Regression test `test/tool-name-wire.test.mjs`: every registered tool name
  must match `^[a-zA-Z0-9_-]+$`, contain no dot, keep the `eval_` namespace and
  be unique — so a dotted name can never ship again.

### Changed

- READMEs (five languages), `TROUBLESHOOTING.md`, the quickstart sample, the
  acceptance suite, the diagrams and their generator all use the underscore
  names, and the READMEs state the wire-name rule. Earlier entries here use the
  new spelling too, so a repository-wide search no longer finds dotted names.

## [0.1.0] — 2026-11-03

### Stable

- First non-alpha release: tool names and the CLI surface are covered by a
  compatibility promise (breaking changes require a minor bump).
- Ships a quickstart sample, a one-line prompt, a permission block and real captures.

## [0.1.0-alpha.12] — 2026-11-01

### Security / Fixes

- Release configuration hardening: wider host peer range and a build step before publish.


### Added

- `eval_pass_at_k`: unbiased pass@k estimator `1 - C(n-c,k)/C(n,k)` with exact binomials, plus the per-task and mean values. Verified by `node --test test/*.test.mjs` (12/12).

## [0.1.0] — 2026-11-01

### Added

- `eval_summary`: aggregate pass count, pass rate and failing task ids for a graded run, using the same grader as `eval_grade`.
- Canonical-JSON grading: object key order no longer changes the verdict; array order still matters.

Verified by `node --test test/*.test.mjs` (7/7).

## [0.1.0-alpha.7] — 2026-11-01

### Changed

- Documentation: five-language fixture/acceptance links now resolve on npm; added specific related-checker/tool links.
- Marketplace metadata: taxonomy category, archetype, domains and status; docs page now shows the same.
- Added a real terminal hero (and GIF for the active docs set) plus `TROUBLESHOOTING.md`.

All notable changes to `dsh-eval-pack` are documented here. The format follows Keep a Changelog; this project uses alpha versions.

## [0.1.0-alpha.6] — 2026-11-01

### Added

- Five-language READMEs: English, 简体中文, Español, Português, हिन्दी.
- Local workflow SVG at `docs/assets/dsh-eval-pack-flow.svg`.
- Family cross-links (domain index, checker family, `dsh-kit`), compatibility, permissions, and related-work sections.
- Standard repository files: `SECURITY.md`, `PRIVACY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `icon.svg`.

### Changed

- README aligned with the PerryLink DSH checker/plugin family style; package remains public/synthetic, alpha, not GA.

## [Earlier]

Earlier alpha builds are available from npm and GitHub Releases; this file starts at the family-standard documentation wave.
