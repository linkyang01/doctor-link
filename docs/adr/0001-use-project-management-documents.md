# 0001. Use project management documents

## Status

Accepted

## Context

Doctor link is evolving through continuous discussion, external research, and code implementation. If we rely on memory, the project direction may drift and completed work may not map back to requirements.

We need a lightweight project management system that works directly in the GitHub repository.

## Decision

Use Markdown-based project management files inside the repository.

The project will use:

- `TODO.md` for step-by-step task tracking;
- GitHub Issues for phase-level tracking;
- `docs/adr/` for architecture decision records;
- README files for external project positioning;
- `docs/PROJECT_TARGET_AND_FOUNDATION.md` as the project charter.

## Consequences

Positive:

- Every implementation task has a visible checklist.
- Architectural decisions are preserved with context.
- Future AI coding tools can read project management documents before modifying code.
- The user can inspect progress without reading all code.

Negative:

- Documentation must be maintained as part of the workflow.
- Code changes require updating TODO or related issue status.

## Working rule

No major code work should proceed without a corresponding TODO item or GitHub Issue.
