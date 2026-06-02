# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

## Current Status

Doctor link has completed the P0-P6 protocol, schema, productization, and ecosystem planning work, and P7 has converted the planned local runtime capabilities into implemented, tested, and documented CLI behavior.

P5: Productization and Release Readiness is complete. P6 implementation requires separate explicit authorization for hosted, external, release, signing-key, marketplace, or account-system behavior.

P7.10 adds the final validation and closure layer, including a P7 runtime validation script and CI coverage for the P7 command surface.

Doctor link remains local-first. It does not create a hosted platform, external account system, telemetry service, marketplace, GitHub Release, release tag, or PyPI publication.

## Core Positioning

Doctor link is a diagnostic context layer for AI coding workflows.

It follows these principles:

- evidence first;
- reproduction first;
- human-confirmed issues first;
- AI must not dismiss a human-confirmed issue without evidence;
- fixes must be verified;
- local-first and read-only-first;
- protocol and CLI before hosted platform behavior.

## Standard Diagnostic Package

Doctor link generates and maintains standard diagnostic packages under `DoctorReports/`, including evidence, timeline, user assertions, verification results, AI collaboration records, workflow metadata, schema validation outputs, pipeline summaries, CI reports, distribution readiness reports, knowledge indexes, and archive records.

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
doctor-link schema validate <package_dir> --write --json
doctor-link conformance run <fixtures_root> --out DoctorReports/conformance --json
doctor-link health DoctorReports --json

doctor-link ci report DoctorReports --out DoctorReports/ci --json
doctor-link distribution check . --dist dist --out DoctorReports/distribution --json

doctor-link adapter list . --json
doctor-link adapter validate .doctorlink/adapters/demo-adapter/adapter.yml --json
doctor-link adapter run demo-adapter verification . --json

doctor-link plugin list . --json
doctor-link plugin validate .doctorlink/plugins/demo-plugin/plugin.yml --json
doctor-link plugin run demo-plugin verification . --json

doctor-link integrity manifest . --out DoctorReports/integrity-manifest.json --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --json
doctor-link privacy scan . --out DoctorReports/privacy-scan.json --json
doctor-link privacy redaction-gate . --out DoctorReports/redaction-gate.json --json
doctor-link privacy export-gate . --manifest DoctorReports/integrity-manifest.json --out DoctorReports/export-gate.json --json

doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
doctor-link knowledge query DoctorReports/knowledge-index.json "missing evidence" --json
doctor-link knowledge export DoctorReports/knowledge-index.json DoctorReports/knowledge-export.json --json
doctor-link archive create DoctorReports DoctorReports/archive --metadata owner=qa --json
doctor-link archive inspect DoctorReports/archive --json
doctor-link archive policy-check DoctorReports/archive --max-files 1000 --json
doctor-link archive export DoctorReports/archive DoctorReports/archive.zip --json
```

## Validation

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link
python -m build
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
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
- `docs/privacy-model.md`
- `docs/product-overview.md`
- `docs/release-policy.md`
- `docs/usability-validation.md`
- `docs/e2e-validation.md`
- `docs/p5.9-final-audit.md`
- `docs/p5.10-local-validation.md`
- `docs/p6-schema-v1.md`
- `docs/p6-conformance.md`
- `docs/p6-adapter-sdk.md`
- `docs/p6-plugin-sdk.md`
- `docs/p6-ai-coding-integrations.md`
- `docs/p6-signing-integrity.md`
- `docs/p6-privacy-security.md`
- `docs/p6-enterprise-governance.md`
- `docs/p6-diagnostic-knowledge-base.md`
- `docs/p6-public-ecosystem-assets.md`
- `docs/p6-quality-closure.md`
- `docs/p7-final-audit.md`
- `docs/p7-self-validation.md`

## Runtime Coverage

P7 implements local runtime support for:

- evidence hardening;
- local workbench hardening;
- AI handoff runtime;
- CI and operational automation;
- distribution readiness checks;
- adapter runtime;
- plugin runtime;
- integrity and privacy gates;
- local knowledge indexing;
- local archive helpers.

## Boundaries

Doctor link does not currently provide:

- hosted Web platform;
- cloud synchronization;
- external account system;
- telemetry;
- marketplace;
- real signing keys or key management;
- hosted enterprise archive;
- hosted diagnostic knowledge base;
- real RBAC or enterprise identity integration;
- GitHub Release, release tag, or PyPI publication.
