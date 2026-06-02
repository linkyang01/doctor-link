# P7 Final Audit

Status: final validation and closure

## Scope

P7 was opened to convert prior planning, schema, and documentation-only capabilities into real local runtime behavior where appropriate.

P7 remains local-first. It does not introduce hosted services, paid cloud dependencies, external account systems, remote publishing, marketplace behavior, telemetry, real signing key management, or release publication.

## Runtime completion summary

### P7.1 Evidence hardening

Completed runtime coverage:

- richer command metadata;
- command duration and timeout metadata;
- stdout / stderr split output where present;
- improved environment capture;
- project structure summary;
- large log truncation metadata;
- encoding-tolerant log ingestion;
- binary log skip behavior;
- media probe missing-tool behavior;
- redaction coverage for command output and logs;
- custom redaction pattern support;
- evidence integrity index.

### P7.2 Local workbench hardening

Completed runtime coverage:

- collapsible local workbench sections;
- project health panel;
- evidence search and filtering;
- assertion/evidence navigation;
- verification state visualization;
- accessibility structure;
- controlled CLI-only write-back;
- write-back backup and audit records.

### P7.3 AI handoff runtime

Completed runtime coverage:

- target tool profile model;
- Codex, Cursor, Continue, Aider, OpenHands, Claude Code, and generic profiles;
- handoff compatibility checker;
- target-specific instructions;
- file inclusion policy;
- missing evidence warnings;
- privacy warnings;
- AI result ingestion;
- repair session IDs;
- multi-round repair session history.

### P7.4 Operational automation

Completed runtime coverage:

- `doctor-link ci report`;
- CI report JSON and Markdown;
- GitHub step summary Markdown;
- failure triage summary;
- regression score;
- test matrix aggregation;
- project health trend;
- CI artifact index.

### P7.5 Distribution readiness

Completed runtime coverage:

- `doctor-link distribution check`;
- local readiness dry-run;
- artifact checksum generation;
- wheel metadata verification;
- source archive metadata verification;
- distribution manifest;
- blocking checklist automation;
- target environment capture.

### P7.6 Adapter SDK runtime

Completed runtime coverage:

- adapter manifest loader;
- adapter schema validation;
- adapter capability validation;
- adapter discovery;
- local adapter execution boundary;
- evidence collector, verification, and handoff capability names;
- adapter audit records;
- `doctor-link adapter list`;
- `doctor-link adapter validate`;
- `doctor-link adapter run`.

### P7.7 Plugin SDK runtime

Completed runtime coverage:

- plugin manifest loader;
- plugin permission model enforcement;
- plugin discovery;
- collector, renderer, handoff, and verification extension points;
- local process boundary label;
- plugin audit log;
- `doctor-link plugin list`;
- `doctor-link plugin validate`;
- `doctor-link plugin run`.

### P7.8 Integrity and privacy runtime gates

Completed runtime coverage:

- integrity manifest generator;
- integrity verify command;
- hash mismatch detection;
- missing file detection;
- unsafe path detection;
- unsigned manifest warning;
- privacy policy loader;
- privacy scan command;
- redaction gate;
- export safety gate.

Real signing and key management remain intentionally out of scope.

### P7.9 Local knowledge base and enterprise archive runtime

Completed runtime coverage:

- local diagnostic knowledge index;
- recurring failure signature extraction;
- repair outcome aggregation;
- project health trend aggregation;
- knowledge query;
- knowledge export;
- archive metadata record;
- retention policy check;
- audit trail append behavior;
- local archive export.

Hosted archive and hosted knowledge base services remain intentionally out of scope.

## P7.10 validation closure

P7.10 adds `scripts/p7_runtime_validate.sh`, a local runtime validation script that exercises P7 runtime capabilities from P7.1 through P7.9.

The script validates:

- diagnosis strategy validation;
- reproduction listing and execution;
- test matrix listing and execution;
- schema validation;
- evidence collection;
- user assertion recording;
- AI result ingestion;
- diagnosis history recording;
- assertion compliance;
- risk review;
- verification;
- handoff generation;
- local workbench build;
- workbench write-back audit;
- CI report generation;
- distribution readiness check;
- adapter list / validate / run;
- plugin list / validate / run;
- integrity manifest and verification;
- privacy scan;
- redaction gate;
- export gate;
- knowledge build / query / export;
- archive create / inspect / policy-check / export.

## CI closure

P7.10 updates CI to run:

- ruff static checks;
- pytest with coverage;
- CLI smoke tests;
- existing E2E validation;
- package build;
- P7 runtime validation;
- installed wheel smoke test.

The package validation job also runs the existing validation script and the new P7 runtime validation script after installing the built wheel.

## Final boundaries

P7 closure does not mean Doctor link has implemented:

- hosted Web platform;
- cloud synchronization;
- external account system;
- paid cloud service;
- telemetry system;
- marketplace;
- real signing keys or key management;
- hosted enterprise archive;
- hosted diagnostic knowledge base;
- real RBAC or enterprise identity integration;
- GitHub Release, release tag, or PyPI publication.

P7 closure means the planned local runtime capabilities through P7.9 are implemented, tested, documented, and validated in CI.

## Closure condition

P7 is considered repository-side complete after the P7.10 PR passes CI and is merged into `main`.

Issue #95 should only be closed after final authorization and successful merge of P7.10.
