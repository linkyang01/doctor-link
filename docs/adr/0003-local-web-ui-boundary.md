# ADR 0003: Local Web UI Boundary

## Status

Accepted

## Context

Doctor link has completed the P0/P1/P1+ CLI diagnostic foundation. The next stage is P2: a local Web UI and diagnostic package browser.

Doctor link must remain a diagnostic context layer for AI coding workflows. The Web UI must not turn Doctor link into a cloud service, a generic log viewer, or an AI coding tool replacement.

## Decision

P2 Web UI will be local-first and package-first.

The initial Web UI will:

- run locally from the CLI;
- read an existing standard diagnostic package directory;
- render package sections in a browser-friendly view;
- preserve evidence-first and human-assertion-first semantics;
- avoid mutating package contents in the first batch;
- avoid external network dependencies;
- avoid authentication, accounts, cloud sync, or hosted services.

The first P2 batch will provide a diagnostic package browser for:

- summary;
- timeline;
- evidence list;
- user assertions;
- AI task;
- verification plan and result;
- investigation boundary;
- redaction report;
- manifest and package readme when available.

## Consequences

- The CLI remains the source of package creation and collection workflows.
- The Web UI is a viewing and navigation layer in the first batch.
- Package structure remains compatible with P0/P1/P1+ tools.
- No new server framework is introduced initially; Python standard library HTTP serving is preferred until UI requirements justify a framework.
- Future P2 batches may add package comparison, local annotations, or guided validation, but those changes must preserve the diagnostic protocol and be tracked in TODO and ADR when architectural boundaries change.
