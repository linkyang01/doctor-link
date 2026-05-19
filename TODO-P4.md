# Doctor link P4 TODO

Issue: #19
Parent tracker: TODO-P3-P5.md
Roadmap: docs/roadmap/p3-p5.md

P4 goal: turn Doctor link from a manual diagnostic toolkit into an automated project-level diagnosis pipeline.

## Execution batches

P4 should be implemented in small CI-safe PRs:

1. P4.1 Strategy foundation
2. P4.2 Reproduction management
3. P4.3 Test matrix automation
4. P4.4 Before / after package workflow
5. P4.5 Automated comparison and verification
6. P4.6 GitHub Actions and PR integration docs
7. P4.7 Project health summary
8. P4.8 P4 quality and closure

## P4.1 Strategy foundation

- [x] Define `.doctorlink/diagnosis.yml`
- [x] Add strategy loader
- [x] Add strategy validation result model
- [x] Support project type
- [x] Support default commands
- [x] Support evidence rules
- [x] Support verification rules
- [x] Support excluded paths
- [x] Add `doctor-link strategy validate` command
- [x] Add unit tests
- [x] Add CLI tests
- [x] Update docs

## P4.2 Reproduction management

- [x] Define reproduction metadata model
- [x] Add `.doctorlink/reproduce.yml` example
- [x] Support manual reproduction entries
- [x] Support command reproduction entries
- [x] Support test reproduction entries
- [x] Add `doctor-link reproduce list`
- [x] Add `doctor-link reproduce run <id>`
- [x] Capture reproduction output into diagnostic evidence
- [x] Add tests
- [x] Update docs

## P4.3 Test matrix automation

- [x] Extend `.doctorlink/test-matrix.yml` for executable jobs
- [x] Define test job status model
- [x] Add `doctor-link test run`
- [x] Capture outputs into `evidence/test-results/`
- [x] Link test results to verification checklist where possible
- [x] Add tests
- [x] Update docs

## P4.4 Before / after package workflow

- [x] Define before / after workflow metadata
- [x] Add `doctor-link diagnose before`
- [x] Add `doctor-link diagnose after`
- [x] Ensure packages are linkable by metadata
- [x] Preserve before report path for comparison
- [x] Add tests
- [x] Update docs

## P4.5 Automated comparison and verification

- [ ] Add `doctor-link diagnose compare`
- [ ] Add `doctor-link diagnose verify`
- [ ] Generate pipeline summary report
- [ ] Do not mark success when verification evidence is missing
- [ ] Add tests
- [ ] Update docs

## P4.6 GitHub Actions and PR integration docs

- [ ] Add reusable workflow example
- [ ] Add PR diagnostic check mode documentation
- [ ] Document artifact upload pattern
- [ ] Document optional PR comment summary
- [ ] Add workflow syntax check if feasible
- [ ] Update docs

## P4.7 Project health summary

- [ ] Define project health model
- [ ] Count diagnostic packages
- [ ] Count unresolved assertions
- [ ] Count failed or missing verifications
- [ ] Count recent regressions
- [ ] Generate `project-health.json`
- [ ] Generate `project-health.md`
- [ ] Add local Web UI project health panel if feasible
- [ ] Add tests
- [ ] Update docs

## P4.8 Quality and closure

- [ ] Add P4 fixture project
- [ ] Add pipeline smoke tests
- [ ] Add broken reproduction scenario
- [ ] Add failed test scenario
- [ ] Add missing evidence scenario
- [ ] Update README.zh-CN.md
- [ ] Update README.en.md
- [ ] Update TODO.md
- [ ] Update TODO-P3-P5.md
- [ ] Add P4 final audit
- [ ] Close Issue #19 after CI passes

## Boundaries

- P4 may add local automation commands and local files.
- P4 must not introduce paid cloud services.
- P4 must not add external account systems.
- P4 must not publish releases.
- P4 must not change repository permissions.
- P4 must not start P6 implementation.
