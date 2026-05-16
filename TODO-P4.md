# Doctor link P4 TODO

Issue: #19
Parent tracker: TODO-P3-P5.md
Roadmap: docs/roadmap/p4.md

P4 goal: turn Doctor link from a diagnostic package toolkit into an automated project-level diagnosis pipeline.

## P4.1 Project Diagnostic Strategy

- [ ] Define `.doctorlink/diagnosis.yml`
- [ ] Add project type field
- [ ] Add default command list
- [ ] Add evidence rules
- [ ] Add verification rules
- [ ] Add excluded path rules
- [ ] Add strategy loader
- [ ] Add strategy validation result model
- [ ] Add `doctor-link strategy validate` command
- [ ] Add valid strategy fixture
- [ ] Add invalid strategy fixture
- [ ] Add tests
- [ ] Add docs

## P4.2 Reproduction Script Management

- [ ] Define reproduction entry model
- [ ] Add `.doctorlink/reproduce.yml`
- [ ] Support manual reproduction entry
- [ ] Support command reproduction entry
- [ ] Support test reproduction entry
- [ ] Add reproduction loader
- [ ] Add `doctor-link reproduce list`
- [ ] Add `doctor-link reproduce run <id>`
- [ ] Capture command stdout / stderr / exit code
- [ ] Write reproduction output to diagnostic package evidence
- [ ] Link reproduction output to timeline
- [ ] Add tests
- [ ] Add docs

## P4.3 Test Matrix Automation

- [ ] Extend `.doctorlink/test-matrix.yml` for executable jobs
- [ ] Define test job model
- [ ] Define test job result model
- [ ] Add matrix loader
- [ ] Add `doctor-link test run`
- [ ] Write test outputs to `evidence/test-results/`
- [ ] Record test result into `doctor-report.json`
- [ ] Link test results to verification checklist
- [ ] Add passing job fixture
- [ ] Add failing job fixture
- [ ] Add tests
- [ ] Add docs

## P4.4 Before / After Diagnostic Package Workflow

- [ ] Define diagnosis workflow metadata
- [ ] Add `doctor-link diagnose before`
- [ ] Add `doctor-link diagnose after`
- [ ] Add before package metadata
- [ ] Add after package metadata
- [ ] Link before and after packages
- [ ] Preserve before report path for comparison
- [ ] Add deterministic package naming support
- [ ] Add tests
- [ ] Add docs

## P4.5 Automated Comparison and Verification

- [ ] Add `doctor-link diagnose compare`
- [ ] Add `doctor-link diagnose verify`
- [ ] Run comparison between linked before / after packages
- [ ] Run verification after comparison
- [ ] Generate `pipeline-summary.json`
- [ ] Generate `pipeline-summary.md`
- [ ] Never mark success when evidence is missing
- [ ] Add tests for missing evidence
- [ ] Add tests for candidate verified state
- [ ] Add docs

## P4.6 GitHub Actions and PR Integration

- [ ] Add reusable GitHub Actions example workflow
- [ ] Add PR diagnostic check mode documentation
- [ ] Add artifact upload example
- [ ] Add optional PR comment summary draft
- [ ] Add failed diagnostic pointer to artifact output
- [ ] Add workflow syntax validation in CI if practical
- [ ] Add docs

## P4.7 Project Health Dashboard Foundations

- [ ] Define project health summary model
- [ ] Count diagnostic packages
- [ ] Count unresolved assertions
- [ ] Count failed verifications
- [ ] Count recent regressions
- [ ] Generate `project-health.json`
- [ ] Generate `project-health.md`
- [ ] Add project health panel to local Web UI
- [ ] Add tests
- [ ] Add docs

## P4.8 P4 Quality and Closure

- [ ] Add P4 fixture project
- [ ] Add end-to-end pipeline smoke tests
- [ ] Add broken reproduction scenario
- [ ] Add failed test scenario
- [ ] Add missing evidence scenario
- [ ] Update README.zh-CN.md
- [ ] Update README.en.md
- [ ] Update TODO.md
- [ ] Update TODO-P3-P5.md
- [ ] Add P4 final audit
- [ ] Close Issue #19 after all P4 tasks are complete

## Boundaries

- [ ] Do not publish releases during P4 without explicit authorization.
- [ ] Do not introduce paid cloud services.
- [ ] Do not change Doctor link core positioning.
- [ ] Keep Web UI local-first and read-only by default.
