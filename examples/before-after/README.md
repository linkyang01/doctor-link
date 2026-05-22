# Example Before / After Workflow

This example documents the expected before / after workflow.

## Create baseline

```bash
doctor-link diagnose before --project "Example" --summary "before issue" --out DoctorReports
```

## Create after package

```bash
doctor-link diagnose after --project "Example" --summary "after fix" --before-package <before_package> --out DoctorReports
```

## Compare and verify

```bash
doctor-link diagnose compare <after_package> --json
doctor-link diagnose verify <after_package> --json
```

The generated after package should contain:

- `diagnosis-workflow.json`
- `diagnosis-pipeline-summary.json`
- comparison evidence when a before report exists
- verification result files
