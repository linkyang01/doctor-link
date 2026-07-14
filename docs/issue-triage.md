# Issue Triage Guide

Use this guide to classify Doctor link issues.

## Triage labels

Suggested labels:

- `bug`: incorrect behavior.
- `docs`: documentation issue.
- `enhancement`: product improvement.
- `privacy`: sensitive data or redaction concern.
- `pipeline`: P4 automated diagnosis workflow.
- `ai-handoff`: AI Coding collaboration workflow.
- `release`: release readiness or packaging.

## Triage workflow

1. Confirm the issue summary.
2. Ask for or create a diagnostic package when useful.
3. Check whether a user assertion is present.
4. Identify missing evidence.
5. Identify reproduction steps.
6. Define verification criteria.
7. Route to the right phase or component.

## Closure rule

An issue should not be closed only because an AI tool claims it is fixed. Verification evidence is required.

## Security issues

For vulnerabilities or sensitive privacy failures, do not paste details into public Issues. Route the reporter to GitHub private vulnerability reporting and `SECURITY.md`. Ordinary privacy usability questions may use sanitized evidence and reference the privacy model.

## Public intake

- Incorrect behavior uses `.github/ISSUE_TEMPLATE/bug_report.yml`.
- Product improvements use `.github/ISSUE_TEMPLATE/feature_request.yml`.
- Diagnostic investigations may use `.github/ISSUE_TEMPLATE/diagnostic_issue.yml`.
- Support expectations and preparation steps are defined in `SUPPORT.md`.
