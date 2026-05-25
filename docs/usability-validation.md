# Usability Validation Guide

This guide validates that Doctor link can be installed and used for a local diagnostic workflow.

## Run from source

```bash
python -m pip install -e .
bash scripts/validate_doctor_link.sh
```

The script creates a temporary workspace and runs the core workflow:

- report generation
- evidence collection
- user assertion
- test record
- comparison
- verification
- AI handoff
- local workbench build
- before / after diagnosis workflow
- project health summary

## Expected result

The script should finish with:

```text
Doctor link validation completed successfully.
```

Expected artifacts include:

- `doctor-report.json`
- `summary.md`
- `verification-result.json`
- `.doctorlink-web/index.html`
- `project-health.json`
