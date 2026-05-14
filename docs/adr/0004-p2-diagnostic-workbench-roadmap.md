# ADR 0004: P2 Diagnostic Workbench Roadmap

## Status

Accepted

## Context

P2 has started with a minimal local, read-only diagnostic package browser. That first batch proves that Doctor link can render a standard diagnostic package through `doctor-link view` without introducing cloud services or replacing the CLI workflow.

However, the full P2 goal is broader than a static package page. Doctor link should become a local diagnostic workbench that helps users, developers, and AI coding tools inspect package state, compare before/after evidence, review human-confirmed problems, and understand whether a fix is actually verified.

## Decision

P2 will be expanded into a staged local diagnostic workbench while preserving these boundaries:

- local-first;
- read-only by default;
- package-first;
- evidence-first;
- human assertion first;
- no cloud service dependency;
- no AI coding tool replacement;
- CLI remains the source of diagnostic package creation, evidence collection, verification, and export.

P2 will be organized into the following workstreams:

1. Package index and navigation
   - Browse `DoctorReports/` as a package library.
   - Show package status, timestamps, warnings, evidence counts, assertions, verification state, and redaction status.
   - Open a selected package without requiring the user to copy paths manually.

2. Package detail pages
   - Split the initial single HTML page into clearer views: overview, timeline, evidence, assertions, AI task, verification, redaction, manifest.
   - Highlight missing evidence, failed steps, human-confirmed issues, and verification blockers.

3. Comparison visualization
   - Visualize before/after `report-comparison.json` and `report-comparison.md`.
   - Show resolved, unresolved, new, and changed signals.
   - Make `not_verified` and `candidate_verified` easy to understand.

4. Evidence detail experience
   - Provide safe previews for logs, command output, test results, media probe output, attachments list, and redaction reports.
   - Avoid exposing raw sensitive content beyond already collected package files.
   - Keep evidence paths stable and traceable to `doctor-report.json`.

5. Verification workbench
   - Surface verification status and blockers.
   - Show tests to rerun, missing evidence, suggested next commands, and human review notes.
   - Do not claim final success unless diagnostic evidence supports it.

6. Local review and notes
   - Add optional local notes/review mode in a future batch only after a separate decision.
   - If write-back is introduced, it must be explicit, auditable, and never silently mutate evidence.

## Consequences

- P2 will remain incremental and test-driven.
- TODO.md must track each P2 batch before implementation.
- New Web UI behavior that writes to diagnostic packages requires an additional ADR.
- The first full P2 completion target is a usable local diagnostic workbench, not just a static HTML export.
