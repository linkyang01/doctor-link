# Doctor link TODO

This file tracks phase-level project status. Detailed implementation tasks are tracked in dedicated TODO files, issues, ADRs, and audit documents.

## Current Phase Status

- [x] P0: Diagnostic Foundation
- [x] P1: Evidence Collection Primitives
- [x] P1+: CLI Evidence Pipeline
- [x] P2: Local Read-only Diagnostic Workbench
- [x] P2+: Mainline Diagnostic Workbench Enhancements
- [x] P3: AI Coding Collaboration Layer
- [ ] P4: Automated Diagnosis Pipeline
- [ ] P5: Productization and Release Readiness
- [ ] P6: Diagnostic Protocol Standardization and Ecosystem Platform

## Completed Phase Audits

- [x] P1/P1+/P2 final audit: `docs/p1-p2-final-audit.md`
- [x] P2 final audit: `docs/p2-final-audit.md`
- [x] P2+ final audit: `docs/p2plus-final-audit.md`
- [x] P3 final audit: `docs/p3-final-audit.md`

## Completed Tracking Issues

- [x] Issue #15: P2 local Web UI and diagnostic package browser
- [x] Issue #31: P1/P1+ assertion-test-verification hardening
- [x] Issue #37: P2+ mainline diagnostic workbench enhancements
- [x] Issue #18: P3 AI Coding collaboration layer

## Active / Future Tracking Issues

- [ ] Issue #19: P4 automated diagnosis pipeline
- [ ] Issue #20: P5 productization and release readiness
- [ ] Issue #22: P6 diagnostic protocol standardization and ecosystem platform

## P3 Completed Scope

- [x] AI task template system
- [x] AI tool handoff packages
- [x] `doctor-link handoff`
- [x] `doctor-link ai-result`
- [x] `doctor-link diagnosis-history`
- [x] `doctor-link assertion-check`
- [x] `doctor-link risk-review`
- [x] `ai-repair-result.json` / `ai-repair-result.md`
- [x] `diagnosis-history.json` / `diagnosis-history.md`
- [x] `assertion-compliance-report.json` / `assertion-compliance-report.md`
- [x] `repair-risk-review.json` / `repair-risk-review.md`
- [x] P3 tests and CI validation

## Deferred Decisions

- [ ] Web UI write-back remains deferred and requires a future ADR.
- [ ] P6 implementation requires separate explicit authorization.
- [ ] Release publishing, GitHub Release, PyPI publishing, repository permission changes, paid cloud services, and external account systems require separate explicit authorization.

## Working Rules

1. Code changes must be tied to a TODO, issue, or audit document.
2. Architecture changes must be recorded in `docs/adr/`.
3. Completed work must update tracking files.
4. Do not proceed from memory only; inspect repository state first.
5. Do not publish releases without explicit authorization.
