# P7 Real-capability Gap Audit

Status: initial P7.0 audit

## Purpose

This audit separates implemented runtime capabilities from documentation-only, schema-only, planning-only, deferred UX, release/distribution, and local-only work.

P7 exists to avoid treating planning documents as runtime implementation.

## Classification model

Capabilities are classified as:

```text
implemented-runtime
implemented-cli
implemented-docs
schema-only
planning-only
deferred-ux
release-action
local-only
p7-runtime-candidate
out-of-scope-without-authorization
```

## Implemented runtime / CLI capabilities

The following are treated as already implemented in the current mainline scope and should be preserved during P7:

- diagnostic package creation;
- evidence collection primitives;
- CLI evidence pipeline;
- verification record generation;
- user assertion recording;
- local read-only package workbench generation;
- AI handoff package generation;
- AI result record intake;
- diagnosis history recording;
- assertion compliance checking;
- repair risk review;
- strategy validation;
- reproduction listing and running;
- test matrix listing and running;
- before / after diagnostic package workflow;
- automated comparison and verification;
- project health summary;
- schema validation;
- conformance runner.

## Documentation-only or example-only capabilities from P1-P5

These areas exist as documentation, examples, or basic artifacts, but P7 should review whether they need deeper runtime/product behavior:

- GitHub Actions PR diagnostics beyond documentation and workflow examples;
- release execution beyond draft release notes and release readiness checklist;
- target-environment validation record completion;
- product website-style documentation;
- adapter and extension documentation that predates real runtime SDKs.

## Deferred UX capabilities from P2/P2+

Known deferred workbench items:

- actual Web UI write-back is not implemented;
- collapsible sections are not implemented in the static workbench;
- richer front-end accessibility audit remains future work;
- dedicated project health Web UI panel was deferred.

P7 must decide which of these become runtime/product requirements.

## P1/P1+ hardening gaps

Current P1/P1+ is complete for the accepted scope, but P7 should harden it for production use:

- command capture metadata can be richer;
- command duration and timeout handling can be stronger;
- environment capture can be more comprehensive;
- log ingestion can better handle large files and encodings;
- media probe behavior can be more graceful when tools are missing;
- redaction coverage can be stronger;
- evidence integrity records can be added.

## P3 AI collaboration gaps

P3 has local collaboration records and handoff packages, but does not implement real tool-specific runtime integration helpers.

P7 runtime candidates:

- target tool profiles;
- handoff compatibility checks;
- tool-specific instruction generation;
- repair session management;
- AI result ingestion from real tool output files;
- stronger verification gates for claimed fixes.

## P4 automation gaps

P4 has pipeline commands and reports, but operational automation can be improved.

P7 runtime candidates:

- CI report generation command;
- PR/report markdown artifacts;
- failure triage summary;
- before / after regression scoring;
- project health trend aggregation;
- CI artifact index.

## P5 release/distribution gaps

P5 release readiness exists, but release execution was intentionally not performed.

P7 release-readiness candidates:

- release dry-run;
- artifact checksum generation;
- wheel and sdist metadata verification;
- release manifest generation;
- release blocking checklist automation;
- target-environment validation helper.

Release actions remain authorization-gated:

- GitHub Release creation;
- release tag creation;
- PyPI publishing;
- repository permission changes.

## P6 specification-only capabilities

P6 is complete as a specification and schema closure. The following are not implemented as runtime capabilities:

- Adapter SDK runtime;
- Plugin SDK runtime;
- dynamic local plugin loading;
- real third-party AI tool integration helpers;
- real signing implementation;
- key management implementation;
- integrity verify command implementation;
- privacy scan implementation;
- redaction gate implementation;
- export safety gate implementation;
- enterprise archive local implementation;
- local diagnostic knowledge base implementation;
- ecosystem catalog validation tooling.

## Local-only capabilities

The following cannot be completed from the repository alone:

- local / target-environment validation execution;
- recording the final local validation result in `docs/p5.10-local-validation.md`.

## Out of scope without explicit authorization

These remain out of scope unless separately authorized:

- hosted Web platform;
- cloud service;
- external account system;
- paid cloud services;
- hosted marketplace;
- telemetry collection;
- GitHub Release creation;
- release tag creation;
- PyPI publishing;
- repository permission changes.

## P7 implementation priority

Recommended first implementation sequence:

1. P7.1 evidence hardening;
2. P7.8 integrity/privacy gates;
3. P7.3 AI handoff runtime helpers;
4. P7.6 Adapter SDK runtime;
5. P7.7 Plugin SDK runtime;
6. P7.4 operational automation;
7. P7.2 local workbench hardening;
8. P7.9 knowledge base and archive runtime;
9. P7.5 release dry-run tooling;
10. P7.10 final validation.

This order prioritizes safety, evidence quality, and validation before extensibility and release/distribution concerns.
