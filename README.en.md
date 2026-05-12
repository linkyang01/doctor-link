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
- before/after diagnostic comparison.

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

### Layer 1: Diagnostic Protocol

Core models:

- DiagnosticEvent
- DiagnosticPackage
- EvidenceItem
- TimelineStep
- UserAssertion
- ProblemMap
- AITask
- VerificationChecklist

### Layer 2: Evidence Collection

Collects:

- environment information;
- logs;
- command outputs;
- test results;
- files and attachments;
- screenshots;
- external tool outputs.

### Layer 3: Human Diagnosis Surface

Human-readable outputs:

- summary.md
- problem-map.md
- timeline.md
- evidence-list.md
- user-assertions.json

### Layer 4: AI Collaboration Package

AI-readable outputs:

- ai-context.json
- ai-task.md
- investigation-boundary.md
- fix-verification-checklist.md

### Layer 5: Fix Verification Loop

Fix validation outputs:

- before-report.json
- after-report.json
- regression-result.json
- Go / No-Go conclusion

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

## Runtime modes

Doctor link supports three diagnostic modes:

### 1. External Mode

Doctor link runs outside the target program and collects project files, logs, command outputs, environment information, and user assertions.

This is the first mode to implement.

### 2. Sidecar Mode

Doctor link runs alongside the target program and watches logs, process status, file changes, test execution, and manual failure markers.

### 3. Embedded SDK Mode

The target program can optionally integrate a lightweight SDK to emit structured runtime events.

This is optional and should not be required for Doctor link to be useful.

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

## Planned commands

```bash
doctor-link init
doctor-link scan
doctor-link report
doctor-link assert
doctor-link ai-task
doctor-link verify-plan
```

## Current status

Doctor link is in the foundation-building stage.

The current priority is to implement:

1. core data models;
2. standard diagnostic package generation;
3. user assertion support;
4. problem map generation;
5. AI task generation;
6. fix verification checklist generation;
7. `.doctorlink/` configuration templates.

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
