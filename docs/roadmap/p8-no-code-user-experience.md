# P8 No-code User Experience and Guided Workflow

Status: largely complete (v0.1.0-rc.1 + v0.1.1 + v0.1.2 polish)

## Purpose

P8 turns Doctor link from a developer-oriented CLI tool into a guided local-first diagnostic workflow that non-programmer users can complete with minimal command-line knowledge.

P8 does not replace the existing CLI. It adds a safer, clearer, guided layer on top of the proven P0-P7 runtime foundation.

## Target users

P8 focuses on users who:

- do not write code;
- can copy and paste simple commands if necessary;
- need to collect evidence for a software problem;
- need to give a clear repair package to an AI coding tool or developer;
- need to open and understand a local diagnostic report;
- need safe defaults and clear guidance.

## Current gap

Doctor link has a complete technical workflow:

```text
collect evidence -> build diagnostic package -> record assertions -> verify -> view report -> AI handoff -> repair loop
```

The guided no-code workflow is now available through `wizard`, `diagnose-now`, `home`, bilingual quick-start guides, and macOS/Windows helper scripts. Remaining P8 polish targets v0.1.1+ (wizard multi-tool handoff, Windows validation record, example CI smoke).

## Product principles

- Keep local-first behavior.
- Keep read-only-first behavior.
- Do not introduce hosted services.
- Do not introduce account systems.
- Do not introduce telemetry.
- Do not publish to PyPI as part of P8 unless separately authorized.
- Keep all advanced CLI commands available.
- Add guided commands for non-programmers.
- Prefer plain-language prompts and plain-language errors.
- Make successful output tell the user exactly what to open or share next.

## Scope

### P8.1 Guided wizard

Add:

```bash
doctor-link wizard
```

The wizard should ask plain-language questions:

- Which folder should Doctor link inspect?
- What problem are you trying to diagnose?
- Do you want to include logs?
- Do you want to generate an AI handoff package?
- Do you want to build the local HTML report?

Expected output:

- diagnostic package;
- user assertion;
- basic evidence;
- verification placeholder;
- optional AI handoff;
- optional local workbench;
- final next-step summary.

### P8.2 One-command diagnosis

Add:

```bash
doctor-link diagnose-now <project_folder> --summary "problem summary"
```

This command should run the common workflow:

- report;
- collect;
- assert;
- verify;
- view build;
- optional handoff.

It should end with clear output:

```text
Diagnostic report created:
DoctorReports/.../.doctorlink-web/index.html

AI handoff created:
DoctorReports/handoff/...

Next step:
Open the report or give the handoff folder to your AI coding tool.
```

### P8.3 No-code quick start docs

Add:

- `docs/guides/no-code-quick-start.zh-CN.md`
- `docs/guides/no-code-quick-start.en.md`

These docs should avoid developer jargon and explain:

- what Doctor link is;
- when to use it;
- what it creates;
- which command to copy;
- where the report is;
- what to send to AI;
- what not to send;
- what to do when a command fails.

### P8.4 Friendly error messages

Add a friendly error helper for common user-facing problems:

- folder not found;
- Python version unsupported;
- command not found;
- report directory not found;
- no package found;
- permission denied;
- invalid path;
- no AI handoff target selected.

### P8.5 Local home page

Add:

```bash
doctor-link home
```

This command should build a static local homepage with links to:

- latest diagnostic reports;
- quick start docs;
- local workbench pages;
- validation docs;
- AI handoff outputs;
- troubleshooting docs.

This remains local static HTML. It is not a hosted platform.

### P8.6 Packaging helpers for non-programmers

Add helper scripts:

- `scripts/start-doctor-link-macos.command`
- `scripts/start-doctor-link-windows.ps1`

These scripts should start the wizard or print simple installation guidance.

## Acceptance criteria

P8 is complete when:

- `doctor-link wizard` exists and can complete a minimal guided diagnosis;
- `doctor-link diagnose-now` exists and can complete the default workflow;
- no-code quick start docs exist in Chinese and English;
- common user errors produce friendly next-step messages;
- `doctor-link home` can generate a static local homepage;
- helper scripts exist for macOS and Windows;
- tests cover the wizard, diagnose-now, and friendly errors;
- CI passes on Python 3.10, 3.11, and 3.12;
- P7 runtime validation still passes;
- no PyPI publication, hosted service, telemetry, marketplace, or account system is introduced beyond the published GitHub Release.

## Out of scope

P8 does not include:

- Electron desktop app;
- hosted Web app;
- cloud sync;
- user accounts;
- telemetry;
- marketplace;
- PyPI publication;
- paid services;
- automatic code modification;
- production deployment claims.

## Release target

P8 is a candidate for a future:

```text
v0.2.0 no-code workflow preview
```

`v0.1.0-rc.1` is published on GitHub (Latest, 2026-06-29). Further no-code UX polish ships in `v0.1.1` and may preview in a future `v0.2.0` workbench release.
