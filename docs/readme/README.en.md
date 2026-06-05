# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

## Current Status

Doctor link has completed the P0-P6 protocol, schema, productization, and ecosystem planning work. P7 converted the planned local runtime capabilities into implemented, tested, and documented CLI behavior. Post-P7 hardening fixes have also been completed.

P5: Productization and Release Readiness is complete. P6 implementation requires separate explicit authorization for hosted, external, release, signing-key, marketplace, or account-system behavior.

P7.10 added the final validation and closure layer, including a P7 runtime validation script and CI coverage for the P7 command surface.

Doctor link remains local-first. It does not create a hosted platform, external account system, telemetry service, marketplace, GitHub Release, release tag, or PyPI publication.

## Common Commands

```bash
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link verify <package_dir> --write-back
doctor-link handoff <package_dir> --tool codex --out DoctorReports/handoff
doctor-link ci report DoctorReports --out DoctorReports/ci --json
doctor-link distribution check . --dist dist --out DoctorReports/distribution --json
doctor-link adapter run demo-adapter verification . --allow-run --json
doctor-link plugin run demo-plugin verification . --allow-run --json
doctor-link integrity verify . DoctorReports/integrity-manifest.json --strict --json
doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
doctor-link archive create DoctorReports-source DoctorReports/archive --metadata owner=qa --json
```

Adapter and Plugin `run` commands are dry-run by default. They validate manifests and write audit/run records without executing configured local commands. Use `--allow-run` only after reviewing the manifest and intentionally approving local command execution.

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

- `../installation.md`
- `../quick-start.md`
- `../cli-reference.md`
- `../project-status.md`
- `../p7-final-audit.md`
- `../p7-self-validation.md`
- `../acceptance-review.md`
- `../archive/completed-todos/README.md`

## Runtime Coverage

P7 implements local runtime support for evidence hardening, local workbench hardening, AI handoff runtime, CI automation, distribution readiness, adapter runtime, plugin runtime, integrity and privacy gates, local knowledge indexing, and local archive helpers.

## Boundaries

Doctor link does not currently provide hosted Web platform, cloud synchronization, external account system, telemetry, marketplace, real signing keys or key management, hosted enterprise archive, hosted diagnostic knowledge base, real RBAC, GitHub Release, release tag, or PyPI publication.
