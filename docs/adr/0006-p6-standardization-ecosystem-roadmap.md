# ADR 0006: P6 Standardization and Ecosystem Roadmap

## Status

Accepted

## Context

Doctor link's earlier roadmap stages build the foundation for diagnostic packages, evidence collection, local workbench capabilities, AI Coding collaboration, automated diagnosis, and productization.

After P5, Doctor link can become more than a tool: it can define a stable diagnostic context protocol for AI Coding workflows and support an ecosystem of adapters, plugins, viewers, validators, and integrations.

P6 is therefore not a normal feature phase. It is a standardization and ecosystem phase.

## Decision

P6 will be defined as:

> Diagnostic Protocol Standardization and Ecosystem Platform

P6 focuses on making Doctor link's diagnostic package format, evidence model, user assertion model, AI handoff model, and verification model stable enough for external tools and teams to adopt.

P6 will be organized into these workstreams:

1. Diagnostic Package Schema v1
   - formal JSON schemas;
   - schema versioning;
   - schema migration;
   - compatibility test suite.

2. SDK and extension ecosystem
   - Adapter SDK planning;
   - Plugin SDK planning;
   - collector extension points;
   - handoff profile extension points;
   - viewer extension points.

3. Third-party tool integration specification
   - AI Coding tool integration guidelines;
   - Codex / Cursor / Continue / Aider / OpenHands profile specifications;
   - generic tool handoff protocol.

4. Security, privacy, and integrity standardization
   - signing and integrity verification;
   - privacy classification levels;
   - redaction level specification;
   - enterprise sharing and archive policies.

5. Team and enterprise governance
   - team review protocol;
   - multi-role review states;
   - audit trail specification;
   - diagnostic package retention model.

6. Cross-project diagnostic knowledge
   - taxonomy for problem types;
   - reproduction pattern library;
   - verification pattern library;
   - repair quality metrics.

7. Public ecosystem assets
   - public example library;
   - template catalog;
   - integration guides;
   - contribution and compatibility rules.

## Boundaries

P6 must not be started as implementation work until earlier foundations are mature enough.

P6 must not silently change existing package semantics. Compatibility and migration rules must be explicit.

P6 must not promise external integrations or SDKs before their contracts are specified and tested.

## Consequences

- P6 tasks are tracked separately in `TODO-P6.md`.
- P6 roadmap is documented in `docs/roadmap/p6.md`.
- P6 implementation should only start after explicit authorization.
- Any breaking package schema change requires a separate ADR.
- Any externally exposed SDK or integration contract requires tests and compatibility fixtures.
