# P1 / P1+ Hardening TODO

P1 and P1+ are accepted as complete for the current diagnostic foundation scope.

This checklist tracks follow-up hardening work for assertion-to-test-to-verification traceability.

## Audit

- [x] Add P1/P1+ completion audit
- [x] Map capabilities to files, CLI commands, and CI smoke coverage

## Assertion Test Linkage

- [x] Add related assertion IDs to test records
- [x] Add `--assertion-id` to `doctor-link record`
- [x] Support multiple assertion IDs per test record
- [x] Preserve assertion linkage in doctor-report.json
- [x] Preserve assertion linkage in evidence/test-results
- [x] Add tests for assertion-linked test records
