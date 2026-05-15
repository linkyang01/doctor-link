# Doctor link P2+ Mainline Enhancement TODO

Issue: #37
Roadmap: docs/roadmap/p2plus.md
ADR: docs/adr/0009-p2plus-mainline-enhancement.md

P2+ is not a separate long-term phase. It is a mainline enhancement task group after P2.

Goal: improve the local read-only diagnostic workbench and prepare stronger AI Coding handoff, while keeping Doctor link as a diagnostic context layer.

## Planning

- [x] Add P2+ TODO
- [x] Create P2+ GitHub Issue
- [x] Add P2+ roadmap document
- [x] Add ADR for P2+ mainline enhancement boundary
- [x] Update main TODO

## Review Notes Boundary

- [x] Keep Web UI read-only by default
- [ ] Design review notes data structure
- [x] Add ADR before any write-back implementation
- [ ] If write-back is added later, make it explicit and auditable

## Evidence Review Enhancement

- [x] Add evidence detail summary model
- [x] Show reverse links from evidence to timeline, assertions, tests, and verification when possible
- [x] Improve evidence type grouping
- [x] Improve redaction warning visibility
- [x] Add evidence review tests

## Verification Workbench Enhancement

- [x] Show assertion coverage reason details
- [x] Show test record statuses near assertion coverage
- [x] Explain verification status causes
- [x] Show generated next commands as copyable command blocks
- [x] Add verification workbench tests

## AI Task Handoff Enhancement

- [x] Add AI handoff summary section
- [x] Add copy-ready AI task block
- [x] Add copy-ready investigation boundary block
- [x] Add copy-ready verification checklist block
- [ ] Add Codex / AI Code task template
- [x] Add tests for AI handoff rendering

## Web UI Usability Enhancement

- [x] Add return-to-index navigation
- [ ] Add collapsible long sections
- [x] Add section quick links
- [x] Improve status badges
- [ ] Add basic accessibility checks

## Fixtures and Quality

- [ ] Add sample diagnostic package fixture
- [ ] Include user assertions in fixture
- [ ] Include test records in fixture
- [ ] Include comparison data in fixture
- [ ] Include redaction report in fixture
- [x] Add P2+ smoke tests

## Documentation and Audit

- [ ] Update README.zh-CN.md
- [ ] Update README.en.md
- [ ] Add P2+ final audit
- [x] Update this TODO after each PR
- [ ] Close P2+ Issue after CI passes
