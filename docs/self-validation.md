# Doctor link Self-validation

Doctor link can be used to validate itself as a project.

Self-validation means using the installed `doctor-link` CLI to scan the Doctor link source tree, generate a diagnostic package, collect evidence, record a user assertion, record a test result, verify the package, build a local web view, create an AI handoff package, and generate a project health summary.

## Recorded cloud self-validation result

```text
Workflow: Self Validation #1
Branch: main
Job: validate
Result: success
Duration: 30 seconds
```

The successful run confirmed that Doctor link can execute its own self-validation workflow in GitHub Actions.

## Run locally

Install Doctor link from source first:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Then run:

```bash
bash scripts/self_validate_doctor_link.sh
```

The script writes outputs to:

```text
DoctorLinkSelfValidation/
```

A successful run ends with:

```text
Doctor link self-validation completed successfully.
```

## What the script validates

The self-validation script runs the following checks:

- `doctor-link --help`
- `doctor-link strategy validate . --json`
- `doctor-link reproduce list . --json`
- `doctor-link test list . --json`
- `doctor-link scan doctor_link`
- `doctor-link plan doctor_link`
- `doctor-link report doctor_link`
- `doctor-link env --project-root .`
- `doctor-link collect`
- `doctor-link assert`
- `doctor-link record`
- `doctor-link verify --write-back`
- `doctor-link handoff`
- `doctor-link view --build-only`
- `doctor-link health`

## Run in GitHub Actions

A manual workflow is available:

```text
Self Validation
```

To run it:

1. Open the repository on GitHub.
2. Go to **Actions**.
3. Select **Self Validation**.
4. Click **Run workflow**.
5. Select `main` after the workflow is merged.

The workflow uploads a self-validation artifact containing the generated diagnostic package, summary, coverage file, and built package files.

## Scope

Self-validation is not P6 implementation. It does not publish a release, create a release tag, publish to PyPI, change repository permissions, or introduce cloud services beyond GitHub Actions validation.
