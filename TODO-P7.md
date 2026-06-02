# Doctor link P7 TODO

P7 tracks runtime implementation and real-capability completion.

P7 is not a documentation-only phase. A P7 item is complete only when it has real code, CLI or runtime behavior where applicable, tests, documentation, CI validation, and acceptance evidence.

Related files:

- P7 Issue: #95
- Roadmap: `docs/roadmap/p7.md`
- Gap audit: `docs/p7-real-capability-gap-audit.md`
- Acceptance criteria: `docs/p7-acceptance-criteria.md`
- P7.1 Evidence Hardening: `docs/p7-evidence-hardening.md`
- P7.2 Workbench Hardening: `docs/p7-workbench-hardening.md`
- P7.3 AI Handoff Runtime: `docs/p7-ai-handoff-runtime.md`
- P7.4 Operational Automation: `docs/p7-operational-automation.md`
- P7.5 Distribution Readiness: `docs/p7-distribution-readiness.md`
- P7.6 Adapter Runtime: `docs/p7-adapter-runtime.md`
- P7.7 Plugin Runtime: `docs/p7-plugin-runtime.md`
- P7.8 Integrity and Privacy Gates: `docs/p7-integrity-privacy-gates.md`
- P7.9 Knowledge and Archive Runtime: `docs/p7-knowledge-archive-runtime.md`
- P7.10 Final Audit: `docs/p7-final-audit.md`
- P7.10 Self-validation: `docs/p7-self-validation.md`

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

- [x] Enhance command capture metadata
- [x] Add command duration and timeout metadata
- [x] Separate stdout and stderr records where appropriate
- [x] Improve environment capture
- [x] Improve project structure summary
- [x] Improve log ingestion for large files
- [x] Add encoding-tolerant log ingestion behavior
- [x] Add binary file skip behavior
- [x] Improve media probe missing-tool behavior
- [x] Add stronger redaction coverage
- [x] Add custom redaction pattern support
- [x] Add evidence hash / integrity index
- [x] Add tests and fixtures for P7.1
- [x] Update documentation for P7.1

## P7.2 P2/P2+ local workbench product hardening

- [x] Add collapsible sections to static workbench output
- [x] Add dedicated project health page or panel
- [x] Add evidence search / filtering in local workbench output
- [x] Improve assertion-to-evidence navigation
- [x] Improve evidence-to-assertion navigation
- [x] Improve verification status visualization
- [x] Add basic accessibility audit checklist
- [x] Design controlled local write-back mode
- [x] Implement controlled local write-back only if explicitly enabled
- [x] Add write-back audit record and backup behavior
- [x] Add tests and fixtures for P7.2
- [x] Update documentation for P7.2

## P7.3 P3 AI tool runtime handoff implementation

- [x] Define target tool profile model
- [x] Add Codex profile
- [x] Add Cursor profile
- [x] Add Continue profile
- [x] Add Aider profile
- [x] Add OpenHands profile
- [x] Add Claude Code profile
- [x] Add handoff compatibility checker
- [x] Add target-tool-specific instruction generation
- [x] Add file inclusion policy enforcement
- [x] Add missing evidence warnings
- [x] Add privacy warnings in handoff output
- [x] Enhance AI result ingestion
- [x] Add repair session id support
- [x] Add multi-round repair session management
- [x] Add tests and fixtures for P7.3
- [x] Update documentation for P7.3

## P7.4 P4 operational automation hardening

- [x] Add CI report generation command
- [x] Add GitHub Actions markdown report artifact generation
- [x] Add failure triage summary
- [x] Add before / after regression score
- [x] Add test matrix aggregation report
- [x] Add project health trend support
- [x] Add CI artifact index generation
- [x] Add tests and fixtures for P7.4
- [x] Update documentation for P7.4

## P7.5 P5 release/distribution readiness execution plan

- [x] Add release dry-run command or script
- [x] Add artifact checksum generation
- [x] Add wheel metadata verification
- [x] Add sdist metadata verification
- [x] Add release manifest generation
- [x] Add release blocking checklist automation
- [x] Add target-environment validation helper
- [x] Add tests and fixtures for P7.5
- [x] Update documentation for P7.5
- [x] Do not publish release without explicit authorization

## P7.6 P6 Adapter SDK runtime

- [x] Add adapter manifest loader
- [x] Add adapter schema validation
- [x] Add adapter capability validation
- [x] Add adapter discovery
- [x] Add local adapter execution boundary
- [x] Add evidence collector adapter interface
- [x] Add verification adapter interface
- [x] Add handoff adapter interface
- [x] Add adapter audit records
- [x] Add `doctor-link adapter list`
- [x] Add `doctor-link adapter validate`
- [x] Add `doctor-link adapter run`
- [x] Add tests and fixtures for P7.6
- [x] Update documentation for P7.6

## P7.7 P6 Plugin SDK runtime

- [x] Add plugin manifest loader
- [x] Add plugin permission model enforcement
- [x] Add plugin discovery
- [x] Add collector plugin extension point
- [x] Add renderer plugin extension point
- [x] Add handoff plugin extension point
- [x] Add verification plugin extension point
- [x] Add plugin sandbox boundary
- [x] Add plugin audit log
- [x] Add `doctor-link plugin list`
- [x] Add `doctor-link plugin validate`
- [x] Add `doctor-link plugin run`
- [x] Add tests and fixtures for P7.7
- [x] Update documentation for P7.7

## P7.8 P6 integrity/signing/privacy runtime gates

- [x] Add integrity manifest generator
- [x] Add integrity verify command
- [x] Add hash mismatch detection
- [x] Add missing file detection
- [x] Add unsafe path detection
- [x] Add unsigned package warning
- [x] Add privacy policy loader
- [x] Add privacy scan command
- [x] Add redaction gate command
- [x] Add export safety gate command
- [x] Add local test signing plan if authorized
- [x] Add tests and fixtures for P7.8
- [x] Update documentation for P7.8

## P7.9 P6 local knowledge base and enterprise archive runtime

- [x] Add local diagnostic knowledge index
- [x] Add recurring failure signature extraction
- [x] Add repair outcome aggregation
- [x] Add project health trend aggregation
- [x] Add knowledge export command
- [x] Add archive metadata record
- [x] Add retention policy check
- [x] Add audit trail append behavior
- [x] Add local archive export
- [x] Add `doctor-link knowledge build`
- [x] Add `doctor-link knowledge query`
- [x] Add `doctor-link knowledge export`
- [x] Add `doctor-link archive create`
- [x] Add `doctor-link archive inspect`
- [x] Add `doctor-link archive policy-check`
- [x] Add tests and fixtures for P7.9
- [x] Update documentation for P7.9

## P7.10 P7 final validation and closure

- [x] Add P7 final audit
- [x] Add P7 runtime e2e validation script
- [x] Add P7 self-validation scenario
- [x] Ensure ruff passes
- [x] Ensure pytest passes
- [x] Ensure coverage does not regress materially
- [x] Ensure package build passes
- [x] Ensure `scripts/validate_doctor_link.sh` passes
- [x] Ensure `scripts/e2e_validate.sh` passes
- [x] Update README.zh-CN.md
- [x] Update README.en.md
- [x] Update `docs/project-status.md`
- [x] Mark TODO-P7 complete
- [ ] Close P7 Issue #95 after final authorization
