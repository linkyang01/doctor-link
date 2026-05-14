# ADR 0002: P1+ CLI Evidence Pipeline

## Status

Accepted

## Context

Doctor link P0 and P1 established the diagnostic protocol, standard diagnostic package, user-confirmed problem mechanism, evidence capture primitives, Vly proof readiness, test result recording, and before/after report comparison.

The next step should improve the CLI workflow without changing the existing diagnostic package protocol or starting the local Web UI too early.

## Decision

P1+ will focus on three CLI commands:

1. `doctor-link doctor-package`
   - Validate a diagnostic package.
   - Generate a manifest and package README.
   - Export the package as a zip file.

2. `doctor-link collect`
   - Collect environment, logs, command output, media probe results, and attachments.
   - Write collected evidence into an existing diagnostic package.

3. `doctor-link verify`
   - Read the verification checklist, test records, report comparison, Vly proof, and user assertions.
   - Generate a verification plan and structured verification result.
   - Optionally write verification status back into the package.

P1+ must not introduce the local Web UI. P2 will handle Web UI work separately.

P1+ must not change the P0/P1 diagnostic package structure in a breaking way. New files and fields may be added, but existing files and fields should remain compatible.

## Consequences

- Users get a stronger CLI workflow before any Web UI work begins.
- Diagnostic packages become easier to hand off to AI coding tools, developers, or reviewers.
- P2 can later focus on browsing and visualization instead of fixing incomplete package workflows.
- Tests and CI must cover each new CLI command.

## Non-goals

- No Web UI in P1+.
- No cloud upload.
- No database.
- No replacement of existing P0/P1 commands.
