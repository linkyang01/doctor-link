# Changelog

All notable changes to Doctor link are documented in this file.

Doctor link follows semantic versioning. Public release publishing requires explicit authorization.

## Unreleased

### Added

- Safe leading environment assignments such as `PYTHONPATH=src python ...` in configured reproduction and test commands, without invoking a shell.
- Transactional diagnostic-package updates with cross-process locking and atomic file replacement.
- Automatic reproduction and test-matrix evidence recording with stable IDs, assertion links, timeline entries, and rerun replacement.
- Complex regression scenarios for false-success exits, concurrent record writes, assertion inheritance, failed-test blockers, and handoff status accuracy.
- Installed-package full capability lab covering all 61 public command routes across repair, multi-bug, security, integrity, extension, governance, archive, and concurrency scenarios.
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
