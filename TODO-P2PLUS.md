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
- [ ] Update main TODO

## Review Notes Boundary

- [ ] Keep Web UI read-only by default
- [ ] Design review notes data structure
- [ ] Add ADR before any write-back implementation
- [ ] If write-back is added later, make it explicit and auditable

## Evidence Review Enhancement

- [ ] Add evidence detail summary model
- [ ] Show reverse links from evidence to timeline, assertions, tests, and verification when possible
- [ ] Improve evidence type grouping
- [ ] Improve redaction warning visibility
- [ ] Add evidence review tests

## Verification Workbench Enhancement

- [ ] Show assertion coverage reason details
- [ ] Show test record statuses near assertion coverage
- [ ] Explain verification status causes
- [ ] Show generated next commands as copyable command blocks
- [ ] Add verification workbench tests

## AI Task Handoff Enhancement

- [ ] Add AI handoff summary section
- [ ] Add copy-ready AI task block
- [ ] Add copy-ready investigation boundary block
- [ ] Add copy-ready verification checklist block
- [ ] Add Codex / AI Code task template
- [ ] Add tests for AI handoff rendering

## Web UI Usability Enhancement

- [ ] Add return-to-index navigation
- [ ] Add collapsible long sections
- [ ] Add section quick links
- [ ] Improve status badges
- [ ] Add basic accessibility checks

## Fixtures and Quality

- [ ] Add sample diagnostic package fixture
- [ ] Include user assertions in fixture
- [ ] Include test records in fixture
- [ ] Include comparison data in fixture
- [ ] Include redaction report in fixture
- [ ] Add P2+ smoke tests

## Documentation and Audit

- [ ] Update README.zh-CN.md
- [ ] Update README.en.md
- [ ] Add P2+ final audit
- [ ] Update this TODO after each PR
- [ ] Close P2+ Issue after CI passes
