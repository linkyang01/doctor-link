# Doctor link Project Status

Status date: 2026-07-13

## Current source development

The post-`v0.2.0` source extends automatic solve to Node.js JavaScript and TypeScript projects while preserving the same approval, branch isolation, protected-input, bounded-round, and independent-verification contract. It detects `package.json` or JavaScript/TypeScript source roots, selects npm, pnpm, Yarn, or Bun from package metadata and lockfiles, and falls back to `node --test` for compatible test files.

New regressions cover real npm execution, one- and multi-round repair, test tampering, package-script and runner-configuration weakening, missing toolchains, and baseline timeouts. The `v0.3.0` local candidate passed 329 tests at 85.39% branch-aware coverage, all build/security/repository validation gates, and the installed-wheel lab across 63 routes, 72 invocations, and ten scenarios. A live Node.js inventory repair changed one production file, converted two failures into three passing tests in one Codex round, and preserved the package and test hashes. Cloud validation, merge, tag, and publication remain pending; see [the detailed validation report](validation/javascript-typescript-solve-validation.md). The published `v0.2.0` evidence below remains historical and unchanged.

## Published automatic-solve release

Version `0.2.0` adds `doctor-link solve`, the first goal-aligned automatic problem-solving path. It supports clean Git-backed Python projects, reproduces the failure before editing, requires explicit `--allow-repair`, creates a dedicated repair branch, invokes Codex in a workspace-write sandbox for up to three rounds, and accepts the repair only after Doctor link independently reruns all required commands. Session prompts, Codex JSONL events, stderr, verification results, protected-input hashes, change receipts, and branch metadata remain local and reviewable.

Local validation passed 319 tests at 85.39% branch-aware coverage. The final clean wheel passed 63/63 public routes through 71 invocations and nine complex scenario invariants. A live disposable Git/Python inventory fixture also completed the full path: Doctor link reproduced three failing assertions, Codex fixed the implementation in one round, and the original independent test command passed all three checks. Adversarial validation now also proves that modifying tests, test configuration, directly referenced verification scripts, or post-check golden files cannot produce ordinary `verified`; the default result is blocked, while explicitly authorized verification-input changes return `review_required`.

