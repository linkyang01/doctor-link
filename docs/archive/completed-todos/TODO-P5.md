# Doctor link P5 TODO

Issue: #20
Parent tracker: TODO-P3-P5.md
Roadmap: docs/roadmap/p3-p5.md

P5 goal: make Doctor link productized, installable, documented, secure-by-default, and release-ready without publishing.

No release, GitHub Release, PyPI publication, repository permission change, paid cloud service, or external account system may be introduced without separate explicit authorization.

## Execution batches

P5 should be implemented in small CI-safe PRs:

1. P5.1 Versioning and release policy
2. P5.2 Packaging and installation
3. P5.3 User documentation
4. P5.4 Examples and templates
5. P5.5 Security and privacy review
6. P5.6 Product positioning and website docs
7. P5.7 Adapter and plugin documentation
8. P5.8 Release readiness without publishing

## P5.1 Versioning and release policy

- [x] Define semantic versioning policy
- [x] Add `CHANGELOG.md`
- [x] Add release checklist document
- [x] Add release approval rule: no publishing without explicit authorization
- [x] Add version consistency check
- [x] Add tests or CI coverage for version consistency
- [x] Update docs

## P5.2 Packaging and installation

- [x] Review `pyproject.toml` metadata
- [x] Add license metadata
- [x] Add classifiers
- [x] Add package data rules for templates and docs
- [x] Test local install from source
- [x] Test wheel build
- [x] Add packaging CI job or smoke check
- [x] Document installation methods

## P5.3 User documentation

- [x] Add quick start guide
- [x] Add CLI command reference
- [x] Add diagnostic package format guide
- [x] Add AI coding workflow guide
- [x] Add P2 local workbench guide
- [x] Add troubleshooting guide
- [x] Add Chinese and English documentation parity checklist

## P5.4 Examples and templates

- [x] Add example diagnostic package
- [x] Add example project with `.doctorlink` config
- [x] Add example AI handoff package
- [x] Add example before/after comparison
- [x] Add example verification result
- [x] Add template gallery documentation

## P5.5 Security and privacy review

- [x] Write privacy model document
- [x] Write sensitive information handling document
- [x] Review redaction defaults
- [x] Add security checklist for exported packages
- [x] Add documentation for what may be included in diagnostic packages
- [x] Add tests for redaction regression cases

## P5.6 Product positioning and website docs

- [x] Add product overview page
- [x] Add use case page: non-programmer user
- [x] Add use case page: AI coding tool
- [x] Add use case page: developer
- [x] Add use case page: team workflow
- [x] Add architecture overview diagram source
- [x] Add roadmap document
- [x] Add contribution guide
- [x] Add issue triage guide

## P5.7 Adapter and plugin documentation

- [x] Document adapter concept
- [x] Document collector extension points
- [x] Document handoff profile extension points
- [x] Document project-specific `.doctorlink` customization
- [x] Add future SDK placeholder docs without over-promising implementation

## P5.8 Release readiness without publishing

- [x] Prepare draft release notes
- [x] Prepare draft GitHub Release body
- [x] Verify all tests pass
- [x] Verify documentation is current
- [x] Verify examples work
- [x] Verify no known critical privacy gaps
- [x] Add P5 final audit
- [x] Update README.zh-CN.md
- [x] Update README.en.md
- [x] Update TODO.md
- [x] Update TODO-P3-P5.md
- [x] Close Issue #20 after CI passes
- [x] Stop before publishing unless explicit release authorization is given

## Boundaries

- Do not publish releases without explicit authorization.
- Do not create a GitHub Release without explicit authorization.
- Do not publish to PyPI or other package registries without explicit authorization.
- Do not modify repository permissions without explicit authorization.
- Do not introduce paid cloud services without explicit authorization.
- Do not introduce external account systems without explicit authorization.
- Do not start P6 implementation without explicit authorization.
