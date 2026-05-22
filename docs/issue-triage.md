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

For privacy or sensitive data concerns, avoid pasting secrets into public issues. Use sanitized evidence and reference the privacy model.
