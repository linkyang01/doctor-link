# Use Case: AI Coding Tool

Doctor link prepares structured diagnostic context for AI Coding tools such as Codex, Cursor, Continue, Aider, and OpenHands.

## Problem

AI Coding tools often receive incomplete context and may over-edit, under-test, or ignore user-confirmed issues.

## Doctor link workflow

1. Build or update a diagnostic package.
2. Generate a tool-specific handoff package.
3. Run the AI Coding repair attempt.
4. Record the AI result with `doctor-link ai-result`.
5. Check assertion coverage and repair risk.
6. Verify before closing the issue.

## Value

- Better context for AI repair.
- Reduced guesswork.
- Human-confirmed issues stay visible.
- AI claims are separated from verification evidence.
