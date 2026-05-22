# Use Case: Non-programmer User

Doctor link helps a non-programmer user capture a clear, evidence-backed problem statement.

## Problem

The user knows that the output is wrong, but AI may dismiss it as acceptable or fail to understand the business expectation.

## Doctor link workflow

1. Create a diagnostic package.
2. Add a human-confirmed issue with `doctor-link assert`.
3. Add screenshots, logs, command output, or notes as evidence.
4. Generate `ai-task.md` for AI repair.
5. Require verification before accepting a fix.

## Value

- The user's confirmation becomes a first-class diagnostic signal.
- AI cannot ignore the issue without evidence.
- Fix acceptance is based on verification, not AI confidence.
