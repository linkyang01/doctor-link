# Installation and Local Run Guide

Doctor link is a Python CLI project. This guide explains how to clone the repository, install it locally, run the CLI, and validate that the project works on a local machine.

Version `0.5.1` is available from [PyPI](https://pypi.org/project/doctor-link/) and the authorized [GitHub Release](https://github.com/linkyang01/doctor-link/releases/tag/v0.5.1). For an isolated command-line application install, `pipx` is recommended.

## 1. Requirements

Install these tools before starting:

- Git
- Python 3.10 or later
- pip
- A terminal that supports shell scripts

For automatic repair of a JavaScript/TypeScript project, also install:

- Node.js compatible with that project;
- the package manager selected by its `packageManager` field or lockfile (`npm`, `pnpm`, Yarn, or Bun).

These Node.js tools are optional when Doctor link is used only for Python projects or for diagnostic-package workflows.

Recommended Python versions:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

The `v0.5.1` CI and release workflow validated Python 3.10 through 3.14. Local use should select one of these versions.

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
python -m pip install dist/doctor_link-0.5.1-py3-none-any.whl
doctor-link --version
```

### Install the published GitHub Release wheel

Download `doctor_link-0.5.1-py3-none-any.whl` from the [v0.5.1 release page](https://github.com/linkyang01/doctor-link/releases/tag/v0.5.1), then run:

```bash
python -m pip install ./doctor_link-0.5.1-py3-none-any.whl
doctor-link --version
```

Or install the same published wheel directly from GitHub:

```bash
python -m pip install https://github.com/linkyang01/doctor-link/releases/download/v0.5.1/doctor_link-0.5.1-py3-none-any.whl
doctor-link --version
```

### Install from PyPI

```bash
python -m pip install doctor-link==0.5.1
doctor-link --version
```

For an isolated application install, prefer `pipx`:

```bash
pipx install doctor-link==0.5.1
doctor-link --version
```

The equivalent GitHub Release installation remains available as a fallback:

```bash
pipx install https://github.com/linkyang01/doctor-link/releases/download/v0.5.1/doctor_link-0.5.1-py3-none-any.whl
doctor-link --version
```

The recorded PyPI and GitHub Release isolated-install results are available in [pipx installation validation](validation/pipx-install-validation.md). Registry publication is governed by [PyPI Trusted Publishing](pypi-publishing.md).

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
python -m pip install -e '.[dev]'
```

Run the complete validation sequence:

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-branch --cov-fail-under=85 --cov-report=term-missing --cov-report=xml
bandit -r doctor_link -ll
pip-audit
python -m build
python scripts/validate_distribution_contents.py dist
python -m twine check dist/*
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
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
- Do not create a future GitHub Release without explicit authorization for its exact version and destination.
- Do not tag a future public release without explicit authorization.
- Do not change repository permissions without explicit authorization.
- Do not introduce paid cloud services without explicit authorization.
- Do not introduce external account systems without explicit authorization.
- Do not start P6 implementation without explicit authorization.

This guide covers source installation, installation from the published GitHub wheel, local package build, and local validation. It does not authorize PyPI publication or other hosted services.
