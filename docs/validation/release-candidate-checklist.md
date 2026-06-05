# Doctor link Release Candidate Checklist

Status: `v0.1.0-rc.1 ready after cloud validation`

## Repository and CI

- [x] Main branch contains P0-P7 implementation and post-P7 hardening.
- [x] Root directory cleanup completed.
- [x] Completed TODO trackers archived under `docs/archive/completed-todos/`.
- [x] English and Chinese README files moved under `docs/readme/`.
- [x] Root `README.md` is a lightweight entrypoint.
- [x] GitHub Actions CI passed.
- [x] Python 3.10 passed.
- [x] Python 3.11 passed.
- [x] Python 3.12 passed.
- [x] Ruff passed.
- [x] Pytest passed.
- [x] CLI smoke tests passed.
- [x] E2E validation passed.
- [x] P7 runtime validation passed.
- [x] Wheel build passed.
- [x] Installed wheel smoke test passed.
- [x] Package job passed.

## Runtime Capability Coverage

- [x] Evidence hardening.
- [x] Local workbench hardening.
- [x] AI handoff runtime.
- [x] CI and operational automation.
- [x] Distribution readiness checks.
- [x] Adapter runtime with explicit `--allow-run`.
- [x] Plugin runtime with explicit `--allow-run`.
- [x] Integrity verification with strict mode.
- [x] Privacy scan / redaction / export gates.
- [x] Local knowledge index.
- [x] Local archive helpers.

## Release Boundaries

- [x] No GitHub Release created.
- [x] No release tag created.
- [x] No PyPI publication performed.
- [x] No hosted service introduced.
- [x] No external account system introduced.
- [x] No telemetry introduced.
- [x] No marketplace introduced.
- [x] No real signing key management introduced.
- [x] No hosted archive service introduced.
- [x] No hosted diagnostic knowledge base introduced.

## Pending Items Before Formal External Release

- [ ] Local / target-environment validation record.
- [ ] Final release notes for `v0.1.0-rc.1`.
- [ ] Explicit authorization before creating a release tag.
- [ ] Explicit authorization before creating a GitHub Release.
- [ ] Explicit authorization before PyPI publication.

## Decision

Doctor link is suitable for `v0.1.0-rc.1` release candidate status based on cloud CI validation.

It is not yet certified as locally validated or customer-environment validated.
