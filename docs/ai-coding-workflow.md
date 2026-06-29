# AI Coding Workflow Guide

Doctor link prepares diagnostic context for AI Coding tools. It does not replace those tools.

## Workflow

1. Create or update a diagnostic package.
2. Add user-confirmed issues with `doctor-link assert`.
3. Collect evidence with `doctor-link collect`.
4. Run verification planning with `doctor-link verify`.
5. Generate AI handoff with `doctor-link handoff`.
6. Paste the generated task into an AI Coding tool.
7. Record the AI repair result with `doctor-link ai-result`.
8. Run `doctor-link assertion-check` and `doctor-link risk-review`.
9. Re-run verification.

## Handoff profiles

Supported handoff profiles include:

- `generic`
- `codex`
- `cursor`
- `continue`
- `aider`
- `openhands`
- `claude-code`
- `grok`
- `windsurf`
- `cline`

Example:

```bash
doctor-link handoff "$PACKAGE_DIR" --tool codex --out DoctorReports/handoff
```

## Human-confirmed issue rule

AI must not dismiss a human-confirmed issue as normal behavior without evidence.

## Verification rule

AI output is not verification evidence. A claimed fix must be verified through Doctor link verification, tests, comparison, or evidence review.
