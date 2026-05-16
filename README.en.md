# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

## Core Positioning

Doctor link is a diagnostic context layer for AI coding workflows.

It follows these principles:

- evidence first;
- reproduction first;
- human-confirmed issues first;
- AI must not dismiss a human-confirmed issue without evidence;
- fixes must be verified;
- local-first and read-only-first;
- protocol and CLI before Web UI.

## Key Concept: User Assertion

Sometimes AI does not recognize something as a problem, while the user knows the output is wrong. Doctor link lets the user explicitly mark:

> This is the problem.

That human-confirmed issue becomes a first-class diagnostic signal and is carried into AI tasks, test records, verification, and compliance checks.

## Standard Diagnostic Package

Doctor link generates and maintains standard diagnostic packages:

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
    ├── ai-repair-result.json
    ├── diagnosis-history.json
    ├── assertion-compliance-report.json
    ├── repair-risk-review.json
    └── evidence/
```

## Common Commands

```bash
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link collect <package_dir> --project-root . --logs "logs/*.log" --command "python --version"
doctor-link verify <package_dir> --write-back
doctor-link assert <package_dir> --statement "This is the problem"
doctor-link env --project-root . --out environment.json
doctor-link probe <file> --summary --out probe.json
doctor-link record <package_dir> --name "Test name" --status partial --assertion-id assertion-1
doctor-link vly-proof <library> --package-dir <package_dir>
doctor-link compare before.json after.json --package-dir <package_dir>
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip
doctor-link view <package_dir>
doctor-link view DoctorReports
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ai-result <package_dir> --summary "AI repair summary" --claimed-fix "claimed fix" --assertion-id assertion-1 --verification-step pytest
doctor-link diagnosis-history <package_dir> --ai-pass "round 1" --user-correction "human correction" --evidence-id ev-1
doctor-link assertion-check <package_dir>
doctor-link risk-review <package_dir> --file doctor_link/cli.py --boundary doctor_link/
```

## P1 / P1+: Evidence and Verification Loop

Doctor link supports environment collection, logs, command output, media probing, attachments, test records, Vly proof, before/after comparison, and standard diagnostic package export.

`doctor-link verify` generates:

- `verification-plan.md`
- `verification-result.json`

It does not mark a fix complete just because AI claimed it was fixed. It records missing evidence, tests to rerun, and next commands.

## P2 / P2+: Local Diagnostic Workbench

`doctor-link view` provides a local read-only workbench for browsing:

- summary / timeline / evidence;
- user assertions;
- AI task;
- verification;
- comparison;
- redaction / manifest;
- evidence reverse references;
- assertion coverage;
- AI handoff blocks.

The Web UI is local and read-only by default. It does not add cloud sync, login, or default package write-back.

## P3: AI Coding Collaboration Layer

P3 adds AI Coding collaboration features:

- AI task templates;
- AI tool handoff packages;
- `doctor-link handoff`;
- `doctor-link ai-result`;
- `doctor-link diagnosis-history`;
- `doctor-link assertion-check`;
- `doctor-link risk-review`.

P3 generates and maintains:

- `ai-repair-result.json` / `ai-repair-result.md`;
- `diagnosis-history.json` / `diagnosis-history.md`;
- `assertion-compliance-report.json` / `assertion-compliance-report.md`;
- `repair-risk-review.json` / `repair-risk-review.md`.

These files record AI repair claims, diagnosis rounds, assertion coverage, and repair risk. AI output is a collaboration record, not verification evidence; completion still depends on verification results.

## Project Configuration

Projects can define diagnostic rules in `.doctorlink/`:

```text
.doctorlink/
├── doctorlink.yml
├── collect.yml
├── package.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

CLI options override configuration files.

## Current Status

Doctor link has completed:

- P0: Diagnostic Foundation;
- P1: Evidence Collection Primitives;
- P1+: CLI Evidence Pipeline;
- P2: Local Read-only Diagnostic Workbench;
- P2+: Mainline Diagnostic Workbench Enhancements;
- P3: AI Coding Collaboration Layer.

The next phase is P4: Automated Diagnosis Pipeline.

## Boundaries

The following require separate explicit authorization: publishing a version, creating a GitHub Release, publishing to PyPI, changing repository permissions, adding paid cloud services, adding external account systems, changing Doctor link's core positioning, making the local read-only Web UI write back by default, or starting P6 implementation.
