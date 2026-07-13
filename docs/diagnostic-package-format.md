# Diagnostic Package Format

Doctor link diagnostic packages are stored under `DoctorReports/`.

Typical layout:

```text
DoctorReports/
└── <timestamp>_<project>_<issue>/
    ├── summary.md
    ├── problem-map.md
    ├── timeline.md
    ├── evidence-list.md
    ├── doctor-report.md
    ├── doctor-report.json
    ├── ai-context.json
    ├── reproduce-steps.md
    ├── ai-task.md
    ├── investigation-boundary.md
    ├── fix-verification-checklist.md
    ├── user-assertions.json
    ├── verification-result.json
    ├── diagnosis-workflow.json
    ├── diagnosis-pipeline-summary.json
    ├── package-export-manifest.json
    ├── project-health.json
    └── evidence/
```

## Core files

- `summary.md`: human-readable package summary.
- `problem-map.md`: problem and evidence map.
- `timeline.md`: diagnostic timeline.
- `evidence-list.md`: evidence index.
- `doctor-report.json`: machine-readable package summary.
- `ai-context.json`: machine-readable AI task context.
- `ai-task.md`: AI-ready repair task.
- `fix-verification-checklist.md`: verification checklist.

## User assertion files

- `user-assertions.json`: user-confirmed issues that AI must not dismiss without evidence.
- `assertion-compliance-report.json`: whether AI result records covered the user assertions.

## Verification files

- `verification-plan.md`: what must be checked.
- `verification-result.json`: verification status and missing evidence.
- `diagnosis-pipeline-summary.json`: P4 automated pipeline result.

## AI collaboration files

- `ai-repair-result.json`: AI repair result records.
- `diagnosis-history.json`: multi-round diagnosis records.
- `repair-risk-review.json`: repair risk review.

## Export files

- `package-export-manifest.json`: files included or skipped by `doctor-package`, export destination, validation summary, and redaction-report presence.
- `package-readme.md`: human-readable archive contents and warnings.

The explicit filename avoids collision with the versioned package-level `manifest.json` schema and `handoff-manifest.json`.

## Evidence directory

Common evidence subdirectories:

```text
evidence/
├── logs/
├── commands/
├── probes/
├── attachments/
├── reproductions/
└── test-results/
```

## Compatibility principle

New fields should be additive. Existing diagnostic package readers should ignore unknown fields.

## Mutation and concurrency guarantees

Package writers serialize read-modify-write operations with a package-local lock and replace JSON/Markdown files atomically. This protects concurrent `record`, assertion, reproduction, test-matrix, comparison, and verification updates from silently overwriting one another. The lock is temporary and is not package evidence; stale locks are recovered automatically.

Automated reproduction and test records use stable IDs. Rerunning the same configured item replaces its previous evidence, timeline step, test record, and marked Markdown block instead of accumulating contradictory historical status sections.
