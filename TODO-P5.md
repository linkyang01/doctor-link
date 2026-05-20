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

- [ ] Define semantic versioning policy
- [ ] Add `CHANGELOG.md`
- [ ] Add release checklist document
- [ ] Add release approval rule: no publishing without explicit authorization
- [ ] Add version consistency check
- [ ] Add tests or CI coverage for version consistency
- [ ] Update docs

## P5.2 Packaging and installation

- [ ] Review `pyproject.toml` metadata
- [ ] Add license metadata
- [ ] Add classifiers
- [ ] Add package data rules for templates and docs
- [ ] Test local install from source
- [ ] Test wheel build
- [ ] Add packaging CI job or smoke check
- [ ] Document installation methods

## P5.3 User documentation

- [ ] Add quick start guide
- [ ] Add CLI command reference
- [ ] Add diagnostic package format guide
- [ ] Add AI coding workflow guide
- [ ] Add P2 local workbench guide
- [ ] Add troubleshooting guide
- [ ] Add Chinese and English documentation parity checklist

## P5.4 Examples and templates

- [ ] Add example diagnostic package
- [ ] Add example project with `.doctorlink` config
- [ ] Add example AI handoff package
- [ ] Add example before/after comparison
- [ ] Add example verification result
- [ ] Add template gallery documentation

## P5.5 Security and privacy review

- [ ] Write privacy model document
- [ ] Write sensitive information handling document
- [ ] Review redaction defaults
- [ ] Add security checklist for exported packages
- [ ] Add documentation for what may be included in diagnostic packages
- [ ] Add tests for redaction regression cases

## P5.6 Product positioning and website docs

- [ ] Add product overview page
- [ ] Add use case page: non-programmer user
- [ ] Add use case page: AI coding tool
- [ ] Add use case page: developer
- [ ] Add use case page: team workflow
- [ ] Add architecture overview diagram source
- [ ] Add roadmap document
- [ ] Add contribution guide
- [ ] Add issue triage guide

## P5.7 Adapter and plugin documentation

- [ ] Document adapter concept
- [ ] Document collector extension points
- [ ] Document handoff profile extension points
- [ ] Document project-specific `.doctorlink` customization
- [ ] Add future SDK placeholder docs without over-promising implementation

## P5.8 Release readiness without publishing

- [ ] Prepare draft release notes
- [ ] Prepare draft GitHub Release body
- [ ] Verify all tests pass
- [ ] Verify documentation is current
- [ ] Verify examples work
- [ ] Verify no known critical privacy gaps
- [ ] Add P5 final audit
- [ ] Update README.zh-CN.md
- [ ] Update README.en.md
- [ ] Update TODO.md
- [ ] Update TODO-P3-P5.md
- [ ] Close Issue #20 after CI passes
- [ ] Stop before publishing unless explicit release authorization is given

## Boundaries

- Do not publish releases without explicit authorization.
- Do not create a GitHub Release without explicit authorization.
- Do not publish to PyPI or other package registries without explicit authorization.
- Do not modify repository permissions without explicit authorization.
- Do not introduce paid cloud services without explicit authorization.
- Do not introduce external account systems without explicit authorization.
- Do not start P6 implementation without explicit authorization.
