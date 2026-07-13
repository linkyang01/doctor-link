# Doctor link Release Candidate Checklist

Status: `v0.1.3 locally and cloud validated, merged, tagged, and published on GitHub`

## Repository and CI

- [x] Main branch contains P0-P7 implementation and post-P7 hardening.
- [x] Root directory cleanup completed.
- [x] Completed TODO trackers archived under `docs/archive/completed-todos/`.
- [x] English and Chinese README files moved under `docs/readme/`.
- [x] Root `README.md` is a lightweight entrypoint.
- [x] Current implementation commit pushed and GitHub Actions CI passed (PR #140, run 29245883700).
- [x] Current repaired implementation passed on Python 3.10 in cloud CI.
- [x] Current repaired implementation passed on Python 3.11 in cloud CI.
- [x] Current repaired implementation passed on Python 3.12 locally and in cloud CI.
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
- [x] Current repaired implementation package job passed in cloud CI.
- [x] Linux, macOS, and Windows smoke jobs passed in cloud CI.

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
- [x] GitHub Release `v0.1.2` published (2026-07-13, workflow `29223309411`).
- [x] GitHub Release `v0.1.3` published (2026-07-13, workflow `29246045227`).
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
- [x] GitHub-hosted Linux, macOS, and Windows validation.
- [ ] PyPI publication (optional).

## Decision

Doctor link version `0.1.3` passed local validation and the complete configured GitHub Actions matrix on 2026-07-13: 298 tests, 85.25% branch-aware coverage, and all 62 public CLI routes through a clean installed wheel. PR `#140` was merged as commit `fa779da`, explicit GitHub publication authorization was received, and [GitHub Release `v0.1.3`](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.3) was published with wheel and source-distribution assets by workflow `29246045227`. PyPI publication remains optional and was not performed.

Customer delivery or production-like environments that differ materially from the recorded Mac setup should still be validated on those targets before handoff.
