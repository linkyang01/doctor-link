# Doctor link Cloud Validation Certificate

Status: v0.3.0 candidate cloud validation passed; merge and publication pending

## Certification Type

This certificate records GitHub Actions cloud validation for Doctor link.

It does not claim target customer environment validation, production validation, PyPI publication, hosted service readiness, or enterprise deployment acceptance. GitHub Release `v0.2.0` remains the latest published version; `v0.3.0` is an unmerged candidate.

## Project

- Project: Doctor link
- Repository: `linkyang01/doctor-link`
- Validation type: GitHub Actions Cloud Validation
- Validation scope: repository-side CI and package validation
- Current source candidate: `0.3.0` (validated code commit `c9426e7`, PR `#147`)
- Local Mac validation: passed (2026-07-13); additional target environments optional

## Cloud Validation Evidence

Current `v0.3.0` candidate validation:

- PR: `#147 Prepare v0.3.0 JavaScript and TypeScript solve`
- Validated code commit: `c9426e7bdb5cd1fdf4f7223e14c1635005f1453f`
- CI run: [`29263187097`](https://github.com/linkyang01/doctor-link/actions/runs/29263187097)
- CI result: `success`

Validated jobs and checks:

- Python 3.10: passed
- Python 3.11: passed
- Python 3.12: passed
- Python 3.13: passed
- Python 3.14: passed
- Ruff static checks: passed
- Pytest: passed
- CLI smoke tests: passed
- E2E validation: passed
- P7 runtime validation: passed
- Wheel build: passed
- Installed wheel smoke test: passed
- Installed wheel full-capability lab: 63/63 routes, 72 invocations, 10 complex scenarios
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

Doctor link `v0.3.0` candidate code commit `c9426e7` passed all ten repository-side GitHub Actions jobs, including Python 3.10 through 3.14 and JavaScript solve regressions on Ubuntu, macOS, and Windows. PR `#147` is open and ready for review; it has not been merged, tagged, or published.

The previous [GitHub Release `v0.2.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.2.0) was published from merged commit `40a547c` by [release workflow 29256955705](https://github.com/linkyang01/doctor-link/actions/runs/29256955705). PyPI publication was disabled and not performed.

Local Mac validation was rerun on 2026-07-13. PyPI publication, customer delivery, or production handoff on a different target environment should still be preceded by validation on that environment when it differs materially from the recorded Mac and GitHub runner setup.
