# Doctor link Cloud Validation Certificate

Status: Current repaired implementation cloud validation passed

## Certification Type

This certificate records GitHub Actions cloud validation for Doctor link.

It does not claim target customer environment validation, production validation, PyPI publication, hosted service readiness, or enterprise deployment acceptance. GitHub Release `v0.2.0` was published after this validation succeeded.

## Project

- Project: Doctor link
- Repository: `linkyang01/doctor-link`
- Validation type: GitHub Actions Cloud Validation
- Validation scope: repository-side CI and package validation
- Current source candidate: `0.2.0` (release candidate commit `76e3966`, PR `#145`)
- Local Mac validation: recorded (2026-06-29); additional target environments optional

## Cloud Validation Evidence

Current repaired implementation validation:

- PR: `#145 Prepare v0.2.0 release`
- Release candidate commit: `76e396631caff79e7aee4eb1cb70d6a89aea1dd8`
- CI run: [`29256743976`](https://github.com/linkyang01/doctor-link/actions/runs/29256743976)
- CI result: `success`

Validated jobs and checks:

- Python 3.10: passed
- Python 3.11: passed
- Python 3.12: passed
- Ruff static checks: passed
- Pytest: passed
- CLI smoke tests: passed
- E2E validation: passed
- P7 runtime validation: passed
- Wheel build: passed
- Installed wheel smoke test: passed
- Installed wheel full-capability lab: 63/63 routes, 71 invocations, 9 complex scenarios
- Package validation job: passed
- Security checks: passed
- Ubuntu smoke: passed
- macOS smoke: passed
- Windows smoke: passed

## Certified Scope

The cloud validation certifies that the repository can:

- install dependencies in GitHub Actions runners;
- run static checks;
- run automated tests;
- build wheel and source distributions;
- install the built wheel;
- execute the `doctor-link` CLI after installation;
- run standard E2E validation;
- run P7 runtime validation;
- preserve local-first release and security boundaries.

## Boundaries

This certificate does not certify:

- offline workstation validation;
- customer delivery environment validation;
- production deployment readiness;
- hosted Web platform readiness;
- cloud synchronization;
- external account system;
- telemetry;
- marketplace;
- real signing keys or key management;
- hosted enterprise archive;
- hosted diagnostic knowledge base;
- PyPI publication.

## Certification Conclusion

Doctor link passed repository-side GitHub Actions cloud validation. PR `#145` was subsequently merged as commit `40a547c`, and [GitHub Release `v0.2.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.2.0) was published with wheel and sdist assets by [release workflow 29256955705](https://github.com/linkyang01/doctor-link/actions/runs/29256955705). The release workflow installed the final wheel and reran the full capability lab before tagging. PyPI publication was disabled and not performed.

Local Mac validation has been recorded (2026-06-29). PyPI publication, customer delivery, or production handoff on a different target environment should still be preceded by validation on that environment when it differs materially from the recorded Mac setup.
