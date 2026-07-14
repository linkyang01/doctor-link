# Doctor link

[![Doctor link CI](https://github.com/linkyang01/doctor-link/actions/workflows/ci.yml/badge.svg)](https://github.com/linkyang01/doctor-link/actions/workflows/ci.yml)
[![Python 3.10–3.14](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue)](https://github.com/linkyang01/doctor-link/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Doctor link is a local-first, human-AI shared diagnostic and verified-repair layer for software projects.

Doctor link 是一个本地优先、面向软件项目的人机协同诊断与修复验收层。它不仅组织问题、证据和 AI 上下文，还能在明确授权后驱动 Codex 修复 Python 或 Node.js JavaScript/TypeScript 项目，并独立重测是否真正解决。

- [English documentation](docs/readme/README.en.md)
- [中文文档](docs/readme/README.zh-CN.md)
- [GitHub repository guide](docs/github-repository-guide.md)

## Why Doctor link

AI coding tools can edit code quickly, but they still need reliable context. Doctor link helps a person and an AI tool agree on:

- what the problem is;
- which evidence supports it;
- which claims came from a human;
- which commands reproduced the behavior;
- what changed before and after a fix;
- which checks are required before closure.

Doctor link does not replace Codex, Cursor, Aider, OpenHands, Continue, Cline, Windsurf, or similar tools. It prepares a structured, privacy-aware diagnostic package that those tools can consume.

## Verified status

Latest published version: [`v0.5.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.5.0), published on 2026-07-14.

Version `v0.5.0` adds natural-language reproduction discovery, a guided `doctor-link assist` entrypoint with a local browser result, and a 24-project Python/Node.js benchmark corpus. It passed 363 tests at 85.06% branch-aware coverage, all 66 installed CLI routes through 75 invocations and twelve complex scenarios, and Python 3.10–3.14 plus Ubuntu, macOS, Windows, packaging, and security gates. PR [#150](https://github.com/linkyang01/doctor-link/pull/150) merged as `ac5c2f5`; [release workflow 29305612221](https://github.com/linkyang01/doctor-link/actions/runs/29305612221) published the immutable tag and assets with PyPI disabled.

The verified automatic problem-solving release in [PR #145](https://github.com/linkyang01/doctor-link/pull/145) passed the complete repository validation matrix on 2026-07-13:

- 319 automated tests;
- 85.39% branch-aware coverage with an enforced 85% floor;
- Python 3.10, 3.11, and 3.12;
- Ubuntu, macOS, and Windows smoke validation;
- Ruff, Bandit, and dependency vulnerability checks;
- wheel and source-distribution build, content inspection, Twine validation, and isolated installation;
- E2E, self-validation, project validation, and P7 runtime validation;
- all 63 public CLI routes through 71 real installed-package invocations and nine complex scenarios.

Evidence:

- [100/100 repository-readiness scorecard](docs/validation/local-quality-scorecard.md)
- [cloud validation certificate](docs/validation/cloud-validation-certificate.md)
- [validation evidence index](docs/validation/validation-evidence-index.md)
- [v0.2.0 final PR CI](https://github.com/linkyang01/doctor-link/actions/runs/29256743976)
- [v0.2.0 Release workflow](https://github.com/linkyang01/doctor-link/actions/runs/29256955705)

PR #145 was merged as commit `40a547c`, and the authorized [GitHub Release `v0.2.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.2.0) was published by [release workflow 29256955705](https://github.com/linkyang01/doctor-link/actions/runs/29256955705). The workflow installed the final wheel, reran the full capability lab, and created an immutable tag before uploading both distributions. PyPI publication was disabled and was not performed.

## Main capabilities

| Capability | What it provides |
| --- | --- |
| Preflight | Read-only inspection of project configuration, commands, catalogs, Python version, and local tools. |
| Diagnostic packages | Structured reports, summaries, evidence indexes, timelines, problem maps, and machine-readable JSON. |
| Evidence collection | Logs, attachments, environment metadata, command results, redaction records, and integrity indexes. |
| Human assertions | Explicit records of user-confirmed problems that AI output must not silently dismiss. |
| Reproduction and tests | Shell-free configured command execution, test matrices, evidence write-back, and timeout metadata. |
| Guided problem solving | Ordinary-language problem matching, ranked safe reproduction checks, local browser results, and repair preview without requiring test-command knowledge. |
| Automatic solve | Python and Node.js JavaScript/TypeScript failure reproduction, explicit repair approval, isolated Git branch, bounded Codex rounds, protected verification inputs, and independent regression acceptance. |
| Verification | Missing-evidence reporting, linked assertion coverage, failed-test blockers, before/after comparison, and conservative closure status. |
| AI handoff | Tool-specific packages with explicit repair, evidence, and verification-review readiness states. |
| Local workbench | Static local HTML for reviewing diagnostic packages without a hosted service. |
| Security and privacy | Redaction, privacy scanning, export gates, integrity manifests, and explicit execution approval. |
| Extensibility | Adapter and plugin manifests with dry-run defaults, permission checks, and audit records. |
| Operations | CI reports, project health, local knowledge indexes, archives, and distribution readiness. |

## Quick start

Requirements: Git and Python 3.10 or later.

Current support scope:

- guided diagnosis and diagnostic packages for local software projects;
- verified automatic repair for clean Git repositories containing Python or Node.js JavaScript/TypeScript projects;
- Node.js repair requires the project's package manager and runtime;
- automatic edits require an installed, authenticated Codex CLI and explicit `--allow-repair` approval;
- other language ecosystems and PyPI installation are not yet supported.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install https://github.com/linkyang01/doctor-link/releases/download/v0.5.0/doctor_link-0.5.0-py3-none-any.whl
doctor-link --version
doctor-link preflight . --json
```

For the simplest path, describe the problem and let Doctor link find and validate a reproduction:

```bash
doctor-link assist /path/to/project --problem "Checkout duplicates a charge"
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Create a first diagnostic package:

```bash
doctor-link report . --out DoctorReports
PACKAGE_DIR=$(find DoctorReports -mindepth 1 -maxdepth 1 -type d | head -n 1)
doctor-link collect "$PACKAGE_DIR" --project-root . --command "python --version"
doctor-link verify "$PACKAGE_DIR" --write-back
doctor-link view "$PACKAGE_DIR" --build-only
```

See [Quick Start](docs/quick-start.md) and [Installation](docs/installation.md) for Windows alternatives and complete validation instructions.

Automatically solve a reproducible Python or Node.js-project problem:

```bash
# Preview only: reproduces the issue and writes the repair plan.
doctor-link solve /path/to/project \
  --problem "Checkout creates two charges" \
  --test-command "python -m pytest tests/test_checkout.py -q"

# Explicitly authorize branch creation and Codex edits.
doctor-link solve /path/to/project \
  --problem "Checkout creates two charges" \
  --test-command "python -m pytest tests/test_checkout.py -q" \
  --allow-repair
```

For a Node.js project with a non-placeholder `scripts.test`, Doctor link automatically selects `npm test`, `pnpm test`, `yarn test`, or `bun run test` from `packageManager` and lockfile evidence. If no test script exists but JavaScript test files are present, it falls back to `node --test`:

```bash
doctor-link solve /path/to/node-project \
  --problem "Concurrent updates lose the latest value" \
  --test-command "npm test" \
  --allow-repair
```

See [Automatic Solve with Codex](docs/automatic-solve.md) for command discovery, status codes, evidence files, and rollback.

For an npm, Yarn, or pnpm workspace, keep the repository root and select a package with `--package packages/name`. Interrupted repair receipts can continue with `doctor-link solve --resume SESSION_DIR --allow-repair`. Repeatable multi-project suites use `doctor-link benchmark benchmark.yml --out DoctorReports/benchmark` and report reproduction and repair-success metrics.

## Typical diagnostic workflow

```text
preflight → report → collect → assert → reproduce/test → verify → handoff/view
```

For the automatic Python or Node.js path, the complete workflow is:

```text
solve preview → explicit approval → repair branch → Codex round → protected-input check → independent verification → verified/blocked/failed
```

1. `preflight` checks readiness without running repository commands.
2. `report` creates the diagnostic package.
3. `collect` adds reviewed evidence and command output.
4. `assert` records human-confirmed behavior.
5. `reproduce` and `test` execute explicitly configured checks without a shell.
6. `verify` identifies missing evidence and determines closure status.
7. `handoff` or `view` prepares AI context or a local review interface.

Failed reproductions, failed required test jobs, and incomplete verification return a non-zero exit code even when `--json` is used. See [Automated diagnosis reliability](docs/automated-diagnosis-reliability.md) for the complete evidence and status rules.

## Safety model

- Doctor link is local-first and does not upload diagnostic packages by default.
- Reproduction and test-matrix commands do not invoke a shell; pipelines, redirection, command substitution, and unsafe operators are rejected.
- Adapter and plugin execution is dry-run by default and requires explicit `--allow-run` approval.
- Automatic code repair requires `--allow-repair`, a clean Git working tree, and a failing executable check. Codex remains sandboxed to workspace-write; Doctor link does not auto-commit or push.
- Automatic repair hash-protects tests, package manifests and lockfiles, test configuration, reproduction/test catalogs, and directly referenced verification scripts. Protected-input changes block `verified`; the explicit exception `--allow-verification-changes` returns `review_required` instead of success.
- `--allow-repair` invokes the authenticated Codex service and may send the bounded prompt, failing output, and inspected repository context. Review the preview and remove sensitive data before authorization.
- Generated packages may still contain project-sensitive evidence. Review privacy and redaction reports before sharing them.
- Do not attach secrets or private diagnostic packages to public GitHub issues.

Read [SECURITY.md](SECURITY.md), [sensitive data handling](docs/sensitive-data-handling.md), and the [export security checklist](docs/export-security-checklist.md).

## Development validation

```bash
python -m pip install -e '.[dev]'
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-branch --cov-fail-under=85
bandit -r doctor_link -ll
pip-audit
python -m build
python scripts/validate_distribution_contents.py dist
python -m twine check dist/*
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

GitHub Actions runs the full Python matrix, security checks, package installation, and cross-platform smoke checks for pull requests targeting `main`.

## Repository map

| Path | Purpose |
| --- | --- |
| `doctor_link/` | Python package and CLI runtime. |
| `.doctorlink/` | Repository-owned diagnostic strategies, catalogs, and configuration. |
| `tests/` | Unit, integration, regression, packaging, security, and documentation tests. |
| `scripts/` | E2E, self-validation, package-content, and release helper scripts. |
| `schemas/` | Versioned diagnostic package schemas. |
| `examples/` | Example projects, configurations, handoff data, and diagnostic packages. |
| `docs/` | User guides, architecture, validation evidence, release policy, and historical audits. |
| `.github/` | Issue template, PR template, Dependabot, CI, manual validation, self-validation, and release workflows. |

## Documentation map

- [Quick Start](docs/quick-start.md)
- [Installation](docs/installation.md)
- [PyPI trusted publishing](docs/pypi-publishing.md)
- [CLI reference](docs/cli-reference.md)
- [Automated diagnosis reliability](docs/automated-diagnosis-reliability.md)
- [Automatic Solve with Codex](docs/automatic-solve.md)
- [Full capability validation](docs/full-capability-validation.md)
- Platform integration roadmap: [English](docs/platform-integration-roadmap.md) | [中文](docs/platform-integration-roadmap.zh-CN.md)
- [Product overview](docs/product-overview.md)
- [Architecture overview](docs/architecture-overview.md)
- [GitHub repository and workflow guide](docs/github-repository-guide.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Project status](docs/project-status.md)
- [Validation certification](docs/validation/README.md)
- [Release policy](docs/release-policy.md)

## Project boundaries

Doctor link currently does not provide a hosted web platform, cloud synchronization, an external account system, telemetry, a marketplace, production key management, hosted enterprise archives, hosted diagnostic knowledge bases, or production RBAC. Those capabilities must not be inferred from planning documents.

## License

Doctor link is licensed under the [MIT License](LICENSE).
