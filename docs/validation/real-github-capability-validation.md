# Real GitHub capability validation

Date: 2026-07-15

This validation goes beyond configuration-only preflight. Three pinned public repositories ran their native tests, received one reversible production-code mutation, and were diagnosed without changing their test contracts.

## Projects and baseline

| Project | Commit | Native clean baseline | Injected production fault |
| --- | --- | --- | --- |
| Click 8.3.0 | `00fadb8904387158ce6e9aa1573be770446895c1` | 1284 passed, 22 skipped, 1 expected failure | command-name string conversion adds an invalid prefix |
| p-limit 7.2.0 | `7bdd25c703337360236722ed7d4da5ffadcb7a08` | 18 AVA tests passed | concurrency comparison permits one extra active task |
| Chalk 5.6.2 | `51557784b829c87ff8d138206598764f2eb957b1` | 32 AVA tests passed | ANSI style application returns unstyled text |

## Result

Doctor link reproduced all three faults from ordinary-language problem descriptions. Click selected a focused `tests/test_commands.py` command; both Node projects selected their declared `npm test` entrypoint. All failures were classified as reproduced rather than setup failures.

Advisory explanation ranked the actual changed production file first in every scenario and identified the exact mutation location and enclosing function: `src/click/utils.py:56` in `make_str`, `index.js:11` in `resumeNext`, and `source/index.js:199` in `applyStyle`. Every scenario also produced a structured failure record and a project-owned call chain (10 Click nodes, 2 p-limit nodes, and 20 Chalk nodes). With `--verify-hypothesis`, temporarily restoring each candidate to `HEAD` made its previously failing check pass, so all three hypotheses were classified `confirmed`. Each generated repair guidance record was `actionable`, contained a focused verification command, and separated facts from inference. Exact original bytes and the complete initial worktree state were restored after every experiment. Result: **3/3 passed**.

## Scope and limitations

The injected faults are controlled mutations applied to real upstream source and validated by real upstream tests. They demonstrate discovery, execution, failure classification, advisory file localization, and worktree safety. They do not claim autonomous AI repair quality, production incident coverage, or that a changed file proves root cause. Changed-file hints remain explicitly advisory and may be unrelated in a naturally dirty repository.

Reproduction instructions and the immutable scenario manifest are under `examples/real-github-capability-validation/`. Machine-readable evidence is under `docs/validation/evidence/real-github-capability-2026-07-15/`.
