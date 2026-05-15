# AI Code / Codex Handoff Template

Use this template when handing a Doctor link diagnostic package to an AI Coding tool.

```markdown
# Repair Task

Use the attached Doctor link diagnostic package as the source of truth.

## Required rules

- Treat human user assertions as first-class diagnostic signals.
- Do not dismiss a user-confirmed problem without evidence.
- Use evidence before making conclusions.
- Stay within the investigation boundary.
- Do not claim the issue is fixed until verification evidence supports it.

## Inputs to review

1. `summary.md`
2. `problem-map.md`
3. `timeline.md`
4. `evidence-list.md`
5. `user-assertions.json`
6. `ai-task.md`
7. `investigation-boundary.md`
8. `fix-verification-checklist.md`
9. `verification-result.json`
10. `report-comparison.json` when available

## Expected output

- Root cause with evidence references.
- Minimal repair plan.
- Files changed.
- Tests run.
- Verification evidence.
- Any remaining uncertainty.
```
