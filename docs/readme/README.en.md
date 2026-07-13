# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

## Current Status

Doctor link has completed the P0-P6 protocol, schema, productization, and ecosystem planning work. P7 converted the planned local runtime capabilities into implemented, tested, and documented CLI behavior. Post-P7 hardening fixes have also been completed.

P5: Productization and Release Readiness is complete. P6 implementation requires separate explicit authorization for hosted, external, release, signing-key, marketplace, or account-system behavior.

P7.10 added the final validation and closure layer, including a P7 runtime validation script and CI coverage for the P7 command surface.

Doctor link remains local-first. Version `0.1.2` passed the repaired local suite and the complete GitHub Actions matrix on 2026-07-13: 273 tests, 85.09% branch coverage, Python 3.10–3.12, Ubuntu/macOS/Windows, security, package build, and isolated installation. See the 100-point certification [Actions run 29221918410](https://github.com/linkyang01/doctor-link/actions/runs/29221918410). The defined repository release-readiness score is 100/100. [GitHub Release `v0.1.2`](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.2) was published from merge commit `862281f`; PyPI publication was not performed. The project does not create a hosted platform, external account system, telemetry service, or marketplace.

Current unreleased hardening additionally guarantees non-zero exits for failed reproductions, required tests, and incomplete verification; automated package evidence write-back; before-to-after assertion inheritance; linked passing after-state evidence before candidate verification; and transaction/atomic-write protection for concurrent package updates. See [Automated Diagnosis Reliability](../automated-diagnosis-reliability.md).

The unreleased full-capability lab also executes every one of the 62 public CLI routes against source and a cleanly installed wheel. It combines 70 real command invocations with eight complex repair, concurrency, privacy, integrity, migration, extension, governance, and archive scenarios. See [Full Capability Validation](../full-capability-validation.md).

## Common Commands

```bash
doctor-link wizard --folder . --tool cursor
doctor-link preflight . --json
doctor-link init
doctor-link scan <library>
doctor-link plan <library>
doctor-link report <library> --out DoctorReports
doctor-link reproduce run <id> . --package-dir <package_dir> --json
doctor-link test run . --package-dir <package_dir> --json
doctor-link verify <package_dir> --write-back
doctor-link handoff list
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
pytest -q --cov=doctor_link --cov-branch --cov-fail-under=85
bandit -r doctor_link -ll
pip-audit
python -m build
python scripts/validate_distribution_contents.py dist
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
python examples/full-capability-lab/run-all.py --dist dist
```

## Documentation

- `../installation.md`
- `../quick-start.md`
- `../cli-reference.md`
- `../automated-diagnosis-reliability.md`
- `../full-capability-validation.md`
- `../platform-integration-roadmap.md`
- `../github-repository-guide.md`
- `../project-status.md`
- `../validation/local-quality-scorecard.md`
- `../p7-final-audit.md`
- `../p7-self-validation.md`
- `../acceptance-review.md`
- `../archive/completed-todos/README.md`

## Runtime Coverage

P7 implements local runtime support for evidence hardening, local workbench hardening, AI handoff runtime, CI automation, distribution readiness, adapter runtime, plugin runtime, integrity and privacy gates, local knowledge indexing, and local archive helpers.

## Boundaries

Doctor link does not currently provide hosted Web platform, cloud synchronization, external account system, telemetry, marketplace, real signing keys or key management, hosted enterprise archive, hosted diagnostic knowledge base, or real RBAC. PyPI publication remains optional.
