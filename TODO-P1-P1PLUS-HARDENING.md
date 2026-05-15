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

## Verification Coverage

- [x] Generate assertion test coverage in verification-result.json
- [x] Show assertion coverage in verification-plan.md
- [x] Mark missing assertion coverage as missing evidence or tests to rerun when appropriate
- [x] Add tests for assertion coverage verification

## Documentation

- [x] Keep README stable; P1/P1+ hardening details are documented in `docs/p1-p1plus-audit.md`
- [x] Update P1/P1+ audit after hardening is complete
- [ ] Merge PR #34 after CI passes or manual merge is performed
- [ ] Close Issue #31 after PR #34 is merged
