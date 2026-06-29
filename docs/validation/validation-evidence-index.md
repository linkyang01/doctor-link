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

## Latest Confirmed Local Mac Validation

- Validation type: Local Mac validation
- Date: 2026-06-29
- Machine: MacBook Air, macOS 25.5.0 (arm64)
- Python: 3.11.15
- Commit: `14b552c24feff1f2e28a8cb68e352e9d5b0c76af`
- Branch: `main`
- Result: `success`
- Record: `docs/p5.10-local-validation.md`

| Check | Result |
|---|---:|
| Ruff | Passed |
| Pytest | Passed (217 tests, 84% coverage) |
| Wheel build | Passed |
| validate_doctor_link.sh | Passed |
| e2e_validate.sh | Passed |
| p7_runtime_validate.sh | Passed |
| Installed wheel smoke | Passed |

## Evidence Interpretation

Cloud validation evidence proves repository-side CI validation in GitHub Actions.

Local Mac validation evidence proves the full validation sequence passes on the developer Mac with Python 3.11.15.

This combined evidence does not prove offline deployment validation, customer-environment validation, production acceptance, PyPI release readiness, or hosted platform readiness on environments other than the recorded Mac setup.
