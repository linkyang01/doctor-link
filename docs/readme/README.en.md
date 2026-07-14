# Doctor link

**Language / 语言:** English | [中文](README.zh-CN.md)

Doctor link is a human-AI shared diagnostic layer for software projects. It helps non-programmer users, developers, and AI coding tools work on the same issue using the same evidence and verification standard.

Doctor link does not replace Codex, Aider, OpenHands, Continue, Cursor, or other AI coding tools. It prepares high-quality diagnostic context so AI tools can debug with less guessing, less unrelated editing, and stronger verification.

The current source also provides `doctor-link solve`. For a Python or Node.js JavaScript/TypeScript project in a clean Git repository, it first reproduces the failure and writes a repair preview. Only after `--allow-repair` does Doctor link create an isolated branch, invoke Codex for up to three rounds, and independently rerun every required command. Tests, package manifests and lockfiles, test configuration, configured catalogs, and directly referenced verification scripts are hash-protected: a Codex claim or a weakened test is not success. Only passing checks against unchanged protected inputs produce `verified`.

## Current Status

Doctor link has completed the P0-P6 protocol, schema, productization, and ecosystem planning work. P7 converted the planned local runtime capabilities into implemented, tested, and documented CLI behavior. Post-P7 hardening fixes have also been completed.

P5: Productization and Release Readiness is complete. P6 implementation requires separate explicit authorization for hosted, external, release, signing-key, marketplace, or account-system behavior.

P7.10 added the final validation and closure layer, including a P7 runtime validation script and CI coverage for the P7 command surface.

Version [`v0.5.0`](https://github.com/linkyang01/doctor-link/releases/tag/v0.5.0) is the latest published release. It adds natural-language reproduction, the guided `doctor-link assist` entrypoint, and a retained 24-project Python/Node.js corpus, so users no longer need to know a test command.

Doctor link remains local-first. Version `0.5.0` passed 363 tests at 85.06% branch-aware coverage, all 66 installed CLI routes through 75 real invocations and twelve complex scenarios, Python 3.10–3.14, Ubuntu/macOS/Windows, security checks, package builds, and isolated installation. [Final PR CI 29305470580](https://github.com/linkyang01/doctor-link/actions/runs/29305470580) passed all ten jobs. PR [#150](https://github.com/linkyang01/doctor-link/pull/150) merged as `ac5c2f5`; [release workflow 29305612221](https://github.com/linkyang01/doctor-link/actions/runs/29305612221) published the immutable GitHub Release with PyPI disabled.

The current verified-repair path supports clean Git repositories containing Python or Node.js JavaScript/TypeScript projects. Node.js repair also requires the project's runtime and package manager. Automatic edits require an installed, authenticated Codex CLI and explicit `--allow-repair` approval. Other language ecosystems and PyPI installation are not yet supported. See [Automatic Solve with Codex](../automatic-solve.md), [Automated Diagnosis Reliability](../automated-diagnosis-reliability.md), and [Full Capability Validation](../full-capability-validation.md).

## Common Commands

```bash
doctor-link wizard --folder . --tool cursor
doctor-link assist /path/to/project --problem "Checkout duplicates charges"
doctor-link reproduce suggest /path/to/project --problem "Checkout duplicates charges" --json
doctor-link preflight . --json
doctor-link solve /path/to/python-project --problem "Checkout duplicates charges" --test-command "python -m pytest tests/test_checkout.py -q"
doctor-link solve /path/to/python-project --problem "Checkout duplicates charges" --test-command "python -m pytest tests/test_checkout.py -q" --allow-repair
doctor-link solve /path/to/node-project --problem "Concurrent updates lose data" --test-command "npm test" --allow-repair
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

P7 implements local runtime support for evidence hardening, local workbench hardening, AI handoff runtime, CI automation, distribution readiness, adapter runtime, plugin runtime, integrity and privacy gates, local knowledge indexing, and local archive helpers. The current source extends the automatic-solve vertical slice across Python and Node.js JavaScript/TypeScript projects.

## Boundaries

Doctor link does not currently provide hosted Web platform, cloud synchronization, external account system, telemetry, marketplace, real signing keys or key management, hosted enterprise archive, hosted diagnostic knowledge base, or real RBAC. Automatic repair currently supports Python and Node.js JavaScript/TypeScript projects, requires explicit approval, protects the original verification inputs, and never auto-commits, pushes, or publishes. Other language ecosystems remain unsupported until they receive an equally testable adapter. The exceptional `--allow-verification-changes` path returns `review_required`, not `verified`. `--allow-repair` uses existing Codex authentication to call the service, so users should review the preview and remove sensitive data first. PyPI publication remains optional.
