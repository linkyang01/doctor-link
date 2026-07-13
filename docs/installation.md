# Installation and Local Run Guide

Doctor link is a Python CLI project. This guide explains how to clone the repository, install it locally, run the CLI, and validate that the project works on a local machine.

Install from source by default. Source version `0.1.2` is a locally validated release candidate, not a published GitHub Release or PyPI package. Do not use a `v0.1.2` release-asset URL until an explicitly authorized release has actually been published.

## 1. Requirements

Install these tools before starting:

- Git
- Python 3.10 or later
- pip
- A terminal that supports shell scripts

Recommended Python versions:

- Python 3.10
- Python 3.11
- Python 3.12

Cloud validation has passed on GitHub Actions with Python 3.10, 3.11, and 3.12. Local validation should use one of these versions.

## 2. Clone the repository

Choose a local working directory, then run:

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
```

If the repository already exists locally, update it:

```bash
cd doctor-link
git pull origin main
```

Confirm the branch and commit:

```bash
git branch --show-current
git rev-parse HEAD
```

Expected branch:

```text
main
```

## 3. Create a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

### Windows Git Bash

```bash
py -3 -m venv .venv
source .venv/Scripts/activate
python --version
```

Expected result:

```text
Python 3.10+
```

## 4. Install Doctor link from source

Run from the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

The editable install registers the CLI command:

```bash
doctor-link --help
```

If the command prints help text, the CLI entrypoint is installed successfully.

### Install a locally built wheel

```bash
python -m pip install build
python -m build
python -m pip install dist/doctor_link-0.1.2-py3-none-any.whl
doctor-link --version
```

### Install from PyPI after a future authorized publication

```bash
pip install doctor-link==<published-version>
doctor-link --version
```

## 5. Quick smoke test

Run:

```bash
doctor-link --help
doctor-link init DoctorWorkspace
doctor-link strategy validate . --json
doctor-link preflight . --json
```

The quick smoke test passes if all three commands exit successfully.

## 6. Full local validation

Install validation tools:

```bash
python -m pip install pytest pytest-cov build ruff
```

Run the complete validation sequence:

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-report=term-missing --cov-report=xml
python -m build
python scripts/validate_distribution_contents.py dist
python -m twine check dist/*
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
```

The validation passes when every command exits successfully.

Expected important outputs include:

```text
coverage.xml
dist/*.whl
dist/*.tar.gz
DoctorLinkValidation/DoctorReports/
DoctorLinkValidation/DoctorReports/project-health.json
.doctorlink-e2e/DoctorReports/
.doctorlink-e2e/DoctorReports/project-health.json
```

The usability validation script should finish with:

```text
Doctor link validation completed successfully.
```

## 7. Build a package locally

Install build tooling if not already installed:

```bash
python -m pip install build
```

Build the package:

```bash
python -m build
```

Expected outputs:

```text
dist/doctor_link-<version>-py3-none-any.whl
dist/doctor_link-<version>.tar.gz
```

## 8. Test the built wheel in a clean environment

Create another temporary virtual environment outside the current one:

```bash
python3 -m venv .venv-wheel-test
source .venv-wheel-test/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/*.whl
doctor-link --help
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv-wheel-test
.\.venv-wheel-test\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install dist\*.whl
doctor-link --help
```

If `doctor-link --help` works after wheel installation, the built package can be installed and executed.

## 9. Optional local validation record

After a successful local run, record the environment in `docs/p5.10-local-validation.md`:

```text
Date:
Machine / OS:
Python version:
Commit SHA:
Branch:
Validation result:
Notes:
```

Useful commands:

```bash
python --version
git branch --show-current
git rev-parse HEAD
```

On macOS, also run:

```bash
sw_vers
```

## 10. Common problems

### `doctor-link: command not found`

Make sure the virtual environment is active and the package was installed:

```bash
source .venv/bin/activate
python -m pip install -e .
doctor-link --help
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
doctor-link --help
```

### `python: command not found`

Try `python3` on macOS or Linux:

```bash
python3 --version
```

On Windows, try:

```powershell
py -3 --version
```

### `pip` installs into the wrong Python

Use `python -m pip` instead of `pip`:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

### PowerShell blocks activation

If PowerShell refuses to activate the virtual environment, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Validation scripts fail on Windows PowerShell

The validation scripts are shell scripts. Use Git Bash, WSL, macOS, Linux, or GitHub Actions for the full shell-script validation path.

## 11. Cloud validation status

The current `main` branch has passed GitHub Actions cloud validation.

Recorded cloud validation:

```text
Workflow: P5.10 Manual Validation #1
Branch: main
Commit: 8abeb8b
Runner: GitHub Actions ubuntu-latest
Job: Manual P5.10 validation
Result: success
```

Cloud validation confirms that the project can run static checks, tests with coverage, package build, usability validation, and end-to-end validation in GitHub Actions.

Local validation is still recommended when you need to prove the project on a specific workstation or delivery environment.

## 12. Boundaries

The following actions require separate explicit authorization:

- Do not publish to PyPI without explicit authorization.
- Do not create a GitHub Release without explicit authorization.
- Do not tag a public release without explicit authorization.
- Do not change repository permissions without explicit authorization.
- Do not introduce paid cloud services without explicit authorization.
- Do not introduce external account systems without explicit authorization.
- Do not start P6 implementation without explicit authorization.

This guide only covers local source installation, local package build, and local validation.
