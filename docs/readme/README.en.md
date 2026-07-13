# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

The current source also provides `doctor-link solve`. For a Python project in a clean Git repository, it first reproduces the failure and writes a repair preview. Only after `--allow-repair` does Doctor link create an isolated branch, invoke Codex for up to three rounds, and independently rerun every required command. A Codex claim is not success; only passing checks produce `verified`.

## Current Status

Doctor link has completed the P0-P6 protocol, schema, productization, and ecosystem planning work. P7 converted the planned local runtime capabilities into implemented, tested, and documented CLI behavior. Post-P7 hardening fixes have also been completed.

P5: Productization and Release Readiness is complete. P6 implementation requires separate explicit authorization for hosted, external, release, signing-key, marketplace, or account-system behavior.

P7.10 added the final validation and closure layer, including a P7 runtime validation script and CI coverage for the P7 command surface.

Doctor link remains local-first. Version `0.1.3` passed the repaired local suite and the complete GitHub Actions matrix on 2026-07-13: 298 tests, 85.25% branch coverage, Python 3.10–3.12, Ubuntu/macOS/Windows, security, package build, and isolated installation. [Final PR CI 29245883700](https://github.com/linkyang01/doctor-link/actions/runs/29245883700) passed all eight jobs. The defined repository release-readiness score remains 100/100. [GitHub Release `v0.1.3`](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.3) was published from merge commit `fa779da` by [Release workflow 29246045227](https://github.com/linkyang01/doctor-link/actions/runs/29246045227); PyPI publication was disabled and not performed. The project does not create a hosted platform, external account system, telemetry service, or marketplace.

Version `0.1.3` guarantees non-zero exits for failed reproductions, required tests, and incomplete verification; automated package evidence write-back; before-to-after assertion inheritance; linked passing after-state evidence before candidate verification; and transaction/atomic-write protection for concurrent package updates. See [Automated Diagnosis Reliability](../automated-diagnosis-reliability.md).

The current-source full-capability lab executes all 63 public CLI routes through 71 real command invocations and nine automatic-solve, repair, concurrency, privacy, integrity, migration, extension, governance, and archive scenario invariants. Published `v0.1.3` retains its historical certification of 62 routes, 70 invocations, and eight scenarios. See [Full Capability Validation](../full-capability-validation.md).

## Common Commands

```bash
doctor-link wizard --folder . --tool cursor
doctor-link preflight . --json
doctor-link solve /path/to/python-project --problem "Checkout duplicates charges" --test-command "python -m pytest tests/test_checkout.py -q"
doctor-link solve /path/to/python-project --problem "Checkout duplicates charges" --test-command "python -m pytest tests/test_checkout.py -q" --allow-repair
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
- `../automatic-solve.md`
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

P7 implements local runtime support for evidence hardening, local workbench hardening, AI handoff runtime, CI automation, distribution readiness, adapter runtime, plugin runtime, integrity and privacy gates, local knowledge indexing, and local archive helpers. The current source adds the first Python automatic-solve vertical slice on top of that foundation.

## Boundaries

Doctor link does not currently provide hosted Web platform, cloud synchronization, external account system, telemetry, marketplace, real signing keys or key management, hosted enterprise archive, hosted diagnostic knowledge base, or real RBAC. Automatic repair currently supports Python projects only, requires explicit approval, and never auto-commits, pushes, or publishes. `--allow-repair` uses existing Codex authentication to call the service, so users should review the preview and remove sensitive data first. PyPI publication remains optional.
