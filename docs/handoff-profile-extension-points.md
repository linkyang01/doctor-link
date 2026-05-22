# Handoff Profile Extension Points

Doctor link handoff profiles format diagnostic packages for AI Coding tools.

P5 documents extension points without adding a stable plugin runtime.

## Existing profile concept

A handoff profile can adjust:

- instruction filename;
- AI task wording;
- included package files;
- tool-specific warnings;
- verification reminders.

Existing profiles include generic AI Coding tools and common local workflows.

## Handoff contract

A handoff package should include:

- `handoff-manifest.json`;
- an instruction file for the target tool;
- `ai-task.md`;
- `ai-context.json` when available;
- verification checklist when available;
- explicit human-confirmed issue warning.

## Safety rule

A handoff profile must not remove the rule that AI claims are not verification evidence.

A handoff profile must not hide unresolved user assertions.

## Future extension boundary

Future work may add a registry or SDK for handoff profiles. P5 only documents the expected shape and safety rules.
