# Example AI Handoff Package

This example shows the expected structure of an AI Coding handoff package.

```text
handoff/
├── handoff-manifest.json
├── CODEX_TASK.md
├── ai-task.md
├── ai-context.json
└── fix-verification-checklist.md
```

## Rule

AI tools may use this package to propose or implement repairs, but the AI claim is not verification evidence. Doctor link verification must still be run after changes.
