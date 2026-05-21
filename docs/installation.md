# Installation Guide

Doctor link is currently prepared for source installation and local package build validation.

No PyPI publication has been performed. Publishing requires explicit authorization.

## Install from source

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python -m pip install --upgrade pip
python -m pip install -e .
```

Verify the CLI:

```bash
doctor-link --help
doctor-link strategy validate . --json
```

## Build a wheel locally

Install build tooling:

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

## Local build smoke

After building, install the wheel in a clean virtual environment and run:

```bash
doctor-link --help
doctor-link health DoctorReports --json
```

## Boundaries

- Do not publish to PyPI without explicit authorization.
- Do not create a GitHub Release without explicit authorization.
- Do not tag a public release without explicit authorization.
