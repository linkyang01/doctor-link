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
doctor-link doctor-package <package_dir> --out package.zip \
  --exclude-attachments --exclude-logs --max-file-size 1000000
```

Export runs the privacy safety gate automatically. Any remaining email, API token, secret, or private-key pattern blocks archive creation and returns non-zero. Review the findings and redact the package. Only when the risk has been deliberately accepted should an operator use:

```bash
doctor-link doctor-package <package_dir> --out reviewed-package.zip \
  --allow-unsafe-export --json
```

The override status and finding count are retained in the export manifest. Absolute source and destination paths are never written into the archive.

The gate scans the files actually selected for export. Content removed with `--exclude-logs`, `--exclude-attachments`, `--exclude-screenshots`, or the size limit is not uploaded, archived, or treated as an export blocker. Local legacy-migration backups are also excluded from subsequent archives.

Generated `.doctorlink-web` assets are excluded by default. Add `--include-web` when the local HTML workbench should be part of the archive.

Review the zip before sharing.
