# Doctor link Cloud Validation Certificate

Status: v0.3.0 cloud validation and GitHub Release publication passed

## Certification Type

This certificate records GitHub Actions cloud validation for Doctor link.

It does not claim target customer environment validation, production validation, PyPI publication, hosted service readiness, or enterprise deployment acceptance. GitHub Release `v0.3.0` is the latest published version.

## Project

- Project: Doctor link
- Repository: `linkyang01/doctor-link`
- Validation type: GitHub Actions Cloud Validation
- Validation scope: repository-side CI and package validation
- Published version: `0.3.0` (merge commit `e0224cc`, tag `v0.3.0`)
- Local Mac validation: passed (2026-07-13); additional target environments optional

## Cloud Validation Evidence

Current `v0.3.0` validation:

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

Doctor link `v0.3.0` product commit `c9426e7` passed all ten repository-side GitHub Actions jobs, including Python 3.10 through 3.14 and JavaScript solve regressions on Ubuntu, macOS, and Windows. Final PR head `45f3d52` passed the same matrix in run `29299016223`. PR `#147` merged as `e0224cc`, and release workflow `29299367180` rebuilt and validated the distributions before creating the immutable `v0.3.0` tag and publishing the GitHub Release assets.

The published wheel SHA-256 is `cb0bba0a6be6187bb18daa0ecac36d6804bb9bc1571b021fee36b4d62b0335ad`; the source archive SHA-256 is `fb2b767d7c5cd8ab25a73656ffb2f6197c930579f4553b4344d4be9b79135c34`. Both downloaded assets passed distribution-content and Twine validation, and the wheel passed the 63/63 installed-package lab. PyPI publication was disabled and not performed.

Local Mac validation was rerun on 2026-07-13. PyPI publication, customer delivery, or production handoff on a different target environment should still be preceded by validation on that environment when it differs materially from the recorded Mac and GitHub runner setup.
