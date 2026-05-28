# Doctor link P5.10 TODO

Goal: local validation hardening before any P6 authorization decision.

P5.10 is a validation and documentation phase only. It must not introduce product features, publish a release, create a GitHub Release, create a release tag, publish to PyPI, change repository permissions, introduce paid cloud services, add external account systems, or start P6 implementation.

## Work items

- [x] Confirm P5.9 closeout has merged.
- [x] Keep new feature development paused.
- [x] Define local full-validation command sequence.
- [x] Define expected validation artifacts.
- [x] Define failure triage workflow.
- [x] Define P6 authorization gate.
- [x] Add `docs/p5.10-local-validation.md`.
- [ ] Run the full validation sequence locally and record the actual result.
- [ ] Update `docs/p5.10-local-validation.md` with the actual local run date, environment, and outcome.
- [ ] Decide whether to authorize P6 planning after local validation passes.

## Required local validation commands

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
```

## Completion criteria

P5.10 is complete only after the full local validation sequence is run outside GitHub Actions and the actual environment, result, and artifacts are recorded in `docs/p5.10-local-validation.md`.

## P6 gate

P6 must not start until P5.10 validation is recorded as passed. If P6 is later authorized, it must begin with P6.1 Diagnostic Package Schema v1 and must not begin with Web platform, cloud service, account system, or ecosystem marketplace implementation.
