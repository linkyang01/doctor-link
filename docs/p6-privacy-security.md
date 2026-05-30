# P6.7 Privacy and Security Level Specification

Status: planning specification only

## Scope

P6.7 defines the privacy and security level model for Doctor link diagnostic packages, evidence, redaction, export, enterprise sharing, external AI handoff warnings, sensitive evidence preview, and privacy documentation.

This phase does not implement a hosted permission system, account system, cloud service, Web platform, enterprise identity integration, marketplace, or public release publishing.

## Goals

The goals are to define:

- diagnostic package privacy levels;
- evidence sensitivity levels;
- redaction levels;
- export safety levels;
- enterprise sharing policy model;
- external AI handoff privacy warning rules;
- sensitive evidence preview restrictions;
- privacy documentation requirements.

## Diagnostic package privacy levels

Recommended package privacy levels:

```text
public-example
internal
confidential
restricted
```

### public-example

Use for sanitized examples that are safe to share publicly.

Requirements:

- no credentials;
- no personal data;
- no customer data;
- no private source code;
- no internal infrastructure names.

### internal

Use for ordinary internal project diagnosis.

Requirements:

- internal-only sharing;
- standard redaction;
- package owner review before external handoff.

### confidential

Use for packages containing sensitive project information.

Requirements:

- restricted sharing;
- stronger redaction;
- explicit external handoff warning;
- reviewer approval before export.

### restricted

Use for high-risk packages.

Requirements:

- no external handoff by default;
- no public artifact upload;
- reviewer approval required;
- sensitive evidence preview restrictions enabled.

## Evidence sensitivity levels

Recommended evidence sensitivity levels:

```text
low
medium
high
critical
```

Examples:

- `low`: generated summaries and non-sensitive test output.
- `medium`: file paths, dependency lists, project structure.
- `high`: logs, environment variables, private repository metadata.
- `critical`: credentials, secrets, tokens, regulated data, private customer data.

## Redaction levels

Recommended redaction levels:

```text
none
standard
strict
maximum
```

Rules:

- `none` is only acceptable for sanitized public examples.
- `standard` should remove common secrets and emails.
- `strict` should remove credentials, tokens, private hosts, and personal data.
- `maximum` should minimize raw evidence exposure and prefer summaries.

## Export safety levels

Recommended export safety levels:

```text
local-only
internal-share
external-ai
public-example
```

Rules:

- `local-only`: package should remain on the local machine.
- `internal-share`: package may be shared within an approved team.
- `external-ai`: package may be sent to an external AI tool only after review.
- `public-example`: package may be published as sanitized example material.

## Enterprise sharing policy model

A future enterprise policy should define:

```text
policy_id
allowed_privacy_levels
allowed_export_levels
required_redaction_level
requires_reviewer_approval
allowed_handoff_targets
retention_days
audit_required
```

Rules:

- Enterprise policy should never silently downgrade privacy level.
- External AI handoff should respect allowed targets.
- Review requirements should be explicit.
- Retention rules should be recorded in package metadata or archive metadata.

## External AI handoff privacy warning rules

External AI handoff should warn when:

- package privacy level is `confidential` or `restricted`;
- evidence sensitivity includes `high` or `critical`;
- redaction level is lower than policy requires;
- target tool may use external services;
- user assertions mention sensitive business context;
- logs or attachments are included;
- package has not been reviewed.

## Sensitive evidence preview restrictions

Sensitive evidence preview should follow these rules:

- Do not display critical evidence by default.
- Show summary and metadata before raw content.
- Require explicit confirmation before previewing high or critical evidence.
- Make redaction status visible.
- Preserve provenance so users know where evidence came from.
- Avoid copying sensitive values into generated summaries.

## Privacy documentation requirements

Every future privacy-aware package or integration should document:

- privacy level;
- evidence sensitivity summary;
- redaction level;
- export safety level;
- external handoff warnings;
- reviewer approval status;
- known privacy limitations;
- retention expectation.

## Non-goals

P6.7 does not include:

- hosted policy service;
- user account system;
- role-based access control implementation;
- enterprise SSO;
- cloud storage;
- external AI API integration;
- real approval workflow implementation;
- public release publishing;
- PyPI publishing.
