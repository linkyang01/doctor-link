# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

## Core Positioning

Doctor link is a diagnostic context layer for AI coding workflows.

It follows these principles:

- evidence first;
- reproduction first;
- human-confirmed issues first;
- AI must not dismiss a human-confirmed issue without evidence;
- fixes must be verified;
- local-first and read-only-first;
- protocol and CLI before Web UI.

## Standard Diagnostic Package

Doctor link generates and maintains standard diagnostic packages under `DoctorReports/`, including evidence, timeline, user assertions, verification results, AI collaboration records, workflow metadata, and pipeline summaries.

## Common Commands

```bash
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link collect <package_dir> --project-root . --logs "logs/*.log" --command "python --version"
doctor-link verify <package_dir> --write-back
doctor-link assert <package_dir> --statement "This is the problem"
doctor-link view <package_dir>
doctor-link view DoctorReports

doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ai-result <package_dir> --summary "AI repair summary" --claimed-fix "claimed fix" --assertion-id assertion-1 --verification-step pytest
doctor-link diagnosis-history <package_dir> --ai-pass "round 1" --user-correction "human correction" --evidence-id ev-1
doctor-link assertion-check <package_dir>
doctor-link risk-review <package_dir> --file doctor_link/cli.py --boundary doctor_link/

doctor-link strategy validate . --json
doctor-link reproduce list . --json
doctor-link reproduce run <reproduction_id> . --package-dir <package_dir> --json
doctor-link test list . --json
doctor-link test run . --job <job_id> --package-dir <package_dir> --json
doctor-link diagnose before --project "Demo" --summary "before issue" --out DoctorReports
doctor-link diagnose after --project "Demo" --summary "after fix" --before-package <before_package> --out DoctorReports
doctor-link diagnose compare <after_package> --json
doctor-link diagnose verify <after_package> --json
doctor-link health DoctorReports --json
```

## Documentation

Key user and product documents:

- `docs/installation.md`
- `docs/quick-start.md`
- `docs/cli-reference.md`
- `docs/diagnostic-package-format.md`
- `docs/ai-coding-workflow.md`
- `docs/local-workbench.md`
- `docs/troubleshooting.md`
- `docs/e2e-validation.md`
- `docs/privacy-model.md`
- `docs/product-overview.md`
- `docs/release-policy.md`

## Validation

P5.9 adds release hardening checks:

- ruff static check;
- coverage report;
- wheel and source distribution build;
- installed wheel CLI smoke;
- end-to-end validation script;
- CLI entrypoint review.

Run local E2E validation:

```bash
python -m pip install -e .
bash scripts/e2e_validate.sh
```

## P1 / P1+: Evidence and Verification Loop

Doctor link supports environment collection, logs, command output, media probing, attachments, test records, Vly proof, before/after comparison, and standard diagnostic package export.

`doctor-link verify` generates:

- `verification-plan.md`
- `verification-result.json`

It does not mark a fix complete just because AI claimed it was fixed. It records missing evidence, tests to rerun, and next commands.

## P2 / P2+: Local Diagnostic Workbench

`doctor-link view` provides a local read-only workbench for browsing summaries, timeline, evidence, assertions, AI task, verification, comparison, redaction, manifest, and AI handoff blocks.

The Web UI is local and read-only by default. It does not add cloud sync, login, or default package write-back.

## P3: AI Coding Collaboration Layer

P3 adds AI Coding collaboration features:

- AI task templates;
- AI tool handoff packages;
- `doctor-link handoff`;
- `doctor-link ai-result`;
- `doctor-link diagnosis-history`;
- `doctor-link assertion-check`;
- `doctor-link risk-review`.

AI output is a collaboration record, not verification evidence; completion still depends on verification results.

## P4: Automated Diagnosis Pipeline

P4 adds a local automated diagnosis pipeline:

- diagnosis strategy validation with `.doctorlink/diagnosis.yml`;
- reproduction management with `.doctorlink/reproduce.yml`;
- executable test matrix jobs with `.doctorlink/test-matrix.yml`;
- before / after diagnostic packages;
- automated comparison and verification;
- GitHub Actions PR diagnostics documentation;
- project health summary.

Pipeline success remains false when verification evidence is missing.

## P5: Productization and Release Readiness

P5 adds productization and release readiness preparation without publishing:

- semantic versioning and release policy;
- `CHANGELOG.md` and release checklist;
- packaging metadata, license, and installation guide;
- user documentation and examples;
- privacy and security review;
- product positioning and contribution docs;
- adapter and extension documentation;
- draft release notes and draft GitHub Release body.

P5 does not publish a release, create a GitHub Release, tag a release, or publish to PyPI.

## Project Configuration

Projects can define diagnostic rules in `.doctorlink/`:

```text
.doctorlink/
├── doctorlink.yml
├── diagnosis.yml
├── reproduce.yml
├── collect.yml
├── package.yml
├── test-matrix.yml
├── assertions.yml
└── verification.yml
```

CLI options override configuration files.

## Current Status

Doctor link has completed:

- P0: Diagnostic Foundation;
- P1: Evidence Collection Primitives;
- P1+: CLI Evidence Pipeline;
- P2: Local Read-only Diagnostic Workbench;
- P2+: Mainline Diagnostic Workbench Enhancements;
- P3: AI Coding Collaboration Layer;
- P4: Automated Diagnosis Pipeline;
- P5: Productization and Release Readiness;
- P5.9: Release Hardening and Usability Validation.

The next phase is P6: Diagnostic Protocol Standardization and Ecosystem Platform. P6 implementation requires separate explicit authorization.

## Boundaries

The following require separate explicit authorization: publishing a version, creating a GitHub Release, publishing to PyPI, changing repository permissions, adding paid cloud services, adding external account systems, changing Doctor link's core positioning, making the local read-only Web UI write back by default, or starting P6 implementation.
