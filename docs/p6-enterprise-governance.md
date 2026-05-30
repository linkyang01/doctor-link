# P6.8 Enterprise Archive and Governance Model

Status: planning specification only

## Scope

P6.8 defines the enterprise archive and governance model for Doctor link diagnostic packages.

This phase does not implement a real enterprise archive system, hosted approval workflow, cloud service, account system, identity integration, or release publishing.

## Goals

The goals are to define:

- diagnostic package retention policy format;
- archive metadata model;
- project-level audit trail model;
- reviewer roles;
- approval states;
- team review workflow;
- enterprise export policy;
- deletion and retention boundaries.

## Diagnostic package retention policy format

A future retention policy should include:

```text
policy_id
package_privacy_level
retention_days
archive_required
review_required
legal_hold_allowed
delete_after_expiry
```

Recommended retention defaults:

- `public`: short or example-driven retention after sanitization.
- `internal`: project-defined retention.
- `confidential`: longer retention with review controls.
- `restricted`: strict review and explicit deletion rules.

## Archive metadata model

A future archive record should include:

```text
archive_id
package_id
project
created_at
archived_at
archived_by
privacy_level
retention_policy_id
storage_location
checksum
status
```

Rules:

- Archive metadata should not contain raw secrets.
- Storage locations should be logical labels, not necessarily direct filesystem paths.
- Checksums should refer to exported archive content.
- Archive metadata should be schema-versioned.

## Project-level audit trail model

A future audit trail should record:

```text
event_id
event_type
actor
occurred_at
package_id
summary
related_files
```

Recommended event types:

```text
created
validated
redacted
review_requested
approved
rejected
exported
archived
deleted
retention_extended
```

Rules:

- Audit trails should be append-only.
- Audit records should avoid embedding sensitive evidence content.
- Audit records should reference package evidence by id or path.

## Reviewer roles

Recommended reviewer roles:

```text
owner
maintainer
security_reviewer
privacy_reviewer
legal_reviewer
external_reviewer
```

Rules:

- Restricted packages should require security or privacy review before export.
- External review should be allowed only after redaction review.
- Role names should be recorded as metadata, not as a real identity system in this phase.

## Approval states

Recommended approval states:

```text
draft
pending_review
changes_requested
approved
rejected
expired
revoked
```

Rules:

- Export should require `approved` for confidential or restricted packages.
- Revoked approvals should block future export.
- Expired approvals should require re-review.

## Team review workflow

A future review workflow should follow:

1. Package is created.
2. Schema validation runs.
3. Privacy and redaction status is reviewed.
4. Review request is created.
5. Reviewer approves, rejects, or requests changes.
6. Export or archive proceeds only if policy allows.
7. Audit trail records the decision.

## Enterprise export policy

A future export policy should include:

```text
policy_id
allowed_privacy_levels
allowed_destinations
review_required
redaction_required
signature_required
external_handoff_allowed
retention_policy_id
```

Rules:

- Restricted packages default to external export blocked.
- Confidential packages require review and redaction status.
- Signed package export may be required by policy.
- External AI handoff must respect privacy and security levels.

## Deletion and retention boundaries

Deletion rules:

- Deleting archive metadata does not necessarily delete source evidence.
- Deleting package evidence should be explicit and audited.
- Legal hold should prevent deletion until removed.
- Expired packages should be reviewed before deletion when privacy level is confidential or restricted.

Retention rules:

- Retention should be policy-driven.
- Retention changes should be audited.
- Retention should not override legal hold.

## Non-goals

P6.8 does not include:

- real archive storage implementation;
- enterprise identity integration;
- real access control;
- hosted approval workflow;
- cloud archive service;
- account system;
- public release publishing;
- PyPI publishing.
