# Diagnostic Package Data Contents

Doctor link diagnostic packages may include multiple data categories.

## Low sensitivity by default

These files are usually lower sensitivity, but still should be reviewed:

- `summary.md`
- `problem-map.md`
- `timeline.md`
- `evidence-list.md`
- `fix-verification-checklist.md`

## Potentially sensitive

These files may include private project details:

- `doctor-report.json`
- `ai-context.json`
- `ai-task.md`
- `user-assertions.json`
- `ai-repair-result.json`
- `diagnosis-history.json`
- `repair-risk-review.json`

## Evidence files

Evidence can be highly sensitive depending on what was collected:

- logs;
- command outputs;
- attachments;
- screenshots;
- reproduction outputs;
- test outputs;
- media probe metadata.

## Export guidance

Use `doctor-link doctor-package` options to reduce exported content when possible:

```bash
doctor-link doctor-package <package_dir> --exclude-attachments --exclude-logs --max-file-size 1000000
```

Review the zip before sharing.