The release candidate passed all eight GitHub Actions jobs in PR `#145`, was merged as commit `40a547c`, and was published as [GitHub Release `v0.2.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.2.0) by workflow `29256955705`. PyPI publication was disabled and was not performed.

## Current status

Doctor link has completed P0 through P5.10, has passed P5.10 cloud validation on GitHub Actions, has passed cloud self-validation, has completed P6.1 through P6.11 as planning, schema, specification, conformance, ecosystem asset, and quality-closure documentation, and has completed P7.0 through P7.10 as local runtime implementation and final validation closure.

Post-P7 hardening has also been completed:

- explicit CLI entrypoint registration through `doctor_link.entrypoint:main`;
- archive creation guard to prevent archive output inside the source directory;
- strict integrity verification for untracked files through `--strict`;
- Adapter and Plugin run commands default to dry-run and require `--allow-run` for actual local command execution;
- completed TODO trackers are archived under `docs/archive/completed-todos/`.

Version `0.2.0` passed local and GitHub Actions validation on 2026-07-13: 319 tests, 85.39% branch-aware coverage, Ruff, E2E, self-validation, P7 runtime validation, clean wheel/sdist build, Twine validation, isolated installed-wheel full-capability validation, zero medium/high Bandit findings, and zero known third-party dependency vulnerabilities. GitHub Actions run `29256743976` passed Python 3.10, 3.11, 3.12, security, package install, Ubuntu, macOS, and Windows jobs. The installed-package lab passed all 63 public CLI routes through 71 real invocations and nine complex scenarios. The defined repository release-readiness score remains 100/100 under `docs/validation/local-quality-scorecard.md`. PR `#145` was merged as commit `40a547c`, and [GitHub Release `v0.2.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.2.0) was published on 2026-07-13 by workflow `29256955705`; PyPI was disabled.

All repository-side, non-local, non-release closure work has been completed. Local Mac validation has been recorded in `docs/p5.10-local-validation.md`. Validation on additional target environments (offline workstation, customer delivery, production-like) remains optional when those environments differ from the recorded Mac setup.

P7 was opened as the runtime implementation and real-capability completion phase. P7.10 adds final validation and closure through `scripts/p7_runtime_validate.sh`, CI integration, self-validation integration, final audit documentation, README updates, and project status closure.

P7.1 implemented P1/P1+ evidence hardening for command metadata, environment capture, log ingestion hardening, and evidence integrity indexing.

P7.2 implemented P2/P2+ local workbench product hardening for collapsible sections, local evidence filters, project health panel, verification state visualization, accessibility structure, and controlled CLI-only write-back with backup and audit.

P7.3 implemented P3 AI tool runtime handoff for target tool profiles, compatibility checks, target-specific instructions, file inclusion policy enforcement, missing evidence warnings, privacy warnings, enhanced AI result ingestion, repair session IDs, and multi-round repair session management.

P7.4 implemented P4 operational automation hardening for CI report generation, GitHub Actions markdown summaries, failure triage, regression scoring, test matrix aggregation, project health trend generation, and CI artifact indexing.

P7.5 implemented P5 distribution readiness checks for local dry-run review, artifact checksums, wheel metadata verification, source archive metadata verification, distribution manifest generation, blocking checklist automation, target-environment capture, tests, and documentation.

P7.6 implemented P6 Adapter SDK runtime for adapter manifest loading, schema validation, capability validation, discovery, local execution boundaries, evidence collector / verification / handoff capability interfaces, audit records, CLI commands, tests, and documentation. Post-P7 hardening changed Adapter run behavior to dry-run by default with explicit `--allow-run` execution.

P7.7 implemented P6 Plugin SDK runtime for plugin manifest loading, permission model enforcement, discovery, collector / renderer / handoff / verification extension points, local process boundary, plugin audit log, CLI commands, tests, and documentation. Post-P7 hardening changed Plugin run behavior to dry-run by default with explicit `--allow-run` execution.

P7.8 implemented P6 integrity/signing/privacy runtime gates for local integrity manifests, integrity verification, hash mismatch detection, missing file detection, unsafe path detection, unsigned manifest warnings, privacy policy loading, privacy scanning, redaction gates, export safety gates, tests, and documentation. Post-P7 hardening added strict untracked-file detection. Real signing and key management remain intentionally out of scope unless explicitly authorized later.

P7.9 implemented P6 local knowledge base and enterprise archive runtime for local diagnostic knowledge indexing, recurring failure signature extraction, repair outcome aggregation, project health trend aggregation, knowledge export, archive metadata records, retention policy checks, audit trail append behavior, local archive export, CLI commands, tests, and documentation. Post-P7 hardening blocks archive output directories inside the source directory.

P7.10 implements final validation and closure through P7 runtime E2E validation, CI coverage, self-validation coverage, final audit, README updates, and TODO closure.

P6 and P7 are complete as repository-side local-first implementation work. Version `0.2.0` is locally validated, cloud validated, merged, tagged, and published on GitHub. This does not mean Doctor link has implemented a hosted platform, account system, marketplace, real signing, hosted archive, hosted knowledge base, or PyPI distribution.

## Validation certification status

- [x] Current implementation cloud CI revalidated (PR #145, run 29256743976)
- [x] Local Release Candidate validation passed (2026-07-13)
- [x] First public GitHub Release (`v0.1.0-rc.1`, 2026-06-29)
- [x] GitHub Release `v0.1.1` (2026-06-29)
- [x] GitHub Release `v0.1.2` published (2026-07-13)
- [x] GitHub Release `v0.1.3` published (2026-07-13, workflow 29246045227)
- [x] GitHub Release `v0.2.0` published (2026-07-13, workflow 29256955705)
- [x] Local Mac Validation Recorded (2026-06-29)
- [x] GitHub-hosted Linux, macOS, and Windows validation
- [x] Cross-platform CI jobs configured for Linux, macOS, and Windows
- [x] Release tag published (`v0.1.0-rc.1`)
- [ ] PyPI publication performed (optional; GitHub wheel is the primary install path)

Certification documents:

- `docs/validation/cloud-validation-certificate.md`
- `docs/validation/release-candidate-checklist.md`
- `docs/validation/validation-evidence-index.md`
- `docs/validation/local-validation-pending.md`

## Phase status

- [x] P0: Diagnostic Foundation
- [x] P1: Evidence Collection Primitives
- [x] P1+: CLI Evidence Pipeline
- [x] P2: Local Read-only Diagnostic Workbench
- [x] P2+: Mainline Diagnostic Workbench Enhancements
- [x] P3: AI Coding Collaboration Layer
- [x] P4: Automated Diagnosis Pipeline
- [x] P5: Productization and Release Readiness
- [x] P5.9: Release Hardening and Usability Validation
- [x] P5.10: Cloud Validation on GitHub Actions
- [x] Self Validation: Doctor link validates itself on GitHub Actions
- [x] P5.10: Local Mac validation (2026-06-29)
- [x] P6.1: Diagnostic Package Schema v1
- [x] P6.2: Compatibility and Conformance Test Suite
- [x] P6.3: Adapter SDK Planning Specification
- [x] P6.4: Plugin SDK Planning Specification
- [x] P6.5: Third-party AI Coding Integration Specification
- [x] P6.6: Diagnostic Package Signing and Integrity Specification
- [x] P6.7: Privacy and Security Level Specification
- [x] P6.8: Enterprise Archive and Governance Model
- [x] P6.9: Cross-project Diagnostic Knowledge Base
- [x] P6.10: Public Ecosystem Assets
- [x] P6.11: P6 Quality and Closure
- [x] Final non-local closure audit
- [x] P7.0: Real-capability gap audit and implementation map
- [x] P7.1: P1/P1+ evidence hardening
- [x] P7.2: P2/P2+ local workbench product hardening
- [x] P7.3: P3 AI tool runtime handoff implementation
- [x] P7.4: P4 operational automation hardening
- [x] P7.5: P5 distribution readiness checks
- [x] P7.6: P6 Adapter SDK runtime
- [x] P7.7: P6 Plugin SDK runtime
- [x] P7.8: P6 integrity/signing/privacy runtime gates
- [x] P7.9: P6 local knowledge base and enterprise archive runtime
- [x] P7.10: P7 final validation and closure
- [x] Post-P7 hardening: repository cleanup and acceptance review readiness
