# Failure-mode validation harness

Offline, disposable scenarios that prove Doctor link solve/assist contracts beyond happy-path preflight.

| Scenario | Expected |
| --- | --- |
| Multi-file production repair | `verified` |
| Wrong/partial AI repair | `failed` |
| Multi-file test tampering | `blocked` (`verification_inputs_modified`) |
| Explicit verification-input changes | `review_required` |
| Off-by-one assist reproduction | `reproduced` |
| Public Node.js corpus pins | present in `examples/public-project-validation/projects.json` |

No network and no Codex CLI are required. The runner uses scripted repair executors.

```bash
python examples/failure-mode-validation/run.py --out /tmp/doctor-link-failure-modes
```

This complements:

- the 24-scenario real-project corpus (`examples/real-project-benchmark/`)
- pinned public-project preflight (`examples/public-project-validation/`)
