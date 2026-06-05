# Doctor link Local Validation Pending Notice

Status: pending local or target-environment validation

## Current Situation

Local or target-environment validation has not been executed yet because an appropriate local or delivery environment is currently unavailable.

## What Has Been Completed

Doctor link has completed repository-side cloud validation through GitHub Actions.

Confirmed cloud validation includes:

- static checks;
- pytest;
- multi-version Python matrix;
- CLI smoke tests;
- E2E validation;
- P7 runtime validation;
- wheel build;
- installed wheel smoke validation.

## What Remains Pending

The following is still pending:

- validation on the user's Mac;
- validation on an offline workstation;
- validation on a customer delivery environment;
- validation on a production-like target environment.

## Recommended Future Local Validation Command Sequence

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest pytest-cov build ruff

ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-report=term-missing --cov-report=xml
python -m build

bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

## Local Validation Record Template

```text
Date:
Machine / OS:
Python version:
Commit SHA:
Branch:
Validation result:
Notes:
```

## Release Guidance

Doctor link may be treated as cloud-CI-certified and release-candidate-ready.

Before formal customer delivery, production deployment, PyPI publication, or stable release declaration, a local or target-environment validation record should be added.
