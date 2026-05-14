# Doctor link P2 Draft Notes

Draft only. Do not publish a release without explicit authorization.

## Theme

P2 upgrades the local Web UI into a local diagnostic workbench.

## Highlights

- Local read-only package browser.
- Multi-package DoctorReports workbench index.
- Package cards with project, summary, evidence count, timeline count, user assertion count, verification status, redaction status, and export status.
- Local filters for verification status, user assertions, and redaction warnings.
- Enhanced package detail workbench with Overview, Timeline, Evidence, Assertions, AI Task, Verification, Comparison, Redaction, Manifest, and Raw Files sections.
- Text and JSON evidence previews.
- Binary and unsupported evidence is listed but not embedded.
- Verification panel showing status, missing evidence, tests to rerun, and next commands.
- Comparison, redaction, and manifest panels.
- ADR confirming the P2 Web UI remains read-only.

## Commands

```bash
doctor-link view DoctorReports
```

```bash
doctor-link view DoctorReports/<package_dir>
```

```bash
doctor-link view DoctorReports --build-only
```

## Validation

P2 is ready when tests pass, CLI smoke passes, workbench pages build, broken JSON is handled, missing evidence is shown as a warning, and README files are current.
