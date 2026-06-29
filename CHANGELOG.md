# Changelog

All notable changes to Doctor link are documented in this file.

Doctor link follows semantic versioning. Public release publishing requires explicit authorization.

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

## Unreleased

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