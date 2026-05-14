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
- diagnostic package export;
- local diagnostic package browsing.

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
doctor-link collect <package_dir> --project-root . --logs "logs/*.log" --command "python --version"
doctor-link verify <package_dir> --write-back
doctor-link assert <package_dir> --statement "This is the problem"
doctor-link env --project-root . --out environment.json
doctor-link probe <file> --summary --out probe.json
doctor-link record <package_dir> --name "Test name" --status partial
doctor-link vly-proof <library> --package-dir <package_dir>
doctor-link compare before.json after.json --package-dir <package_dir>
doctor-link doctor-package <package_dir> --out DoctorReports/package.zip
doctor-link view <package_dir>
```

## One-command evidence collection

`doctor-link collect` collects environment information, logs, command output, media probe results, and attachments into an existing diagnostic package.

Example:

```bash
doctor-link collect DoctorReports/<package_dir> \
  --project-root . \
  --logs "logs/*.log" \
  --command "python --version" \
  --probe sample.mp4 \
  --attachment input.txt \
  --note "Additional evidence after user reproduction"
```

The command updates:

- `doctor-report.json`
- `evidence-list.md`
- `timeline.md`
- `summary.md`
- `ai-task.md`
- `evidence/environment.json`
- `evidence/logs/`
- `evidence/command-output/`
- `evidence/test-results/`
- `evidence/attachments/`

If a command fails or media probing fails, the failure result is still preserved as evidence instead of being silently ignored.

### Sensitive information redaction

`doctor-link collect` automatically redacts sensitive information from logs and command output by default and generates:

- `redaction-report.md`
- `redaction-report.json`

Default redaction covers:

- password
- secret
- api_key / api-key
- access_token / access-token
- token
- Cookie
- Authorization Header

Optional redaction:

```bash
doctor-link collect DoctorReports/<package_dir> \
  --logs "logs/*.log" \
  --redact-email \
  --redact-phone \
  --redact-pattern "internal-[0-9]+"
```

If raw logs and command output must be preserved, use:

```bash
doctor-link collect DoctorReports/<package_dir> --logs "logs/*.log" --no-redact
```

Use `--no-redact` only when the package will not be shared externally, because tokens, passwords, cookies, or other secrets may be exposed.

## Fix verification task generation

`doctor-link verify` reads the diagnostic package verification checklist, test records, user assertions, Vly proof, and report comparison to generate a verification plan and structured verification result.

Example:

```bash
doctor-link verify DoctorReports/<package_dir> --write-back
```

The command writes:

- `verification-plan.md`
- `verification-result.json`

When `--write-back` is used, it also updates:

- `doctor-report.json`
- `summary.md`
- `ai-task.md`

Verification statuses include:

- `ready`
- `missing_evidence`
- `not_verified`
- `candidate_verified`
- `needs_review`

Doctor link does not claim a fix is verified just because a verification plan exists. It lists missing evidence, tests to rerun, and suggested next commands.

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

If required files are missing, Doctor link does not pretend that the package is complete. The warning is preserved in the manifest and command output. If `redaction-report.md` is missing, the export notes will remind reviewers to check for sensitive information before sharing.

## Local diagnostic package browser

`doctor-link view` opens a local, read-only browser view for a diagnostic package. It does not modify package contents.

Example:

```bash
doctor-link view DoctorReports/<package_dir>
```

Optional parameters:

```bash
doctor-link view DoctorReports/<package_dir> \
  --host 127.0.0.1 \
  --port 8765 \
  --no-open-browser
```

Build static HTML without starting the local server:

```bash
doctor-link view DoctorReports/<package_dir> --build-only
```

The command generates:

```text
DoctorReports/<package_dir>/.doctorlink-web/index.html
```

The current view includes:

- summary;
- problem-map;
- timeline;
- evidence-list;
- user assertions;
- AI task;
- investigation boundary;
- verification checklist / verification plan / verification result;
- redaction report;
- manifest;
- package readme;
- evidence file list.

The first P2 Web UI batch is local and read-only. It does not add cloud sync, login, or any replacement for the CLI diagnostic workflow.

## Project configuration

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

`collect`, `verify`, and `doctor-package` automatically search upward for a `.doctorlink` directory and load defaults from it. Explicit CLI parameters take priority over configuration files.

### collect.yml example

```yaml
collect:
  project_root: .
  logs:
    - logs/*.log
  commands:
    - python --version
    - doctor-link --help
  probes: []
  attachments: []
  redaction:
    enabled: true
    email: false
    phone: false
    patterns: []
```

### package.yml example

```yaml
package:
  output_dir: DoctorReports
  exclude_attachments: false
  exclude_logs: false
  exclude_screenshots: false
  max_file_size: 1000000
```

### verification.yml example

```yaml
verification:
  write_back: false
  required_signals:
    - test_records
    - report_comparison
```

If `--logs`, `--command`, `--max-file-size`, or similar CLI options are omitted, Doctor link uses `.doctorlink` defaults. If those options are provided on the command line, the command line wins.

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

Doctor link has completed the P0/P1/P1+ diagnostic foundation and is moving into the P2 local Web UI / diagnostic package browser stage.

It currently supports:

1. core data models;
2. standard diagnostic package generation;
3. user assertion support;
4. problem map generation;
5. AI task generation;
6. fix verification checklist generation;
7. basic evidence collection commands;
8. one-command evidence collection;
9. sensitive information redaction;
10. configuration-driven collection, verification, and package export;
11. verification task generation;
12. Vly proof readiness;
13. before/after report comparison;
14. diagnostic package zip export;
15. local read-only diagnostic package browser.

## Success standard for the first version

The first version is successful when it can complete this loop:

1. A user reports or selects a problem.
2. Doctor link creates a standard diagnostic package.
3. Doctor link collects environment, logs, command output, media probe results, and attachments.
4. Doctor link redacts sensitive information from logs and command output.
5. The user marks the confirmed problem.
6. Doctor link generates a problem map.
7. Doctor link generates an AI-ready debugging task.
8. The AI task contains evidence, boundaries, and verification steps.
9. Doctor link generates a fix verification plan.
10. Before/after diagnostic reports can be compared.
11. The diagnostic package can be exported for handoff.
12. The diagnostic package can be browsed locally.
