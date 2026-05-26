# End-to-End Validation

This guide validates that Doctor link can run as an installed CLI and complete a representative local workflow.

## Run

```bash
python -m pip install -e .
./scripts/e2e_validate.sh
```

## What it checks

The script checks:

- CLI availability;
- diagnostic package creation;
- evidence collection;
- user assertion recording;
- verification result generation;
- AI handoff generation;
- local workbench build;
- before / after package workflow;
- automated compare and verify;
- project health summary.

## Expected output

```text
Doctor link E2E validation passed: <path>
```

## Output location

The script writes temporary validation output to:

```text
.doctorlink-e2e/
```
