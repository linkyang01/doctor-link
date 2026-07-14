# Failure-mode validation harness

Status date: 2026-07-14  
Tracking: [#161](https://github.com/linkyang01/doctor-link/issues/161)

## Purpose

Repeatably exercise non-happy-path solve/assist contracts that public-project preflight cannot cover:

1. Multi-file production bugs and hash-protected tests
2. Wrong AI repair → `failed`
3. `--allow-verification-changes` → `review_required`
4. Non-trivial logic/off-by-one assist reproduction
5. Presence of pinned public Node.js demo projects

## Location

| Path | Role |
| --- | --- |
| `examples/failure-mode-validation/run.py` | Scenario materializer + runner |
| `examples/failure-mode-validation/README.md` | Operator notes |
| `tests/test_failure_mode_validation.py` | Offline CI gate |

## How to run

```bash
python examples/failure-mode-validation/run.py --out DoctorReports/failure-mode-validation
```

## Evidence

Recorded run: [`docs/validation/evidence/failure-mode-validation-2026-07-14/`](evidence/failure-mode-validation-2026-07-14/) — **6/6 PASS**.

## Boundaries

- Offline fixtures only; no writes to real upstream repositories
- Scripted repair executors stand in for Codex
- Public Node.js scenario only checks pin metadata; it does not clone remotes
