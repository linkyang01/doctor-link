# Deep diagnostics clean-install validation

Date: 2026-07-15

The current `codex/deep-error-diagnostics` source was built as version `0.5.1` into a fresh wheel and source distribution. The artifacts passed distribution-content inspection and Twine metadata validation. A new Python 3.12 virtual environment then installed the wheel and all declared dependencies from package indexes without using the source checkout.

## Artifact results

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `doctor_link-0.5.1-py3-none-any.whl` | 214,705 bytes | `f59dfd4c7b7b0f7d58a4a96f7e3112a836d084547e6ed574c272a228d735cf81` |
| `doctor_link-0.5.1.tar.gz` | 469,955 bytes | `7c6475d48a52c261893f7e4446a0bfcdb1df7e4222b58bc089903ad06e525cae` |

The wheel contains `explain_cli.py`, `solve_cli.py`, `root_cause.py`, `hypothesis_verifier.py`, and `repair_guidance.py`. `pip check` reported no broken requirements. Runtime imports resolved from the clean environment's `site-packages`, not the repository.

## Installed-wheel smoke tests

1. `doctor-link --version` returned `0.5.1`.
2. Installed `explain --help` exposed `--verify-hypothesis`.
3. Installed `solve --help` exposed `--require-grounded-root-cause`.
4. A temporary Git project committed `app.py` with `return 5`, then received an uncommitted `return 4` regression.
5. Installed `explain --verify-hypothesis` selected `app.py:2` in `total`, returned `confirmed`, generated `actionable` repair guidance, restored exact original regression bytes, and reported `worktree_unchanged=true`.
6. Both `explain-session.json` and `root-cause.md` were written.
7. A separate clean Git project failed only because a third-party module was missing. Installed `solve --require-grounded-root-cause` returned `blocked`, recorded `grounded_root_cause_required`, and created no repair branch.

The host's default `python3` is Python 3.9.6. A first installation attempt was correctly rejected because Doctor Link requires Python 3.10 or later. Installation then succeeded in a fresh Python 3.12.13 environment. This is expected compatibility enforcement, not an artifact failure.

## Limits

This validates local macOS/Python 3.12 artifacts before a version bump. It is not a PyPI publication, GitHub Release, or cross-platform cloud certificate. The artifacts remain temporary validation outputs and must be rebuilt from the final merged release commit.
