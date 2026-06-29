# Doctor link Local Validation Status

Status: local Mac validation recorded; additional target environments optional

## Current Situation

Local Mac validation was executed successfully on 2026-06-29. The full validation sequence passed on the developer machine.

Recorded evidence:

- `docs/p5.10-local-validation.md`

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

Local Mac validation (2026-06-29) includes:

- ruff static checks;
- pytest with coverage (217 passed, 84%);
- wheel and source distribution build;
- `scripts/validate_doctor_link.sh`;
- `scripts/e2e_validate.sh`;
- `scripts/p7_runtime_validate.sh`;
- installed wheel smoke test.

## What Remains Optional

The following target environments have not been recorded yet:

- validation on an offline workstation;
- validation on a customer delivery environment;
- validation on a production-like target environment.

These are optional follow-ups when Doctor link must be proven on environments that differ from the recorded Mac setup.

## Local Validation Record (Mac)

```text
Date: 2026-06-29
Machine / OS: MacBook Air, macOS 25.5.0 (Darwin 25.5.0 arm64)
Python version: 3.11.15
Commit SHA: 14b552c24feff1f2e28a8cb68e352e9d5b0c76af
Branch: main
Validation result: success
Notes: full validation sequence passed; see docs/p5.10-local-validation.md
```

## Recommended Validation Command Sequence

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

## Release Guidance

Doctor link may be treated as cloud-CI-certified, release-candidate-ready, and locally validated on the developer Mac.

Before formal customer delivery, production deployment, PyPI publication, or stable release declaration on a different target environment, rerun this validation sequence on that environment and append a record to `docs/p5.10-local-validation.md`.