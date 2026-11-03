# Changelog

## [0.1.0] — 2026-11-03

### Stable

- First non-alpha release: tool names and the CLI surface are covered by a
  compatibility promise (breaking changes require a minor bump).
- Ships a quickstart sample, a one-line prompt, a permission block and real captures.

## [0.1.0-alpha.12] — 2026-11-01

### Security / Fixes

- Release configuration hardening: wider host peer range and a build step before publish.


### Added

- `eval.pass_at_k`: unbiased pass@k estimator `1 - C(n-c,k)/C(n,k)` with exact binomials, plus the per-task and mean values. Verified by `node --test test/*.test.mjs` (12/12).

## [0.1.0] — 2026-11-01

### Added

- `eval.summary`: aggregate pass count, pass rate and failing task ids for a graded run, using the same grader as `eval.grade`.
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
