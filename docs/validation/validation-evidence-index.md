# Doctor link Validation Evidence Index

## Latest Confirmed Cloud Validation

- Validation type: GitHub Actions Cloud Validation
- PR: `#110 Repository root cleanup`
- Merge commit: `09830b934d92c41509daa75b929d82081c6c827d`
- CI run: `#312`
- CI conclusion: `success`

## Checks

| Check | Result |
|---|---:|
| Python 3.10 | Passed |
| Python 3.11 | Passed |
| Python 3.12 | Passed |
| Ruff | Passed |
| Pytest | Passed |
| CLI smoke | Passed |
| E2E validation | Passed |
| P7 runtime validation | Passed |
| Wheel build | Passed |
| Installed wheel smoke | Passed |
| Package job | Passed |

## Key Validated Commands

Representative validation commands include:

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-report=term-missing --cov-report=xml
python -m build
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
doctor-link --help
doctor-link strategy validate . --json
```

## Key Runtime Areas Covered

- Package installation.
- CLI entrypoint.
- Diagnostic package generation.
- Verification write-back.
- Local workbench build.
- AI handoff.
- CI report generation.
- Distribution readiness.
- Adapter and plugin dry-run / explicit run boundaries.
- Integrity and privacy gates.
- Local knowledge and archive helpers.

## Evidence Interpretation

This evidence proves repository-side CI validation in GitHub Actions.

It does not prove local Mac validation, offline deployment validation, customer-environment validation, production acceptance, PyPI release readiness, or hosted platform readiness.
