# Adversarial deep-diagnosis validation

Date: 2026-07-15

This validation targets misleading and unsafe cases rather than ordinary success paths. It combines four dedicated adversarial scenarios with existing safety regressions that exercise the same production interfaces.

| Scenario | Required behavior | Result |
| --- | --- | --- |
| Multi-file test → service → repository traceback | Preserve the project-owned call path in order | PASS |
| Unrelated recent source change plus a different production stack path | Mark the disagreement as conflicting evidence; do not claim stack support for the unrelated file | PASS |
| Focused repair check passes but full regression fails | Return `failed`; never return `verified` | PASS |
| Missing third-party dependency | Treat `<string>` and dependency frames as non-project evidence; block grounded repair before branch creation | PASS |
| Opaque failing command with grounded-root-cause gate | Block before branch creation | PASS |
| Repair edits protected tests/configuration | Block acceptance with `verification_inputs_modified` | PASS |
| Diagnostic command pollutes the worktree | Return `modified_worktree` or `unsafe_to_test` | PASS |
| Counterfactual experiment completes | Restore exact original bytes and complete worktree fingerprint | PASS |

The adversarial suite exposed and fixed two real defects. Changed-file location fallback was incorrectly described as stack evidence even when the stack did not contain that file. Also, Python's synthetic `<string>` traceback frame was incorrectly treated as project production code, allowing a dependency error through the grounded-evidence gate.

After repair, all eight adversarial expectations pass. The pinned Click, p-limit, and Chalk capability harness also remains **3/3 PASS**, demonstrating that the stricter project-frame rules and conflict warning did not regress the controlled real-project scenarios.

## Interpretation

When changed files and production stack frames disagree, Doctor link keeps the changed file as an advisory first hypothesis because assertion failures often omit the earlier data-transform function from their stack. It now labels that disagreement explicitly and requires a counterfactual experiment to confirm or reject the changed-file hypothesis. This avoids both unsafe overconfidence and the real-project regression caused by blindly preferring the terminal stack.

These tests prove the stated deterministic scenarios. They do not establish universal root-cause accuracy, autonomous repair quality for arbitrary repositories, or production incident coverage.
