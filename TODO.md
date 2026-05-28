# Doctor link TODO

This file tracks phase-level project status. Detailed implementation tasks are tracked in dedicated TODO files, issues, ADRs, and audit documents.

## Current Phase Status

- [x] P0: Diagnostic Foundation
- [x] P1: Evidence Collection Primitives
- [x] P1+: CLI Evidence Pipeline
- [x] P2: Local Read-only Diagnostic Workbench
- [x] P2+: Mainline Diagnostic Workbench Enhancements
- [x] P3: AI Coding Collaboration Layer
- [x] P4: Automated Diagnosis Pipeline
- [x] P5: Productization and Release Readiness
- [x] P5.9: Release hardening and usability validation
- [ ] P5.10: Local validation hardening before P6 authorization
- [ ] P6: Diagnostic Protocol Standardization and Ecosystem Platform

## Completed Phase Audits

- [x] P1/P1+/P2 final audit: `docs/p1-p2-final-audit.md`
- [x] P2 final audit: `docs/p2-final-audit.md`
- [x] P2+ final audit: `docs/p2plus-final-audit.md`
- [x] P3 final audit: `docs/p3-final-audit.md`
- [x] P4 final audit: `docs/p4-final-audit.md`
- [x] P5 final audit: `docs/p5-final-audit.md`
- [x] P5.9 final audit: `docs/p5.9-final-audit.md`

## Completed Tracking Issues

- [x] Issue #15: P2 local Web UI and diagnostic package browser
- [x] Issue #31: P1/P1+ assertion-test-verification hardening
- [x] Issue #37: P2+ mainline diagnostic workbench enhancements
- [x] Issue #18: P3 AI Coding collaboration layer
- [x] Issue #19: P4 automated diagnosis pipeline
- [x] Issue #20: P5 productization and release readiness
- [x] Issue #71: P5.9 release hardening and usability validation

## Active / Future Tracking Issues

- [ ] P5.10 local validation hardening before P6 authorization
- [ ] Issue #22: P6 diagnostic protocol standardization and ecosystem platform

## Completed P4 Scope

- [x] `doctor-link strategy validate`
- [x] `doctor-link reproduce list/run`
- [x] `doctor-link test list/run`
- [x] `doctor-link diagnose before/after`
- [x] `doctor-link diagnose compare/verify`
- [x] `doctor-link health`
- [x] GitHub Actions PR diagnostics documentation
- [x] P4 pipeline smoke coverage

## Completed P5 Scope

- [x] Versioning and release policy
- [x] Packaging and installation readiness
- [x] User documentation
- [x] Examples and templates
- [x] Security and privacy review
- [x] Product positioning and website docs
- [x] Adapter and plugin documentation
- [x] Draft release notes and release readiness audit
- [x] P5.9 release hardening and usability validation

## P5.10 Scope

- [x] Keep feature development paused.
- [x] Define local validation command sequence.
- [x] Define expected validation artifacts.
- [x] Define failure triage workflow.
- [x] Define P6 authorization gate.
- [ ] Record actual local validation run results.

## Deferred Decisions

- [ ] Web UI write-back remains deferred and requires a future ADR.
- [ ] Dedicated project health Web UI panel is deferred to a future visual refresh.
- [ ] P6 implementation requires separate explicit authorization.
- [ ] Release publishing, GitHub Release, PyPI publishing, repository permission changes, paid cloud services, and external account systems require separate explicit authorization.

## Working Rules

1. Code changes must be tied to a TODO, issue, or audit document.
2. Architecture changes must be recorded in `docs/adr/`.
3. Completed work must update tracking files.
4. Do not proceed from memory only; inspect repository state first.
5. Do not publish releases without explicit authorization.
