# Doctor link P2 Draft Notes

Draft only. Do not publish a release without explicit authorization.

## Theme

P2 upgrades Doctor link from CLI-first diagnostic package generation into a local, read-only diagnostic workbench.

## Highlights

- Local read-only package browser.
- Multi-package `DoctorReports` workbench index.
- Package cards with project, summary, evidence count, timeline count, user assertion count, verification status, redaction status, and export status.
- Local filters for verification status, user assertions, and redaction warnings.
- Enhanced package detail workbench with Overview, Timeline, Evidence, Assertions, AI Task, Verification, Comparison, Redaction, Manifest, and Raw Files sections.
- Text and JSON evidence previews.
- Binary and unsupported evidence is listed but not embedded.
- Stable evidence anchors and evidence ID links.
- Timeline, AI Task, and Verification sections can link to matching evidence cards when evidence references are available.
- Dedicated comparison reader for `report-comparison.json` and `report-comparison.md`.
- Comparison panel showing status, before/after report references, resolved signals, unresolved signals, new signals, changed signals, deltas, notes, Markdown, and raw JSON.
- Verification panel showing status, missing evidence, tests to rerun, next commands, report comparison status, Vly Core Proof status, and assertion test coverage when present.
- Unknown assertion coverage is shown explicitly when coverage data is not available.
- Redaction and manifest panels for sharing and export review.
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

P2 hardening is ready when:

- unit tests pass;
- CLI smoke tests pass;
- single-package workbench pages build;
- multi-package DoctorReports workbench pages build;
- broken JSON is handled without crashing;
- missing evidence is shown as a warning;
- comparison data is parsed through the dedicated reader;
- evidence links resolve to stable evidence anchors;
- verification signals are visible in the workbench;
- Issue #15 and `TODO-P2-HARDENING.md` are aligned.

## Safety Boundaries

- No release is published by P2.
- No GitHub Release is created by P2.
- No package registry publishing is performed by P2.
- No cloud sync is added.
- No account system is added.
- The Web UI remains local and read-only by default.
- Review-note write-back remains deferred unless a future ADR explicitly approves it.

## Known Limits

- P2 is a static local workbench, not a full front-end application.
- The browser view does not mutate diagnostic packages.
- Assertion test coverage is displayed when present; full generation of coverage is part of the later P1/P1+ assertion-linkage hardening work.
- Evidence linking depends on evidence IDs or paths being available in the diagnostic package.
