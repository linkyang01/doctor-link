# Changelog

All notable changes to Doctor link are documented in this file.

Doctor link follows semantic versioning. Public release publishing requires explicit authorization.

## Unreleased

### Fixed

- `assist` / reproduction suggestion no longer treats pytest collection and environment setup failures (non-test exit codes) as successful reproduction.
- Common English stop words such as `not` and `set` are excluded from problem-term matching so unrelated test files are less likely to be selected.
- `solve` preview and `assist` no longer require a clean Git working tree; dirty trees still block only `--allow-repair`.
- `solve --tool` validation no longer uses `click.Choice`, avoiding breakage on some pre-release click builds in polluted environments.

### Changed

- Click is constrained to `>=8.1.7,<9`.
- Guided HTML results include exit codes, selected reproduction command, short evidence snippets, and advisory root-cause hints.
- Automatic solve repair prompts include an advisory "Suspected root cause" section when failing evidence can be clustered.

### Added

- Authoritative post-v0.5.1 maintenance roadmap, support and security routes, compatibility/deprecation policy, issue templates, scheduled PyPI smoke workflow, and a pinned public-project preflight validation harness (Issue #156).
- `doctor-link explain` clusters failing check output into advisory source-file root-cause hints without editing code (Issue #159).

## [0.5.1] - 2026-07-14

Distribution and public-documentation consistency patch.

### Changed

- PyPI and `pipx` are now the primary public installation path, with the immutable GitHub Release retained as a fallback.
- README, bilingual entrypoints, installation guidance, project status, and release evidence consistently describe the published v0.5 feature set and current support boundary.
- PyPI publication uses a dedicated Trusted Publishing workflow with a protected GitHub environment, short-lived OIDC credentials, and digital attestations instead of a stored API token.

### Validation

- 365 automated tests pass locally before release preparation.
- A clean `pipx install doctor-link==0.5.0` from PyPI returned the expected version and passed preflight with zero blockers and zero warnings.
- The v0.5.1 release must repeat the Python 3.10-3.14, cross-platform, security, package, installed-wheel, GitHub Release, PyPI, and clean pipx gates.

## [0.3.0] - 2026-07-14

Verified automatic repair for Node.js JavaScript and TypeScript projects.

### Added

- JavaScript/TypeScript project detection from `package.json` and common source roots.
- Automatic npm, pnpm, Yarn, and Bun test selection from `packageManager` and lockfiles, with `node --test` fallback for compatible test files.
- Cross-platform package-manager resolution binds Windows npm, pnpm, Yarn, Bun, and Corepack launchers to their concrete executable paths before safe subprocess execution.
- Real npm integration regressions for one- and multi-round repairs, package-script weakening, and test-contract tampering.

### Changed

- Automatic solve now supports both Python and Node.js JavaScript/TypeScript projects while retaining the same explicit approval, isolated branch, three-round limit, and independent acceptance contract.
- Verification-input protection now covers package manifests, lockfiles, workspace files, TypeScript/JavaScript configuration, and common Jest, Vitest, Playwright, and Cypress configuration files.
- Project checks run with non-interactive `CI=1` and `NO_COLOR=1` environment defaults.
- Supported-runtime validation expands through Python 3.13 and 3.14.
- The primary quick start now begins with guided diagnosis or verified repair on the user's own project instead of an internal-format demonstration.

### Security

- Missing required verification executables and timed-out baseline checks block before branch creation or Codex invocation.
- Generated dependency, build, coverage, and cache directories are pruned from protected-input discovery without weakening source test protection.
- Command evidence preserves invalid UTF-8 safely, and empty commands, permission failures, and other operating-system launch errors return structured results instead of crashing diagnostics.

### Validation

- 339 automated tests pass locally with 85.48% branch-aware coverage and the enforced 85% floor.
- The installed-wheel full-capability lab covers all 63 CLI routes through 72 real invocations and ten complex scenario invariants, including a JavaScript/npm approval-gate scenario.
- A disposable Node.js inventory project completed a live Codex repair: two failing acceptance cases became three passing tests in one round while the package manifest and original test hashes remained unchanged.
- GitHub Actions run `29263187097` passed all ten Python 3.10-3.14, security, package, Ubuntu, macOS, and Windows jobs for code commit `c9426e7`.
- Release workflow `29299367180` rebuilt, installed, and validated the distributions before publishing GitHub Release `v0.3.0` from merge commit `e0224cc`; PyPI publication was disabled.

## [0.2.0] - 2026-07-13

Verified automatic problem-solving release with bounded Codex repair, independent regression acceptance, and protected verification inputs.

### Added

- `doctor-link solve` for an end-to-end Python-project loop: reproduce a concrete failure, preview the bounded Codex task, require explicit repair approval, create an isolated Git branch, run up to three Codex repair rounds, and independently verify every required command.
- Local solve-session receipts containing prompts, Codex JSONL events, stderr, per-round verification results, final status, branch metadata, and rollback guidance.
- Automatic command discovery from `.doctorlink/reproduce.yml`, `.doctorlink/test-matrix.yml`, or a `python -m pytest` fallback.
- Complex automatic-solve regressions for approval gating, non-reproduction, dirty-worktree protection, unsafe commands, one- and multi-round success, exhausted rounds, and Codex sandbox arguments.

### Changed

- Product positioning now makes verified problem resolution the user-facing goal while retaining the diagnostic context layer as its evidence foundation.
- Shell-free command execution accepts internal environment overrides so automatic checks can prevent Python bytecode artifacts from dirtying a clean repository.
- Automatic solve snapshots tests, test configuration, configured catalogs, and directly referenced verification scripts before repair; protected-input changes now block ordinary verification.
- Explicit `--allow-verification-changes` uses the distinct `review_required` status and exit code 6, so intentionally changed acceptance inputs cannot be confused with `verified`.

### Security

- Automatic repair refuses dirty or non-Git workspaces, requires `--allow-repair`, uses `codex exec --sandbox workspace-write --json`, never bypasses the Codex sandbox, and does not auto-commit, push, or publish.
- A repair provider can no longer obtain `verified` by deleting or weakening protected tests and verification configuration; per-round hashes and structured change receipts preserve the original acceptance contract.

### Validation

- 319 automated tests passed with 85.39% branch-aware coverage and the enforced 85% floor.
- The final clean wheel passed all 63 public routes through 71 real invocations and nine complex scenario invariants.
- A disposable Git/Python inventory project completed a live Codex repair: three baseline failures became three passing tests in one round, and Doctor link returned `verified` from its independent rerun.
- Ruff, Bandit, dependency vulnerability audit, wheel/sdist build, distribution-content validation, and Twine validation passed.

## [0.1.3] - 2026-07-13

Reliability, evidence integrity, privacy-safe package export, installed-wheel full-capability validation, and platform-integration planning release.

### Added

- Safe leading environment assignments such as `PYTHONPATH=src python ...` in configured reproduction and test commands, without invoking a shell.
- Transactional diagnostic-package updates with cross-process locking and atomic file replacement.
- Automatic reproduction and test-matrix evidence recording with stable IDs, assertion links, timeline entries, and rerun replacement.
- Complex regression scenarios for false-success exits, concurrent record writes, assertion inheritance, failed-test blockers, and handoff status accuracy.
- Installed-package full capability lab covering all 62 public command routes across repair, migration, multi-bug, security, integrity, extension, governance, archive, and concurrency scenarios.
- Versioned package-export manifest schema and automatic CLI inventory enforcement.

### Changed

- `reproduce run`, required `test run` jobs, `verify`, and `diagnose verify` now return non-zero when their machine-readable result is unsuccessful.
- After-state packages inherit before-state user assertions and investigation boundaries.
- Before/after comparison resolves an assertion only when a linked after-state test record passes; a missing assertion is not proof of resolution.
- Verification includes failed, partial, and unknown test records in blockers and rerun instructions, while replacing stale verification commands on later runs.
- Handoff compatibility distinguishes `needs_repair`, `needs_evidence`, `ready_for_verification_review`, and `ready`, and exposes the current verification status.
- The six-bug shop-service example now creates the package before running checks, attaches all automated evidence, and validates the expected unresolved status.
- GitHub Actions now executes the full capability lab against the cleanly installed wheel and uploads its per-command evidence.

### Fixed

- Prevented concurrent CLI processes from silently overwriting each other's package updates.
- Prevented stale comparison and verification sections from accumulating and incorrectly implying `candidate_verified`.
- Prevented failed reproductions and required test jobs from printing failure JSON while returning shell exit code 0.
- Repaired `doctor-package --include-web` and exposed the documented attachment/log/screenshot/size filters.
- Prevented package export manifests from being misclassified as AI handoff manifests during Schema and Conformance validation.
- Made `doctor-package` run the privacy export gate by default, with an explicit audited `--allow-unsafe-export` override.
- Removed absolute local paths from archived export manifests and package README files.
- Added `schema migrate` to convert legacy export-shaped `manifest.json` files while preserving backups and refusing formal manifests.
- Made zip export atomic with destination-capacity preflight so interruptions and low-disk failures preserve the previous complete archive.
- Added large-file-count, command-timeout, interrupted-export, retry, and insufficient-disk regression coverage.

### Validation

- 298 automated tests passed with 85.25% branch-aware coverage and an enforced 85% minimum.
- All 62 public routes passed through 70 real installed-package command invocations and eight complex scenario invariants.
- Python 3.10, 3.11, and 3.12 passed.
- Ubuntu, macOS, and Windows smoke jobs passed.
- Ruff, Bandit, pip-audit, distribution-content validation, Twine, and isolated wheel installation passed.

## [0.1.2] - 2026-07-13

Release-readiness repair, security hardening, distribution validation, cross-platform CI, and GitHub documentation expansion.

### Added

- AI handoff profiles for `grok`, `windsurf`, and `cline`.
- `doctor-link diagnose-now --tool` and aligned guided-workflow tool selection.
- `doctor-link handoff list`, compatibility checks, and JSON generation output.
- Read-only `doctor-link preflight` checks for configuration, commands, catalogs, tools, and Python readiness.
- Safe shell-free configured-command sequence runner with portable Python resolution.
- Wheel and source-distribution content validation, Twine validation, and isolated installed-wheel checks.
- Bandit, dependency audit, Dependabot, immutable release-tag checks, and an 85% branch-coverage gate.
- GitHub Actions jobs for Python 3.10–3.12 and Ubuntu, macOS, and Windows smoke validation.
- Security policy, GitHub repository guide, pull-request template, improved diagnostic issue form, and detailed validation evidence.

### Changed

- Default guided handoff tool is `cursor`.
- Config-relative evidence paths are resolved from the configured project root.
- Adapter and plugin command execution uses the shared audited command runner.
- Release, manual-validation, self-validation, and CI workflows enforce aligned package, security, and validation gates.
- README, installation, contribution, security, validation, and release documents reflect the real `v0.1.2` scope and publication boundary.

### Fixed

- Reconciled CLI and runtime interface drift affecting collect, verify, strategy validation, comparison, Vly proof, workbench JSON, AI result/history, assertion compliance, and risk review.
- Repaired AI handoff manifest/file reconciliation and task generation interfaces.
- Restored all local E2E, self-validation, P7 runtime, project validation, and installed-wheel paths.
- Handled invalid YAML and missing optional catalogs without uncontrolled tracebacks.
- Made configured `python` commands work on systems without a global `python` alias.
- Removed generated reports and cache content from source distributions.

### Security

- Replaced shell-based reproduction and test-matrix execution with argument-vector execution that rejects unsafe operators.
- Kept adapter and plugin execution dry-run by default and gated real execution behind explicit `--allow-run` approval.
- Added medium/high-confidence source scanning and dependency-vulnerability auditing to CI.
- Preserved local-first evidence, redaction, integrity, privacy scan, and export-gate boundaries.

### Validation

- 273 automated tests passed.
- Branch-aware coverage reached 85.09% with an enforced 85% floor.
- Python 3.10, 3.11, and 3.12 passed.
- Ubuntu, macOS, and Windows smoke jobs passed.
- Security, package build/install, E2E, self-validation, project validation, and P7 runtime checks passed.
- GitHub Actions certification run: `29221918410`.

## [0.1.1] - 2026-06-29

Post-release documentation alignment and wizard handoff polish.

### Added

- `doctor-link wizard --tool` to select an AI handoff profile without interactive prompts.
- `doctor-link wizard --handoff/--no-handoff` and `--collect-evidence/--no-collect-evidence` for non-interactive runs.
- Wizard interactive prompt for AI tool profile when `--tool` is omitted.

### Changed

- Project status, validation certificates, and README files reflect the published GitHub Release (`v0.1.0-rc.1`).
- P8 no-code UX roadmap marked largely complete.

## [0.1.0-rc.1] - 2026-06-29

Release candidate for the local-first diagnostic CLI and AI collaboration workflow.

### Added

- `doctor-link wizard` interactive guided diagnosis workflow.
- `doctor-link home` local static homepage for recent diagnostic packages.
- `doctor-link diagnose-now --full` and `--handoff` for one-command diagnosis pipelines.
- Friendly Python version and path error helpers.
- `.gitignore` for local artifacts and virtual environments.
- Adapter registry with unified `VlyAdapter` facade over Core Proof logic.
- Examples: `python-api-bug`, `media-playback-library`.
- No-code quick start guides in English and Chinese under `docs/guides/`.
- Release notes at `docs/validation/v0.1.0-rc.1-release-notes.md`.

### Changed

- `report` reads `.doctorlink/diagnosis.yml` project metadata and boundaries.
- `verify` CLI lists missing evidence items and next commands.
- `assertion-check` supports `--json` output.
- `diagnose-now` recommendations are project-type aware.
- `problem_map_builder` and `verification_builder` are wired into package generation.
- `reproduce.yml` accepts YAML list commands and `reproduction_id` aliases.
- Project status moves to Release Candidate Ready with expanded Phase A/B closure.

### Fixed

- Diagnostic packages no longer hard-code project name `Doctor link` when `diagnosis.yml` defines `project`.

## Historical development backlog

### Added

- P0 diagnostic foundation.
- P1 evidence collection primitives.
- P1+ CLI evidence pipeline.
- P2 local read-only diagnostic workbench.
- P2+ diagnostic workbench enhancements.
- P3 AI Coding collaboration layer.
- P4 automated diagnosis pipeline.
- P5 release policy and productization planning.
- P6/P7 local runtime, adapter/plugin SDK, integrity gates, and validation closure.

### Security

- Release preparation preserves local-first and explicit-redaction boundaries.
