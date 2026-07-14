# Doctor link Quick Start

This guide takes Doctor link from a clean source checkout to a useful result on your own project. Choose the guided diagnosis path when you want evidence and a report, or the verified-repair path when you already have a failing test.

## 1. Install the current release

Requirements: Git and Python 3.10 through 3.14.

Current release: `v0.5.1`.

```bash
python -m venv .venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install and confirm the CLI:

```bash
python -m pip install --upgrade pip
python -m pip install doctor-link==0.5.1
doctor-link --version
doctor-link preflight . --json
```

`preflight` is read-only. It checks configuration, command safety, runtime catalogs, Python, and local tools without running project-owned commands.

## 2. Choose the shortest path to your goal

### Path A: guided diagnosis

Use the interactive wizard when you want Doctor link to ask what it needs:

```bash
doctor-link wizard --folder /path/to/your/project
```

The wizard can collect evidence, create a local diagnostic package, build an HTML workbench, and prepare an AI handoff. It prints the exact files to open or share.

### Path B: one-command diagnosis

Use a single non-interactive command when the problem is already easy to describe:

```bash
doctor-link diagnose-now /path/to/your/project \
  --full \
  --summary "checkout creates a duplicate charge"
```

Add `--handoff` to prepare a reviewed package for an AI coding tool:

```bash
doctor-link diagnose-now /path/to/your/project \
  --full \
  --handoff \
  --tool codex \
  --summary "checkout creates a duplicate charge"
```

### Path C: reproduce and verify an automatic repair

Start with a preview. Doctor link runs the independent check and writes the bounded repair task, but does not edit code:

```bash
doctor-link solve /path/to/your/project \
  --problem "checkout creates a duplicate charge" \
  --test-command "python -m pytest tests/test_checkout.py -q"
```

For a Node.js project, use its project-owned test command:

```bash
doctor-link solve /path/to/your/node-project \
  --problem "concurrent updates lose the latest value" \
  --test-command "npm test"
```

When the preview returns `approval_required`, review the generated prompt and protected inputs. Only then authorize an isolated repair branch and Codex edits:

```bash
doctor-link solve /path/to/your/project \
  --problem "checkout creates a duplicate charge" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --allow-repair
```

The target must be a clean Git repository. Doctor link independently reruns the original check after every repair round and returns `verified` only when the check passes without unauthorized changes to tests or verification configuration.

## 3. Understand the result

Common automatic-solve states:

| Status | Meaning |
| --- | --- |
| `approval_required` | The failure was reproduced and a repair preview is ready; no edit occurred. |
| `verified` | Independent checks passed and protected verification inputs stayed acceptable. |
| `not_reproduced` | The supplied checks already pass; Doctor link will not authorize an edit. |
| `blocked` | Repository, toolchain, command safety, or verification-contract requirements were not met. |
| `review_required` | Verification inputs changed with explicit authorization and require human review. |
| `failed` | The bounded repair rounds ended without a verified result. |

Every path writes local receipts. Automatic solve records the baseline, prompts, repair rounds, verification output, protected-input hashes, blockers, and rollback guidance under the printed solve-session directory.

## 4. Review local reports

Build a home page for recent diagnostic packages:

```bash
doctor-link home --reports DoctorReports
```

Open the printed `index.html` path in a browser. For individual packages, `doctor-link view <package>` builds or serves the local workbench.

## 5. Go deeper only when needed

- [Automatic Solve with Codex](automatic-solve.md) explains command discovery, approval, branches, protected inputs, and rollback.
- [Diagnostic package format](diagnostic-package-format.md) explains evidence and report files.
- [CLI reference](cli-reference.md) lists advanced collection, verification, privacy, integrity, adapter, plugin, archive, and CI commands.
- [Troubleshooting](troubleshooting.md) covers missing tools, permissions, invalid configuration, and sensitive-data handling.

## Safety boundary

Doctor link is local-first and does not upload project evidence by default. Review configured commands before executing them, inspect diagnostic and handoff packages before sharing, and remove credentials or private customer data. Automatic repair requires explicit approval and never commits, pushes, publishes, or merges changes for you.
