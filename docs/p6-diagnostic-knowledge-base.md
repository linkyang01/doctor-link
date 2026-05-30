# P6.9 Cross-project Diagnostic Knowledge Base

Status: planning specification only

## Scope

P6.9 defines the cross-project diagnostic knowledge base model for Doctor link.

This phase does not implement a real knowledge base service, hosted indexing, cloud aggregation, external account system, marketplace, telemetry collection, or release publishing.

## Goals

The goals are to define:

- problem taxonomy;
- reproduction pattern taxonomy;
- verification pattern taxonomy;
- repair outcome taxonomy;
- recurring failure signature model;
- AI repair quality metrics;
- project health trend metrics;
- knowledge export format;
- privacy boundaries for cross-project learning.

## Problem taxonomy

A future knowledge base should classify problems using stable categories.

Recommended problem categories:

```text
build_failure
test_failure
runtime_error
configuration_error
dependency_error
data_error
performance_regression
security_risk
usability_issue
unknown
```

Each problem taxonomy entry should include:

```text
problem_id
category
summary
symptoms
affected_components
severity
confidence
source_package_ids
```

## Reproduction pattern taxonomy

A reproduction pattern should describe how a failure is triggered.

Recommended reproduction pattern types:

```text
command
unit_test
integration_test
manual_steps
fixture_based
environment_specific
intermittent
not_reproduced
```

Each reproduction pattern should include:

```text
pattern_id
kind
commands
steps
required_files
environment_constraints
expected_signal
```

## Verification pattern taxonomy

A verification pattern should describe how a fix or diagnosis is validated.

Recommended verification pattern types:

```text
static_check
unit_test
integration_test
end_to_end_test
schema_validation
conformance_validation
manual_review
security_review
privacy_review
```

Each verification pattern should include:

```text
verification_id
kind
commands
expected_result
required_evidence
review_required
```

## Repair outcome taxonomy

A repair outcome should record what happened after diagnosis.

Recommended outcomes:

```text
fixed
partially_fixed
not_fixed
won_t_fix
cannot_reproduce
needs_more_evidence
blocked
```

Each repair outcome should include:

```text
outcome_id
status
summary
files_changed
evidence_used
verification_result
remaining_risks
```

## Recurring failure signature model

A recurring failure signature should identify repeated or similar failures across packages.

Recommended signature fields:

```text
signature_id
category
normalized_message
affected_paths
command_pattern
dependency_pattern
environment_pattern
occurrence_count
first_seen
last_seen
confidence
```

Rules:

- Signatures should avoid storing raw secrets.
- Similarity should be explainable.
- Evidence should reference source package ids, not duplicate full sensitive content.

## AI repair quality metrics

Recommended AI repair quality metrics:

```text
repair_success_rate
verification_pass_rate
regression_rate
human_correction_rate
evidence_usage_rate
assertion_coverage_rate
reopen_rate
```

Rules:

- Metrics should be computed from recorded package evidence.
- Metrics should not imply correctness without verification.
- Human corrections should remain first-class signals.

## Project health trend metrics

Recommended project health metrics:

```text
package_count
open_problem_count
verified_fix_count
failed_verification_count
missing_evidence_count
schema_validity_rate
conformance_score_trend
recurring_failure_count
```

Rules:

- Health metrics should be explainable.
- Aggregated metrics should preserve privacy boundaries.
- Trends should link back to package-level evidence.

## Knowledge export format

A future knowledge export should include:

```text
schema_version
export_id
created_at
source_scope
problem_taxonomy
reproduction_patterns
verification_patterns
repair_outcomes
recurring_failure_signatures
metrics
privacy_boundaries
```

Export rules:

- Export should include only approved package-derived data.
- Export should not include raw restricted evidence.
- Export should preserve source package ids for traceability.
- Export should document privacy level and redaction status.

## Privacy boundaries for cross-project learning

Cross-project learning should follow these boundaries:

- No raw secrets should be copied into knowledge records.
- Restricted packages should be excluded by default.
- Confidential packages require explicit review before aggregation.
- Package ids may be referenced only when policy allows.
- Aggregated patterns should avoid identifying customers, users, or private systems.
- External AI handoff must follow P6.7 privacy rules.

## Non-goals

P6.9 does not include:

- real knowledge base storage implementation;
- cloud indexing;
- telemetry collection;
- hosted analytics;
- account system;
- enterprise identity integration;
- marketplace features;
- public release publishing;
- PyPI publishing.
