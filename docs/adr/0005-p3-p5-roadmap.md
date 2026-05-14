# ADR 0005: P3-P5 Roadmap

## Status

Accepted

## Context

Doctor link has already established its diagnostic protocol foundation, evidence collection pipeline, verification loop, packaging workflow, and the first local Web UI foundation.

The next major stages must remain aligned with Doctor link's core positioning: Doctor link is the diagnostic context layer for AI Coding. It is not a generic log viewer, not a cloud SaaS product by default, and not a replacement for AI coding tools.

## Decision

Doctor link will use the following roadmap after P2:

- P3: AI Coding Collaboration Layer
- P4: Automated Diagnosis Pipeline
- P5: Productization and Release Readiness

### P3: AI Coding Collaboration Layer

P3 turns Doctor link from a diagnostic package tool into a structured collaboration layer between users, diagnostic evidence, and AI coding tools.

P3 focuses on:

- AI repair task templates;
- Codex / Cursor / Continue / Aider / OpenHands handoff formats;
- AI repair result intake;
- multi-turn AI diagnosis history;
- human-confirmed issue enforcement;
- repair risk review;
- fix verification binding.

P3 must preserve the rule that AI cannot dismiss a human-confirmed problem without evidence.

### P4: Automated Diagnosis Pipeline

P4 turns Doctor link from a manually operated CLI workflow into an automated project-level diagnostic pipeline.

P4 focuses on:

- project diagnostic strategy files;
- automated evidence collection rules;
- reproduction scripts;
- test matrix automation;
- before/after diagnostic package generation;
- comparison automation;
- verification automation;
- GitHub Actions and PR integration;
- project health dashboard foundations.

P4 must not claim automatic success without verification evidence.

### P5: Productization and Release Readiness

P5 turns Doctor link from an engineering project into a product-ready, installable, documented, and releasable software project.

P5 focuses on:

- versioning;
- release notes;
- installation and packaging;
- user documentation;
- examples;
- website / landing documentation;
- security and privacy review;
- adapter/plugin documentation;
- release checklist.

No release should be published without explicit authorization.

## Consequences

- TODO.md must track P3, P4, and P5 as concrete tasks.
- Each stage gets a GitHub Issue for project management.
- Work must remain incremental: finish one task, mark it complete, then continue.
- Architectural changes inside P3-P5 require additional ADRs.
- P6 can be planned later as standardization and ecosystem platform work, but it is not part of this ADR.
