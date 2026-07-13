# GitHub Actions PR Diagnostics

This document describes how to use Doctor link in GitHub Actions for pull request diagnostics.

For the repository's own CI, package, security, manual, self-validation, and release workflows, see [GitHub Repository and Workflow Guide](github-repository-guide.md). The workflow below is an integration example for another project; it is not the same as Doctor link's internal CI matrix.

## Goals

- Run Doctor link in CI without publishing anything.
- Generate diagnostic artifacts for failed or risky PRs.
- Upload `DoctorReports/**` as a workflow artifact.
- Optionally post a concise PR comment summary in a future integration.

## Minimal PR Diagnostic Workflow

```yaml
name: Doctor link PR Diagnostics

on:
  pull_request:
    branches: [main]

jobs:
  doctor-link:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install project and Doctor link
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e .
          python -m pip install pytest

      - name: Validate diagnosis strategy
        run: |
          doctor-link preflight . --json
          doctor-link strategy validate . --json

      - name: Create before diagnostic package
        run: |
          doctor-link diagnose before --project "${{ github.repository }}" --summary "PR baseline" --out DoctorReports

      - name: Run tests
        run: |
          doctor-link test run . --package-dir "$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | head -n 1)" --json

      - name: Create after diagnostic package
        run: |
          BEFORE_PACKAGE=$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | head -n 1)
          doctor-link diagnose after --project "${{ github.repository }}" --summary "PR result" --before-package "$BEFORE_PACKAGE" --out DoctorReports

      - name: Run automated verification
        run: |
          AFTER_PACKAGE=$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | tail -n 1)
          doctor-link diagnose verify "$AFTER_PACKAGE" --json

      - name: Upload Doctor link reports
        uses: actions/upload-artifact@v7
        if: always()
        with:
          name: doctor-link-reports
          path: DoctorReports/**
          if-no-files-found: warn
```

## Artifact Upload Pattern

Always upload `DoctorReports/**` with `if: always()` so diagnostic packages are preserved even when tests fail.

Recommended artifacts:

- `doctor-report.json`
- `diagnosis-workflow.json`
- `diagnosis-pipeline-summary.json`
- `verification-result.json`
- `evidence/**`

## Optional PR Comment Summary

P4 documents the intended PR comment pattern but does not implement write-back to GitHub comments by default.

A future integration may summarize:

- pipeline status;
- missing evidence;
- failed test matrix jobs;
- unresolved user assertions;
- artifact download link.

## Boundaries

- This workflow does not publish releases.
- This workflow does not require paid cloud services.
- This workflow does not create external accounts.
- PR comments remain optional and require explicit repository permissions.
- Uploaded reports may contain sensitive repository evidence; configure artifact retention and access accordingly.
- Do not expose secrets through command output, workflow summaries, PR comments, or public artifacts.
- Pin or review third-party Actions according to the consuming repository's supply-chain policy.
