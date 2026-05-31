# P7.2 Local Workbench Product Hardening

Status: runtime implementation

## Scope

P7.2 hardens the local diagnostic package workbench while preserving Doctor link's local-first and read-only-first default.

## Implemented runtime changes

### Collapsible workbench sections

The package detail workbench now renders major sections as native HTML `<details>` sections:

- Overview
- Project Health
- Controlled Write-back
- Timeline
- Evidence
- User Assertions
- AI Task
- Verification Workbench
- Before / After Comparison
- Redaction
- Manifest / Export
- Raw Evidence File List

This keeps large diagnostic packages easier to review without requiring a framework or cloud dependency.

### Project health panel

The package detail page now includes a local-only project health panel derived from package signals:

- verification status;
- missing evidence count;
- tests to rerun count;
- user assertion count;
- redaction status;
- computed local health score.

The score is only a review aid. It does not replace verification results.

### Evidence search and filtering

The Evidence section now includes local browser-side filtering:

- search by path, type, evidence id, or preview text;
- filter by evidence type;
- visible evidence count;
- reset control.

The filtering script runs only in the generated local HTML page and does not modify package files.

### Assertion and evidence navigation

The workbench now improves navigation by:

- keeping evidence anchors for paths and evidence IDs;
- rendering assertion anchors;
- linking evidence references from timeline, assertions, verification status reasons, and raw result blocks where possible.

### Verification status visualization

The Verification Workbench now includes an explicit verification state panel with `role="status"` and status-based styling. The UI still must not claim a fix is complete when evidence is missing.

### Accessibility structure

P7.2 adds or preserves:

- `<!doctype html>` and `lang="en"`;
- viewport metadata;
- skip link to main content;
- labelled navigation;
- semantic `main` region;
- native `<details>` disclosure sections;
- keyboard-accessible controls.

### Controlled local write-back

The browser page remains static and read-only.

Controlled write-back is implemented as a CLI-only operation:

```bash
doctor-link workbench-note <package_dir> --note "review note" --enable-write-back
```

Default behavior without `--enable-write-back`:

- does not write package files;
- returns a warning;
- can emit JSON for automation.

Enabled behavior:

- appends a Markdown note to `workbench-notes.md` by default;
- creates a timestamped backup if the target note file already exists;
- appends an audit record to `workbench-writeback-audit.jsonl`;
- remains local-only.

## Safety boundaries

P7.2 does not:

- make the browser UI write back directly;
- introduce cloud sync;
- introduce accounts;
- expose the whole package directory through the browser server;
- publish releases;
- create tags;
- publish to PyPI.

## Validation

P7.2 includes tests for:

- collapsible sections;
- project health panel;
- evidence search/filter controls;
- evidence search metadata;
- verification state panel;
- skip-link accessibility structure;
- write-back disabled by default;
- explicit write-back with audit and backup;
- CLI dry-run and explicit write-back behavior.
