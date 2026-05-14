# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects.

It is designed to help non-programmer users, developers, and AI coding tools work on the same problem using the same evidence.

Doctor link does not replace Codex, Aider, OpenHands, Continue, or any other AI coding tool. Instead, it prepares the diagnostic context that those tools need in order to debug more accurately.

## What problem does it solve?

AI coding tools are good at modifying code when the task is clear. They become unreliable when the bug report is vague, the runtime evidence is missing, or the user expectation is not represented.

Typical vague input:

> It does not work.

Doctor link turns that into a structured diagnostic package:

- what happened;
- where it happened;
- how to reproduce it;
- what the expected behavior was;
- what the actual behavior was;
- what evidence is available;
- what the user confirmed as the problem;
- what should be investigated;
- what should not be changed;
- how to verify the fix.

## Core positioning

Doctor link is not a log viewer and not a prompt generator.

It is:

> A diagnostic context layer for AI coding workflows.

It provides:

- evidence collection;
- reproduction recording;
- timeline building;
- problem mapping;
- user-confirmed issue preservation;
- AI-ready task generation;
- fix verification planning;
- before/after diagnostic comparison;
- diagnostic package export.

## Key concept: User Assertion

A key feature of Doctor link is `User Assertion`.

Sometimes AI does not recognize something as a problem. For example, the program does not crash, but the user knows the result is wrong.

Doctor link lets the user explicitly say:

> This is the problem.

That human-confirmed issue becomes a first-class diagnostic signal and is included in the AI task.

The generated AI task must include:

> The human user has confirmed this as the problem. Do not dismiss it as normal behavior without evidence.

## Five-layer foundation

Doctor link is designed around five layers:

```text
Layer 1: Diagnostic Protocol
Layer 2: Evidence Collection
Layer 3: Human Diagnosis Surface
Layer 4: AI Collaboration Package
Layer 5: Fix Verification Loop
```

## Standard diagnostic package

Each diagnosis should generate a package like this:

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
    └── evidence/
        ├── environment.json
        ├── logs/
        ├── screenshots/
        ├── command-output/
        ├── test-results/
        └── attachments/
```

## Common commands

```bash
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link assert <package_dir> --statement "This is the problem"
doctor-link env --project-root . --out environment.json
doctor-link probe <file> --summary --out probe.json
doctor-link record <package_dir> --name "Test name" --status partial
doctor-link vly-proof <library> --package-dir <package_dir>
doctor-link compare before.json after.json --package-dir <package_dir>
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip
```

## Diagnostic package export

`doctor-link doctor-package` exports a standard diagnostic package as a zip file for handoff to AI coding tools, developers, or reviewers.

Example:

```bash
doctor-link doctor-package DoctorReports/<package_dir> \
  --out DoctorReports/doctor-package.zip
```

Optional filters:

```bash
doctor-link doctor-package DoctorReports/<package_dir> \
  --out DoctorReports/doctor-package.zip \
  --exclude-attachments \
  --exclude-logs \
  --exclude-screenshots \
  --max-file-size 1000000
```

The exporter writes:

- `manifest.json`: export time, validation result, included files, and skipped files;
- `package-readme.md`: handoff notes, validation result, and skipped file summary;
- `.zip` output preserving the diagnostic package directory structure.

If required files are missing, Doctor link does not pretend that the package is complete. The warning is preserved in the manifest and command output.

## Project configuration

Projects can define their diagnostic rules in `.doctorlink/`:

```text
.doctorlink/
├── doctorlink.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

## First real scenario: Vly

Vly is the first real use case for Doctor link.

Doctor link will help Vly verify whether it can become an all-in-one media player by testing:

- full-format playback;
- disc source playback;
- subtitles;
- audio tracks;
- local NAS simulation;
- playback failure diagnosis;
- user-confirmed playback issues;
- Go / No-Go decision for the next stage.

## Current status

Doctor link has completed the P0/P1 diagnostic foundation and is moving into the P1+ CLI evidence pipeline stage.

It currently supports:

1. core data models;
2. standard diagnostic package generation;
3. user assertion support;
4. problem map generation;
5. AI task generation;
6. fix verification checklist generation;
7. basic evidence collection commands;
8. Vly proof readiness;
9. before/after report comparison;
10. diagnostic package zip export.

## Success standard for the first version

The first version is successful when it can complete this loop:

1. A user reports or selects a problem.
2. Doctor link creates a standard diagnostic package.
3. The user marks the confirmed problem.
4. Doctor link generates a problem map.
5. Doctor link generates an AI-ready debugging task.
6. The AI task contains evidence, boundaries, and verification steps.
7. Doctor link generates a fix verification checklist.
8. Before/after diagnostic reports can be compared.
9. The diagnostic package can be exported for handoff.
