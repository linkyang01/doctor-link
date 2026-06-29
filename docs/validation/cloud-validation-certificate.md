# Doctor link Cloud Validation Certificate

Status: Cloud CI Certified / Release Candidate Ready

## Certification Type

This certificate records GitHub Actions cloud validation for Doctor link.

It does not claim local machine validation, target customer environment validation, production validation, PyPI publication, GitHub Release publication, release tag creation, hosted service readiness, or enterprise deployment acceptance.

## Project

- Project: Doctor link
- Repository: `linkyang01/doctor-link`
- Validation type: GitHub Actions Cloud Validation
- Validation scope: repository-side CI and package validation
- Recommended release status: `v0.1.0-rc.1 ready`
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
- GitHub Release creation;
- release tag creation;
- PyPI publication.

## Certification Conclusion

Doctor link has passed repository-side GitHub Actions cloud validation and is suitable for `v0.1.0-rc.1` release candidate preparation.

Local Mac validation has been recorded (2026-06-29). Formal external release, PyPI publication, customer delivery, or production handoff on a different target environment should still be preceded by validation on that environment when it differs materially from the recorded Mac setup.
