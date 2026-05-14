# ADR 0007: Review Notes Boundary

## Status

Accepted

## Context

P2 expands the local Web UI into a diagnostic workbench. The workbench can browse packages, preview evidence, review verification status, review comparisons, review redaction status, and inspect export manifests.

A later review mode may allow a human reviewer to add notes while inspecting a diagnostic package. For P2, the Web UI must remain local and read-only by default.

## Decision

P2 will not add Web UI write-back.

Review notes stay as a future decision item. Before they are implemented, a new ADR must define:

- review note schema;
- reviewer metadata;
- timestamp requirements;
- source page requirements;
- audit trail rules;
- explicit save action;
- read-only mode versus write-enabled mode;
- how notes appear in the diagnostic package;
- how notes affect AI tasks and verification.

## Consequences

- P2 can complete as a read-only diagnostic workbench.
- The browser may show review guidance, but it must not save notes by default.
- Any future notes feature must be explicit, auditable, and covered by tests.
- Evidence files, user assertions, and verification files remain the authoritative diagnostic record.
