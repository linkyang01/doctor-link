# Real-project Reproduction Benchmark

This corpus materializes 24 isolated Git projects: twelve Python and twelve Node.js services covering payments, authorization, cache consistency, Unicode, concurrency, configuration, retry accounting, pagination, timezone conversion, transaction rollback, path traversal, and rate limits.

Every scenario starts with an observable production defect and an unchanged acceptance test. The runner asks Doctor link to derive a reproduction command from the ordinary-language problem, execute it, and stop at the repair approval gate. No Codex call or code edit occurs.

```bash
python examples/real-project-benchmark/run.py \
  --doctor-link "$(command -v doctor-link)" \
  --out /tmp/doctor-link-real-project-benchmark
```

The benchmark passes only when all 24 scenarios are genuinely reproduced and return `approval_required`. Results include selected reproduction commands, per-session receipts, reproduction rate, duration, and expectation matches.
