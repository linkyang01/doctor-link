# Doctor link Acceptance and Publication Readiness Review

Status: acceptance review
Date: 2026-06-03

## Review scope

This review covers the repository state after:

- P0-P5.10 completion;
- P6.1-P6.11 specification and schema closure;
- P7.0-P7.10 local runtime implementation and final validation closure;
- post-P7 hardening fixes;
- repository cleanup and completed TODO archival.

## Repository organization review

### Completed TODO trackers

The completed root TODO trackers have been moved to:

```text
docs/archive/completed-todos/
```

Root-level TODO files now act as short archive pointers only:

- `TODO-P6.md` points to `docs/archive/completed-todos/TODO-P6.md`;
- `TODO-P7.md` points to `docs/archive/completed-todos/TODO-P7.md`.

Active project status is maintained in:

```text
docs/project-status.md
```

### Current active documentation

The primary active documentation set is:

- `README.md`;
- `README.en.md`;
- `README.zh-CN.md`;
- `docs/cli-reference.md`;
- `docs/project-status.md`;
- `docs/p5.10-local-validation.md`;
- `docs/p7-final-audit.md`;
- `docs/p7-self-validation.md`;
- `docs/acceptance-review.md`.

Historical phase documents remain available under `docs/` and completed TODO trackers remain available under `docs/archive/completed-todos/`.

## Implementation review

### Completed runtime capabilities

The repository implements local-first CLI/runtime behavior for:

- evidence collection and hardening;
- diagnostic package creation and verification;
- user assertions and AI repair result tracking;
- diagnosis history and assertion checking;
- risk review;
- local static workbench generation;
- controlled workbench write-back;
- strategy validation;
- reproduction catalog listing and running;
- test matrix listing and running;
- before/after diagnosis pipeline;
- schema validation;
- conformance validation;
- CI report generation;
- distribution readiness checks;
- Adapter runtime;
- Plugin runtime;
- integrity manifest generation;
- integrity verification with optional strict untracked-file detection;
- privacy scanning;
- redaction gate;
- export safety gate;
- local diagnostic knowledge indexing;
- local archive creation, inspection, policy checking, and export.

### Post-P7 hardening status

Post-P7 hardening fixed the main audit findings:

- CLI extension registration is explicit through `doctor_link.entrypoint:main`.
- `archive create` blocks archive output directories that are equal to or inside the source directory.
- `integrity verify --strict` detects files under the validation root that are missing from the manifest.
- Adapter and Plugin `run` commands default to dry-run and require `--allow-run` for actual local command execution.
- Audit records include dry-run and explicit user approval state.

## Design consistency review

### Local-first boundary

The local-first boundary is preserved.

Doctor link does not create or require:

- hosted services;
- cloud synchronization;
- external account systems;
- telemetry;
- marketplace behavior;
- real signing keys or key management;
- hosted enterprise archives;
- hosted diagnostic knowledge base services;
- real RBAC or enterprise identity integration.

### Release boundary

No release action has been performed:

- no GitHub Release;
- no release tag;
- no PyPI publication;
- no repository permission change;
- no paid cloud service;
- no external account system.

### Adapter and Plugin execution boundary

Adapter and Plugin local command execution now requires explicit approval:

```bash
doctor-link adapter run demo-adapter verification . --allow-run --json
doctor-link plugin run demo-plugin verification . --allow-run --json
```

Without `--allow-run`, the commands create dry-run records and do not execute configured local commands.

This makes the implementation better aligned with the intended safety model.

### Archive safety boundary

Archive output must not be placed inside the source directory. This prevents recursive archive pollution and self-copying.

### Integrity verification boundary

Strict integrity verification is available through:

```bash
doctor-link integrity verify . DoctorReports/integrity-manifest.json --strict --json
```

Strict mode blocks untracked files that are present under the validation root but missing from the manifest.

## Validation review

The CI workflow covers:

- Python 3.10;
- Python 3.11;
- Python 3.12;
- ruff static checks;
- pytest with coverage;
- CLI smoke tests;
- existing E2E validation;
- package build;
- P7 runtime validation;
- installed wheel smoke test.

The package validation job also installs the built wheel and runs validation from the installed CLI.

The P7 runtime validation script exercises the major P7 command surface, including Adapter and Plugin execution with explicit `--allow-run`.

## Acceptance decision

### Functional acceptance

Decision: ready, subject to CI passing on this cleanup branch.

Rationale:

- major planned local runtime capabilities are implemented;
- P6 and P7 completion trackers are closed and archived;
- design boundaries are documented;
- safety hardening findings have been addressed;
- CI validates the main command surface across supported Python versions.

### Documentation acceptance

Decision: ready, subject to CI passing on this cleanup branch.

Rationale:

- README files describe current status and local-first boundaries;
- CLI reference matches current Adapter/Plugin dry-run and `--allow-run` behavior;
- P7 Adapter and Plugin documents match current runtime behavior;
- project status explains completion and remaining optional target-environment validation;
- completed TODO trackers are archived instead of left as active root-level task lists.

### Release acceptance

Decision: not yet authorized.

The repository is technically close to release-ready after CI passes, but release publication still requires explicit authorization.

Before a formal external release, GitHub Release, release tag, PyPI publishing, or customer delivery, the target environment should run:

```bash
ruff check doctor_link tests scripts
pytest -q --cov=doctor_link
python -m build
bash scripts/validate_doctor_link.sh
bash scripts/e2e_validate.sh "$(pwd)"
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

Then the result should be recorded in:

```text
docs/p5.10-local-validation.md
```

## Remaining risks

The remaining risks are intentional boundaries rather than blocking implementation defects:

- real signing and key management are not implemented;
- hosted services are not implemented;
- marketplace behavior is not implemented;
- telemetry is not implemented;
- target-environment validation has not been recorded;
- formal release authorization has not been granted.

## Final conclusion

Doctor link is ready for repository-side acceptance after this cleanup branch passes CI and is merged.

Doctor link is not yet authorized for public release, tag creation, GitHub Release creation, PyPI publication, or customer delivery until target-environment validation is run and explicit release authorization is granted.
