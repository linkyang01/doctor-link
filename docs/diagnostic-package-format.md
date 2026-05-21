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
