# Platform Integration Roadmap

This roadmap plans the product layer beyond Doctor link's completed local-first diagnostic runtime. GitHub/AI connections, team collaboration, and cloud governance are separate delivery stages. They do not change the local package format into a cloud-only dependency and do not block the current local release.

## Product principles

1. Local-first remains a supported operating mode with no required account, telemetry, or hosted service.
2. Every external write requires explicit scope, actor identity, authorization, and an audit record.
3. Diagnostic packages remain portable across AI tools and source-control providers.
4. Cloud services receive the minimum required evidence, after privacy and integrity gates pass.
5. Provider-specific behavior lives behind Adapter/Plugin interfaces rather than the core diagnostic model.

## Delivery sequence

| Phase | Outcome | Depends on | Release gate |
| --- | --- | --- | --- |
| P0 Integration foundation | Stable provider-neutral contracts, consent, identity, audit, and retry model | Current local runtime | No external write without preview and audit |
| P1 GitHub and AI direct connections | Import CI/issue context and deliver reviewed handoffs to selected AI tools | P0 | Read-only by default; writes explicitly approved |
| P2 Team collaboration | Shared case queue, roles, comments, assignments, approvals, and activity history | P0, P1 identity model | Tenant/workspace isolation and permission tests |
| P3 Cloud governance | Enterprise identity, key management, retention, regional policy, audit export, backup and recovery | P2 | Security review, threat model, DR exercise, compliance evidence |

## P0 — Integration foundation

### Scope

- define provider-neutral objects for repository references, issues, pull requests, CI runs, AI sessions, approvals, and external receipts;
- add connection profiles stored outside diagnostic packages, with secrets delegated to OS keychain or a managed secret store;
- introduce capability-scoped permissions such as `repository:read`, `ci:read`, `issue:write`, `pull_request:write`, and `ai_session:create`;
- standardize preview, confirmation, idempotency key, retry, timeout, cancellation, and rollback behavior;
- extend audit records with actor, provider, action, target, request hash, result, and external receipt URL;
- require privacy export and integrity checks before evidence can leave the local workspace.

### Acceptance criteria

- provider contract and JSON Schemas pass conformance fixtures;
- simulated duplicate requests do not create duplicate external writes;
- expired credentials, network loss, rate limits, cancellation, and partial provider outages return recoverable states;
- logs and receipts contain no access tokens or unredacted diagnostic content.

## P1 — GitHub and AI direct connections

### GitHub connector

- read repository metadata, linked issues/PRs, check runs, job logs, and diagnostic artifacts;
- create a local diagnostic case from a selected issue, PR, or failed workflow;
- produce a review preview before commenting, uploading an artifact, opening an issue, or updating a PR;
- attach Doctor link verification results and evidence indexes without uploading excluded files;
- retain GitHub run, job, issue, PR, comment, and artifact identifiers as external receipts.

### AI connector

- keep the existing handoff package as the provider-neutral source of truth;
- support Codex/OpenAI and additional tools through adapters that declare accepted context, size limits, and result schemas;
- create an AI repair session only after the user reviews files, boundaries, and requested work;
- import claimed fixes, changed-file lists, verification steps, and tool receipts back into the diagnostic package;
- never mark a repair verified solely because an AI provider reports success.

### Acceptance criteria

- read-only GitHub and AI previews work without write permissions;
- every external write has a before preview, explicit approval, immutable local audit record, and provider receipt;
- a failed or interrupted upload can be retried idempotently;
- AI results remain blocked until Doctor link's local evidence and assertion checks pass.

## P2 — Team collaboration

### Scope

- workspaces with `owner`, `maintainer`, `reviewer`, and `viewer` roles;
- shared diagnostic case queue with assignment, priority, status, labels, comments, and mentions;
- approval policies for sensitive export, AI handoff, external comments, and repair closure;
- optimistic concurrency controls and conflict-visible edits rather than last-write-wins;
- immutable activity stream plus exportable audit history;
- self-hosted deployment first, with offline package import/export retained.

### Acceptance criteria

- a role/permission matrix is covered by positive and negative tests;
- cross-workspace access and guessed identifiers cannot expose cases or artifacts;
- concurrent comments, assignments, and approvals preserve every authorized action;
- revoked users and expired sessions lose access immediately;
- a workspace can export its cases and audit trail without vendor lock-in.

## P3 — Cloud governance

### Scope

- tenant isolation, SSO through OIDC/SAML, SCIM lifecycle, MFA policy, and service accounts;
- RBAC with optional attribute and project policies;
- envelope encryption backed by KMS/HSM, key rotation, signed packages, and signature verification;
- configurable retention, legal hold, deletion evidence, data residency, and customer-managed storage;
- centralized policy distribution for privacy patterns, export rules, adapters, and AI providers;
- security event export, administrative audit, backups, restore drills, regional failover, and disaster recovery objectives;
- usage metering only after a documented privacy model and explicit product decision.

### Acceptance criteria

- independent threat model and penetration test close all critical/high findings;
- tenant-isolation tests cover application, storage, search, cache, logs, and background jobs;
- key rotation and revocation are demonstrated without losing authorized historical packages;
- retention/deletion workflows produce verifiable receipts;
- backup restoration and regional recovery meet declared RPO/RTO targets;
- hosted deployment has operational runbooks, incident response, status reporting, and rollback procedures.

## Recommended releases

1. `v0.1.3`: current local reliability, privacy-safe atomic export, migration, and resilience validation.
2. `v0.2.0`: P0 contracts plus read-only GitHub/AI connection previews.
3. `v0.3.0`: explicitly approved GitHub/AI writes with receipts and idempotent retry.
4. `v0.4.0`: self-hosted team collaboration beta.
5. `v1.0.0`: cloud governance only after security, isolation, recovery, and operational acceptance gates pass.

## Explicit non-goals for the current release

- no required cloud account;
- no automatic source-code push, PR merge, issue comment, or AI session creation;
- no background upload or telemetry;
- no claim of real enterprise RBAC, managed signing, or regulatory compliance before P3 acceptance.
