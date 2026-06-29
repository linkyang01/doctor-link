# GitHub Release Draft: Doctor link v0.1.0-rc.1

Status: draft only. Do not publish, tag, or upload packages without explicit authorization.

## Release title

```text
Doctor link v0.1.0-rc.1
```

## Tag

```text
v0.1.0-rc.1
```

Do not create this tag until explicitly authorized.

## Release type

```text
Pre-release
```

## Release body

Doctor link v0.1.0-rc.1 is a cloud-CI-certified release candidate for a local-first diagnostic context layer for AI coding workflows.

### Status

```text
Cloud CI Certified
Release Candidate Ready
Local Mac Validation Recorded (2026-06-29)
```

This pre-release candidate is suitable for internal review, local source installation tests, CLI workflow validation, and AI coding diagnostic workflow evaluation. Local Mac validation passed on 2026-06-29.

It is not yet certified for production deployment, customer environment acceptance, PyPI publication, or stable public release on environments other than the recorded Mac setup.

### Validation evidence

Latest confirmed cloud validation:

- Certification package: `docs/validation/`
- Release candidate notes: `docs/release-notes/v0.1.0-rc.1.md`
- PR: `#110 Repository root cleanup`
- Merge commit: `09830b934d92c41509daa75b929d82081c6c827d`
- CI run: `#312`
- CI result: `success`

Validation coverage:

- Python 3.10
- Python 3.11
- Python 3.12
- Ruff
- Pytest
- CLI smoke tests
- E2E validation
- P7 runtime validation
- Wheel build
- Installed wheel smoke test
- Package validation job

### Included capabilities

- Diagnostic package generation
- Evidence collection
- Environment capture
- User assertions
- Verification result recording
- Local workbench generation
- AI handoff generation
- AI result ingestion
- Diagnosis history
- Assertion compliance checks
- Risk review
- Strategy validation
- Reproduction management
- Test matrix execution
- Before / after package workflow
- Automated comparison and verification
- Project health summaries
- CI report generation
- Distribution readiness checks
- Adapter runtime with dry-run default and explicit `--allow-run`
- Plugin runtime with dry-run default and explicit `--allow-run`
- Integrity manifest generation
- Integrity verification with strict untracked-file detection
- Privacy scan, redaction gate, and export gate
- Local diagnostic knowledge index
- Local archive helpers
- Archive output guard preventing archives inside the source directory

### Repository hardening included

- Root directory cleanup
- Completed TODO trackers archived under `docs/archive/completed-todos/`
- English and Chinese README files moved under `docs/readme/`
- Root `README.md` reduced to a lightweight entrypoint
- Cloud validation certification package added under `docs/validation/`
- Release candidate notes added under `docs/release-notes/`

### Boundaries

This release candidate does not include:

- hosted Web platform
- cloud synchronization
- external account system
- telemetry
- marketplace
- real signing key management
- hosted enterprise archive
- hosted diagnostic knowledge base
- production deployment certification
- customer environment acceptance
- GitHub Release publication unless this draft is explicitly approved and published
- release tag creation unless explicitly approved
- PyPI publication unless explicitly approved

### Recommended installation for evaluation

```bash
git clone https://github.com/linkyang01/doctor-link.git
cd doctor-link
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
doctor-link --help
```

### Recommended validation for evaluators

```bash
python -m pip install pytest pytest-cov build ruff
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link --cov-report=term-missing --cov-report=xml
python -m build
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

### Before formal release

Before formal external release, complete:

- [ ] Local or target-environment validation record.
- [ ] Explicit authorization to create `v0.1.0-rc.1` tag.
- [ ] Explicit authorization to publish this GitHub pre-release.
- [ ] Explicit authorization before any PyPI publication.

## Publishing checklist

Before pressing **Publish release**, confirm:

- [ ] The tag `v0.1.0-rc.1` is intentionally authorized.
- [ ] The release is marked as **Pre-release**.
- [ ] The release body above has been reviewed.
- [ ] No PyPI upload will be performed as part of this step.
- [ ] Local / target validation remains clearly marked as pending unless completed separately.
