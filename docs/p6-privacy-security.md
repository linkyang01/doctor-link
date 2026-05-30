# P6.7 Privacy and Security Level Specification

Status: planning specification only

## Scope

P6.7 defines privacy and security levels for Doctor link diagnostic packages, evidence, redaction, export, enterprise sharing, and external AI handoff warnings.

This phase does not implement a real permission system, account system, cloud service, hosted sharing platform, enterprise access control, or release publishing.

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
public
internal
confidential
restricted
```

Definitions:

- `public`: safe for public examples after review.
- `internal`: safe inside the project or organization.
- `confidential`: contains sensitive business, system, or customer context.
- `restricted`: contains credentials, secrets, regulated data, or highly sensitive evidence and must not be exported without explicit review.

## Evidence sensitivity levels

Recommended evidence sensitivity levels:

```text
low
medium
high
critical
```

Examples:

- `low`: file names, generic error summaries, public build output.
- `medium`: local paths, internal component names, configuration summaries.
- `high`: customer data, system topology, private logs, internal URLs.
- `critical`: secrets, credentials, tokens, private keys, regulated data.

## Redaction levels

Recommended redaction levels:

```text
none
standard
strict
locked
```

Definitions:

- `none`: no automated redaction applied.
- `standard`: emails, obvious tokens, and common secrets are redacted.
- `strict`: paths, URLs, hostnames, and structured identifiers may also be redacted.
- `locked`: export should be blocked until manual review is completed.

## Export safety levels

Recommended export safety levels:

```text
safe
review_required
blocked
```

Rules:

- `safe`: package can be exported after normal validation.
- `review_required`: package requires explicit human review before export.
- `blocked`: package must not be exported until sensitive evidence is removed or downgraded by review.

## Enterprise sharing policy model

A future enterprise sharing policy should include:

```text
policy_id
privacy_level
allowed_recipients
allowed_destinations
redaction_required
review_required
retention_days
external_handoff_allowed
```

Rules:

- Restricted packages should default to no external sharing.
- Confidential packages should require review before external handoff.
- Internal packages may be shared inside approved teams.
- Public packages require prior sanitization.

## External AI handoff privacy warning rules

External AI handoff should warn when:

- package privacy level is `confidential` or `restricted`;
- evidence sensitivity level is `high` or `critical`;
- redaction level is `none` or incomplete;
- external service use is possible;
- target tool does not support local-only mode;
- package contains user assertions with sensitive detail;
- package contains raw logs or attachments.

## Sensitive evidence preview restrictions

Sensitive preview should follow these rules:

- Critical evidence should be hidden by default.
- High-sensitivity evidence should show metadata before content.
- Preview should display redaction status.
- Preview should warn before external handoff.
- Preview should not render credentials, tokens, or private keys.

## Privacy documentation requirements

Every future export or integration feature should document:

- what files are included;
- what evidence may be sensitive;
- whether redaction is applied;
- whether external services may receive data;
- whether local-only execution is supported;
- what review steps are required;
- what data is retained.

## Non-goals

P6.7 does not include:

- real access control implementation;
- enterprise identity integration;
- cloud sharing;
- hosted review workflow;
- account system;
- external service integration;
- public release publishing;
- PyPI publishing.
