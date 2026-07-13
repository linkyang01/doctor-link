# Doctor link

[![Doctor link CI](https://github.com/linkyang01/doctor-link/actions/workflows/ci.yml/badge.svg)](https://github.com/linkyang01/doctor-link/actions/workflows/ci.yml)
[![Python 3.10–3.12](https://img.shields.io/badge/python-3.10%E2%80%933.12-blue)](https://github.com/linkyang01/doctor-link/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Doctor link is a local-first, human-AI shared diagnostic layer for software projects.

Doctor link 是一个本地优先、面向软件项目的人机协同诊断层。它把问题描述、运行证据、人工确认、AI 修复上下文和验证结果组织成同一套可追踪的诊断包。

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

Source version: `0.1.2` release candidate.

The repaired implementation in [PR #134](https://github.com/linkyang01/doctor-link/pull/134) passed the complete repository validation matrix on 2026-07-13:

- 273 automated tests;
- 85.09% branch-aware coverage with an enforced 85% floor;
- Python 3.10, 3.11, and 3.12;
- Ubuntu, macOS, and Windows smoke validation;
- Ruff, Bandit, and dependency vulnerability checks;
- wheel and source-distribution build, content inspection, Twine validation, and isolated installation;
- E2E, self-validation, project validation, and P7 runtime validation.

Evidence:

- [100/100 repository-readiness scorecard](docs/validation/local-quality-scorecard.md)
- [cloud validation certificate](docs/validation/cloud-validation-certificate.md)
- [validation evidence index](docs/validation/validation-evidence-index.md)
- [100-point certification Actions run](https://github.com/linkyang01/doctor-link/actions/runs/29221918410)

`v0.1.2` has not been published. Passing CI does not authorize a release, tag, GitHub Release, or PyPI upload.

## Main capabilities

| Capability | What it provides |
| --- | --- |
| Preflight | Read-only inspection of project configuration, commands, catalogs, Python version, and local tools. |
| Diagnostic packages | Structured reports, summaries, evidence indexes, timelines, problem maps, and machine-readable JSON. |
| Evidence collection | Logs, attachments, environment metadata, command results, redaction records, and integrity indexes. |
| Human assertions | Explicit records of user-confirmed problems that AI output must not silently dismiss. |
| Reproduction and tests | Shell-free configured command execution, test matrices, evidence write-back, and timeout metadata. |
| Verification | Missing-evidence reporting, assertion coverage, before/after comparison, and closure status. |
| AI handoff | Tool-specific packages for Codex, Cursor, Cline, Windsurf, Grok Build, and generic AI workflows. |
| Local workbench | Static local HTML for reviewing diagnostic packages without a hosted service. |
| Security and privacy | Redaction, privacy scanning, export gates, integrity manifests, and explicit execution approval. |
| Extensibility | Adapter and plugin manifests with dry-run defaults, permission checks, and audit records. |
| Operations | CI reports, project health, local knowledge indexes, archives, and distribution readiness. |

## Quick start

Requirements: Git and Python 3.10 or later.

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
doctor-link --version
doctor-link preflight . --json
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

## Typical diagnostic workflow

```text
preflight → report → collect → assert → reproduce/test → verify → handoff/view
```

1. `preflight` checks readiness without running repository commands.
2. `report` creates the diagnostic package.
3. `collect` adds reviewed evidence and command output.
4. `assert` records human-confirmed behavior.
5. `reproduce` and `test` execute explicitly configured checks without a shell.
6. `verify` identifies missing evidence and determines closure status.
7. `handoff` or `view` prepares AI context or a local review interface.

## Safety model

- Doctor link is local-first and does not upload diagnostic packages by default.
- Reproduction and test-matrix commands do not invoke a shell; pipelines, redirection, command substitution, and unsafe operators are rejected.
- Adapter and plugin execution is dry-run by default and requires explicit `--allow-run` approval.
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
- [CLI reference](docs/cli-reference.md)
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
