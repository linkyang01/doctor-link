# Doctor link Cloud Validation Certificate

Status: Historical certificate; current repaired commit requires cloud revalidation

## Certification Type

This certificate records GitHub Actions cloud validation for Doctor link.

It does not claim target customer environment validation, production validation, PyPI publication, hosted service readiness, or enterprise deployment acceptance. The evidence below applies to the recorded historical commit, not automatically to the repaired 2026-07-13 working tree. GitHub Release `v0.1.2` is not currently published.

## Project

- Project: Doctor link
- Repository: `linkyang01/doctor-link`
- Validation type: GitHub Actions Cloud Validation
- Validation scope: repository-side CI and package validation
- Current source candidate: `0.1.2` (local validation passed 2026-07-13; cloud revalidation pending)
- Local Mac validation: recorded (2026-06-29); additional target environments optional

## Cloud Validation Evidence

Latest confirmed successful validation after repository root cleanup:

- PR: `#110 Repository root cleanup`
- Merge commit: `09830b934d92c41509daa75b929d82081c6c827d`
- CI run: `#312`
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
- Package validation job: passed

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

Doctor link has passed repository-side GitHub Actions cloud validation. GitHub Release `v0.1.0-rc.1` is published with wheel and sdist assets (2026-06-29).

Local Mac validation has been recorded (2026-06-29). PyPI publication, customer delivery, or production handoff on a different target environment should still be preceded by validation on that environment when it differs materially from the recorded Mac setup.
