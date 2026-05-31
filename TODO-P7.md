# Doctor link P7 TODO

P7 tracks runtime implementation and real-capability completion.

P7 is not a documentation-only phase. A P7 item is complete only when it has real code, CLI or runtime behavior where applicable, tests, documentation, CI validation, and acceptance evidence.

Related files:

- P7 Issue: #95
- Roadmap: `docs/roadmap/p7.md`
- Gap audit: `docs/p7-real-capability-gap-audit.md`
- Acceptance criteria: `docs/p7-acceptance-criteria.md`

Current boundaries:

- Do not create a GitHub Release without explicit authorization.
- Do not create a release tag without explicit authorization.
- Do not publish to PyPI without explicit authorization.
- Do not introduce paid cloud services without explicit authorization.
- Do not introduce external account systems without explicit authorization.
- Do not implement hosted marketplace or telemetry collection without explicit authorization.
- Keep local-first behavior as the default.

---

## P7.0 Real-capability gap audit and implementation map

- [x] Create `TODO-P7.md`
- [x] Create `docs/roadmap/p7.md`
- [x] Create `docs/p7-real-capability-gap-audit.md`
- [x] Create `docs/p7-acceptance-criteria.md`
- [x] Separate implemented runtime capabilities from documentation-only capabilities
- [x] Separate schema-only capabilities from runtime capabilities
- [x] Identify deferred UX capabilities from P1-P5
- [x] Identify P6 specification-only capabilities that require P7 runtime work
- [x] Identify local-only validation steps that require the user's machine
- [x] Identify release/distribution actions that require explicit authorization

## P7.1 P1/P1+ evidence hardening

- [ ] Enhance command capture metadata
- [ ] Add command duration and timeout metadata
- [ ] Separate stdout and stderr records where appropriate
- [ ] Improve environment capture
- [ ] Improve project structure summary
- [ ] Improve log ingestion for large files
- [ ] Add encoding-tolerant log ingestion behavior
- [ ] Add binary file skip behavior
- [ ] Improve media probe missing-tool behavior
- [ ] Add stronger redaction coverage
- [ ] Add custom redaction pattern support
- [ ] Add evidence hash / integrity index
- [ ] Add tests and fixtures for P7.1
- [ ] Update documentation for P7.1

## P7.2 P2/P2+ local workbench product hardening

- [ ] Add collapsible sections to static workbench output
- [ ] Add dedicated project health page or panel
- [ ] Add evidence search / filtering in local workbench output
- [ ] Improve assertion-to-evidence navigation
- [ ] Improve evidence-to-assertion navigation
- [ ] Improve verification status visualization
- [ ] Add basic accessibility audit checklist
- [ ] Design controlled local write-back mode
- [ ] Implement controlled local write-back only if explicitly enabled
- [ ] Add write-back audit record and backup behavior
- [ ] Add tests and fixtures for P7.2
- [ ] Update documentation for P7.2

## P7.3 P3 AI tool runtime handoff implementation

- [ ] Define target tool profile model
- [ ] Add Codex profile
- [ ] Add Cursor profile
- [ ] Add Continue profile
- [ ] Add Aider profile
- [ ] Add OpenHands profile
- [ ] Add Claude Code profile
- [ ] Add handoff compatibility checker
- [ ] Add target-tool-specific instruction generation
- [ ] Add file inclusion policy enforcement
- [ ] Add missing evidence warnings
- [ ] Add privacy warnings in handoff output
- [ ] Enhance AI result ingestion
- [ ] Add repair session id support
- [ ] Add multi-round repair session management
- [ ] Add tests and fixtures for P7.3
- [ ] Update documentation for P7.3

## P7.4 P4 operational automation hardening

- [ ] Add CI report generation command
- [ ] Add GitHub Actions markdown report artifact generation
- [ ] Add failure triage summary
- [ ] Add before / after regression score
- [ ] Add test matrix aggregation report
- [ ] Add project health trend support
- [ ] Add CI artifact index generation
- [ ] Add tests and fixtures for P7.4
- [ ] Update documentation for P7.4

