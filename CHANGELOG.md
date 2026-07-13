# Changelog

All notable changes to Doctor link are documented in this file.

Doctor link follows semantic versioning. Public release publishing requires explicit authorization.

## Unreleased

### Fixed

- Reconciled CLI, core runtime, tests, and validation scripts after interface drift.
- Restored `collect`, `verify`, `strategy validate`, Vly proof, workbench JSON, AI result/history, assertion compliance, and risk-review workflows.
- Restored all local E2E, self-validation, P7 runtime, and installed-wheel validation paths.
- Made configured `python` commands portable on systems that only expose the active interpreter by absolute path.

### Added

- Added `doctor-link preflight` for read-only configuration, command, catalog, tool, and environment readiness checks.
- Added clean wheel/sdist content validation, Twine checks, dependency consistency checks, and source-package runtime-artifact exclusions.
- Added cross-platform CI smoke coverage for Linux, macOS, and Windows.

### Security

- Replaced shell-based reproduction and test-matrix execution with a shell-free command-sequence runner.
- Routed adapter and plugin commands through the same shell-free, timeout-aware command runner.
- Added Bandit, dependency audit, Dependabot, immutable release tags, and an 85% coverage gate.

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

- Diagnostic packages no longer hard-code project name `"Doctor link"` when `diagnosis.yml` defines `project`.

## [0.1.1] - 2026-06-29

Post-release documentation alignment and wizard handoff polish.

### Added

- `doctor-link wizard --tool` to select an AI handoff profile without interactive prompts.
- `doctor-link wizard --handoff/--no-handoff` and `--collect-evidence/--no-collect-evidence` for non-interactive runs.
- Wizard interactive prompt for AI tool profile when `--tool` is omitted.

### Changed

- Project status, validation certificates, and README files reflect the published GitHub Release (`v0.1.0-rc.1`, Latest).
- P8 no-code UX roadmap marked largely complete.

## [0.1.2] - Release candidate, not yet published

AI handoff expansion and guided-workflow CLI polish.

### Added

- AI handoff profiles for `grok` (Grok Build), `windsurf` (Windsurf), and `cline` (Cline).
- `doctor-link diagnose-now --tool` to select an AI handoff profile (aligned with `wizard --tool`).
- `doctor-link handoff list` to list supported handoff profiles.
- `doctor-link handoff check` to pre-check compatibility without generating a package.
- `doctor-link handoff generate --json` (and shorthand `doctor-link handoff <package> --json`) for scripted output.

### Changed

- Default handoff tool for guided workflows (`wizard`, `diagnose-now`, `handoff generate`) is now `cursor`.
- CLI reference, diagnose-now guide, and project status docs reflect `v0.1.2` as Latest.

### Fixed

- Restored `doctor_link/core/ai_handoff.py` after a corrupted remote placeholder blocked handoff generation.

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
