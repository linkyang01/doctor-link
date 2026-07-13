# Doctor link Release Candidate Checklist

Status: `v0.1.2 locally validated release candidate; cloud revalidation and publication pending`

## Repository and CI

- [x] Main branch contains P0-P7 implementation and post-P7 hardening.
- [x] Root directory cleanup completed.
- [x] Completed TODO trackers archived under `docs/archive/completed-todos/`.
- [x] English and Chinese README files moved under `docs/readme/`.
- [x] Root `README.md` is a lightweight entrypoint.
- [ ] Repaired commit pushed and GitHub Actions CI passed.
- [ ] Current repaired commit passed on Python 3.10 in cloud CI.
- [ ] Current repaired commit passed on Python 3.11 in cloud CI.
- [x] Current repaired commit passed locally on Python 3.12.
- [x] Ruff passed.
- [x] Pytest passed.
- [x] CLI smoke tests passed.
- [x] E2E validation passed.
- [x] P7 runtime validation passed.
- [x] Wheel build passed.
- [x] Source distribution build passed.
- [x] Wheel and source distribution content validation passed.
- [x] Twine metadata validation passed.
- [x] Dependency consistency and vulnerability checks passed.
- [x] Installed wheel smoke test passed.
- [ ] Current repaired commit package job passed in cloud CI.
- [x] Linux, macOS, and Windows smoke jobs configured; cloud execution pending.

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

- [x] Historical GitHub Release tag `v0.1.1` exists.
- [ ] GitHub Release `v0.1.2` published.
- [x] Release tag published (`v0.1.0-rc.1`).
- [ ] PyPI publication performed (optional; GitHub wheel is the primary install path).
- [x] No hosted service introduced.
- [x] No external account system introduced.
- [x] No telemetry introduced.
- [x] No marketplace introduced.
- [x] No real signing key management introduced.
- [x] No hosted archive service introduced.
- [x] No hosted diagnostic knowledge base introduced.

## Pending Items Before Broader Distribution

- [x] Local Mac validation record (2026-06-29).
- [x] Final release notes for `v0.1.0-rc.1`.
- [x] GitHub Release and tag published (`v0.1.0-rc.1`).
- [ ] Additional target-environment validation (optional, e.g. Windows).
- [ ] PyPI publication (optional).

## Decision

Doctor link source version `0.1.2` passed repaired local validation on 2026-07-13. It may be published only after the repaired commit is pushed, cloud CI passes, and explicit release authorization is given.

Customer delivery or production-like environments that differ materially from the recorded Mac setup should still be validated on those targets before handoff.
