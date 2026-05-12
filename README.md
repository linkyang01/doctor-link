# Doctor link

Doctor link is a universal diagnostic and AI collaboration tool for software debugging, test planning, evidence collection, and structured issue reporting.

It is designed for non-programmer users and AI coding tools. Its goal is not to fix code directly, but to collect enough structured evidence so AI assistants, Codex, or developers can understand, reproduce, diagnose, and verify software problems.

## Core idea

Most debugging fails because the problem is described vaguely:

> It does not work.

Doctor link turns that into a structured diagnostic package:

- What happened
- Where it happened
- How to reproduce it
- What environment was used
- What logs and evidence are available
- What tests passed or failed
- What task should be given to an AI coding agent
- How to verify the fix

## First use case

The first real scenario is Vly Core Proof: testing whether Vly can become an all-in-one media player.

Doctor link will help Vly by:

- scanning a media test library;
- reading media metadata through external tools such as ffprobe;
- generating playback test plans;
- recording manual or semi-automatic test results;
- generating diagnosis reports;
- generating AI / Codex task prompts;
- deciding whether Vly can continue to the next development stage.

## Long-term positioning

Doctor link is independent from Vly. Vly is only the first adapter.

Future adapters may support:

- desktop apps;
- web apps;
- iOS / macOS projects;
- Python projects;
- Node.js projects;
- AI coding workflows;
- GitHub Issues and Pull Requests.

## Planned commands

```bash
doctor-link init
doctor-link scan ./VlyTestLibrary
doctor-link probe ./VlyTestLibrary
doctor-link plan ./VlyTestLibrary
doctor-link record
doctor-link report
doctor-link ai-task
```

## Initial architecture

```text
doctor-link/
├── doctor_link/
│   ├── cli.py
│   ├── core/
│   ├── adapters/
│   └── templates/
├── docs/
├── examples/
└── tests/
```

## Status

This repository is at the initial skeleton stage.

The first milestone is to build a Python CLI that can:

1. initialize a diagnostic workspace;
2. scan a test library;
3. generate a basic test plan;
4. generate Markdown and JSON diagnostic reports;
5. generate an AI-ready debugging task.