## P7.5 P5 release/distribution readiness execution plan

- [ ] Add release dry-run command or script
- [ ] Add artifact checksum generation
- [ ] Add wheel metadata verification
- [ ] Add sdist metadata verification
- [ ] Add release manifest generation
- [ ] Add release blocking checklist automation
- [ ] Add target-environment validation helper
- [ ] Add tests and fixtures for P7.5
- [ ] Update documentation for P7.5
- [ ] Do not publish release without explicit authorization

## P7.6 P6 Adapter SDK runtime

- [ ] Add adapter manifest loader
- [ ] Add adapter schema validation
- [ ] Add adapter capability validation
- [ ] Add adapter discovery
- [ ] Add local adapter execution boundary
- [ ] Add evidence collector adapter interface
- [ ] Add verification adapter interface
- [ ] Add handoff adapter interface
- [ ] Add adapter audit records
- [ ] Add `doctor-link adapter list`
- [ ] Add `doctor-link adapter validate`
- [ ] Add `doctor-link adapter run`
- [ ] Add tests and fixtures for P7.6
- [ ] Update documentation for P7.6

## P7.7 P6 Plugin SDK runtime

- [ ] Add plugin manifest loader
- [ ] Add plugin permission model enforcement
- [ ] Add plugin discovery
- [ ] Add collector plugin extension point
- [ ] Add renderer plugin extension point
- [ ] Add handoff plugin extension point
- [ ] Add verification plugin extension point
- [ ] Add plugin sandbox boundary
- [ ] Add plugin audit log
- [ ] Add `doctor-link plugin list`
- [ ] Add `doctor-link plugin validate`
- [ ] Add `doctor-link plugin run`
- [ ] Add tests and fixtures for P7.7
- [ ] Update documentation for P7.7

## P7.8 P6 integrity/signing/privacy runtime gates

- [ ] Add integrity manifest generator
- [ ] Add integrity verify command
- [ ] Add hash mismatch detection
- [ ] Add missing file detection
- [ ] Add unsafe path detection
- [ ] Add unsigned package warning
- [ ] Add privacy policy loader
- [ ] Add privacy scan command
- [ ] Add redaction gate command
- [ ] Add export safety gate command
- [ ] Add local test signing plan if authorized
- [ ] Add tests and fixtures for P7.8
- [ ] Update documentation for P7.8

## P7.9 P6 local knowledge base and enterprise archive runtime

- [ ] Add local diagnostic knowledge index
- [ ] Add recurring failure signature extraction
- [ ] Add repair outcome aggregation
- [ ] Add project health trend aggregation
- [ ] Add knowledge export command
- [ ] Add archive metadata record
- [ ] Add retention policy check
- [ ] Add audit trail append behavior
- [ ] Add local archive export
- [ ] Add `doctor-link knowledge build`
- [ ] Add `doctor-link knowledge query`
- [ ] Add `doctor-link knowledge export`
- [ ] Add `doctor-link archive create`
- [ ] Add `doctor-link archive inspect`
- [ ] Add `doctor-link archive policy-check`
- [ ] Add tests and fixtures for P7.9
- [ ] Update documentation for P7.9

## P7.10 P7 final validation and closure

- [ ] Add P7 final audit
- [ ] Add P7 runtime e2e validation script
- [ ] Add P7 self-validation scenario
- [ ] Ensure ruff passes
- [ ] Ensure pytest passes
- [ ] Ensure coverage does not regress materially
- [ ] Ensure package build passes
- [ ] Ensure `scripts/validate_doctor_link.sh` passes
- [ ] Ensure `scripts/e2e_validate.sh` passes
- [ ] Update README.zh-CN.md
- [ ] Update README.en.md
- [ ] Update `docs/project-status.md`
- [ ] Mark TODO-P7 complete
- [ ] Close P7 Issue #95 after final authorization
