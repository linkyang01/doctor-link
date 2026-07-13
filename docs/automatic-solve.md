# Automatic Solve with Codex

`doctor-link solve` turns a concrete Python-project problem into a bounded repair and verification session. It is the shortest path from “this behavior is wrong” to a reviewable fix.

## What it does

The command performs six distinct jobs:

1. confirms that the target is a Python Git repository with a clean working tree;
2. discovers or accepts shell-free reproduction and regression commands;
3. runs those commands to prove the problem exists;
4. after explicit approval, creates a `doctor-link/solve-*` branch and invokes `codex exec` in a workspace-write sandbox;
5. snapshots the tests, test configuration, configured catalogs, and directly referenced verification scripts that define the original acceptance contract;
6. independently reruns every required command after each repair round and accepts the fix only when they all pass against unchanged protected inputs.

Doctor link saves the complete local receipt. A successful Codex exit, an agent message that says “fixed,” or a generated patch is not sufficient by itself.

Changing a test until it passes is also not sufficient. Protected verification inputs are hashed before repair and compared after every round. Their default modification is a release-blocking `verification_inputs_modified` result, even when the modified checks pass.

## Prerequisites

- Python 3.10 or later;
- a Python project at the Git repository root;
- a clean Git working tree;
- at least one executable reproduction or test command;
- Codex CLI installed and authenticated for live repair.

The first release intentionally supports Python projects only. Other project types return `blocked` instead of falling through to an unverified generic repair.

## Step 1: reproduce and preview

Run without `--allow-repair` first:

```bash
doctor-link solve /path/to/project \
  --problem "Checkout creates two charges" \
  --reproduce-command "python -m pytest tests/test_checkout.py::test_single_charge -q" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --json
```

If at least one required command fails, the result is `approval_required` and exit code `2`. Doctor link writes `repair-prompt-preview.md` but does not create a branch, invoke Codex, or edit code.

If all commands pass, the result is `not_reproduced` and exit code `3`. Supply a command that fails while the reported problem exists; Doctor link will not authorize speculative edits.

## Step 2: authorize repair

After reviewing the preview:

```bash
doctor-link solve /path/to/project \
  --problem "Checkout creates two charges" \
  --reproduce-command "python -m pytest tests/test_checkout.py::test_single_charge -q" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --allow-repair
```

Doctor link then:

- rechecks that the repository is still clean;
- creates an isolated `doctor-link/solve-<problem>-<session>` branch;
- calls `codex exec --sandbox workspace-write --json` without bypassing the sandbox;
- limits the run to three repair rounds by default;
- reruns all required checks after every round;
- compares protected verification inputs with the original snapshot after every round;
- returns `verified` only when all required checks pass without changing the original acceptance contract.

Use `--max-rounds 1`, `2`, or `3` to reduce the retry budget. Use `--command-timeout` and `--repair-timeout` to set separate limits for project checks and Codex work.

If a repair legitimately requires a test or verification configuration change, add `--allow-verification-changes` together with `--allow-repair`. This is an exception path: passing checks return `review_required` with exit code `6`, never `verified`, and every changed protected file remains in the receipt for human review.

## Automatic command discovery

When command flags are omitted, Doctor link reads:

- command or test entries from `.doctorlink/reproduce.yml`;
- jobs from `.doctorlink/test-matrix.yml`;
- `python -m pytest` as a fallback when a `tests/` directory exists and no test matrix is configured.

Configured commands use the existing shell-free Doctor link runner. Quoted arguments, leading environment assignments, and `&&` sequences are supported. Pipes, redirection, semicolons, background execution, and other shell control operators are rejected.

## Session evidence

By default, solve evidence is placed outside the target Git repository at:

```text
<project-parent>/DoctorReports/<project-name>/solve-<session-id>/
├── solve-session.json
├── solve-summary.md
├── repair-prompt-preview.md       # preview sessions
└── round-1/
    ├── prompt.md
    ├── codex-events.jsonl
    ├── codex-stderr.log
    ├── verification.json
    └── verification-input-changes.json
```

Later rounds use `round-2/` and `round-3/`. Pass `--out <directory>` to select a different parent directory.

## Status and exit codes

| Status | Exit | Meaning |
| --- | ---: | --- |
| `verified` | 0 | Codex repair completed and every required independent check passed. |
| `approval_required` | 2 | The problem was reproduced; code was not changed because approval is missing. |
| `not_reproduced` | 3 | All supplied or discovered checks already pass. |
| `blocked` | 4 | A safety or readiness condition prevents repair. |
| `failed` | 5 | The repair-round limit was exhausted while verification still failed. |
| `review_required` | 6 | Checks pass only after explicitly authorized protected-input changes; human review is mandatory. |

## Safety and rollback

- Doctor link refuses a dirty working tree so existing user changes are not confused with AI edits.
- Reproduction and test commands run before branch creation and are checked again for unexpected repository changes.
- Tests, test configuration, reproduction/test catalogs, and directly referenced verification scripts are hash-protected by default.
- A repair that changes protected verification inputs cannot return `verified`; without exception approval it is blocked immediately.
- Codex receives workspace-write access only after `--allow-repair`.
- Doctor link never passes `--dangerously-bypass-approvals-and-sandbox`.
- Codex is instructed not to switch branches, commit, push, publish, or edit outside the workspace.
- Doctor link does not automatically commit or push a verified change. Review the diff first.

`--allow-repair` is also the network/data boundary. Doctor link sends the bounded prompt, failing command output, and the repository context Codex chooses to inspect through the user's existing Codex CLI authentication. Review the prompt preview and remove secrets or customer data before authorizing repair. Solve receipts remain local, but the Codex run is not an offline operation unless the user has separately configured a supported local provider outside this first release.

To abandon a repair, switch back to the original branch and delete the repair branch after confirming that no wanted changes remain:

```bash
git switch <original-branch>
git branch -D <doctor-link/solve-branch>
```

## Examples of suitable problems

- a Python API returns `200` while its persisted transaction failed;
- a checkout retry creates duplicate charges under a timing edge case;
- a cache invalidation bug appears only when two configuration flags are combined;
- a parser succeeds for simple files but corrupts nested Unicode data;
- an authorization test passes for administrators but leaks data across tenants.

The quality of the result depends on a command that makes the failure observable. A vague description without an executable check remains useful diagnostic context, but it is not sufficient for automatic closure.

## Codex references

Doctor link's executor follows OpenAI's documented [`codex exec` non-interactive mode](https://developers.openai.com/codex/noninteractive) and the [Codex developer command reference](https://developers.openai.com/codex/cli/reference): explicit workspace selection, `workspace-write` sandboxing for edits, JSONL event output, and no dangerous sandbox bypass.
