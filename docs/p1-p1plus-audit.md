# P1 / P1+ Completion Audit

## Status

P1 and P1+ are accepted as complete for the current diagnostic foundation scope.

This audit does not change code. It records what exists, how it is invoked, and how CI covers the workflow.

## P1 Scope

P1 covers evidence collection primitives and the first domain adapter.

### Capability Traceability

| Capability | Core file | CLI command | Validation |
| --- | --- | --- | --- |
| Environment evidence | `doctor_link/core/environment_collector.py` | `doctor-link env` | CI smoke |
| Command output evidence | `doctor_link/core/command_runner.py` | used by `doctor-link collect` | Unit tests and CI smoke |
| Log evidence | `doctor_link/core/log_collector.py` | used by `doctor-link collect` | Unit tests and CI smoke |
| Media probe evidence | `doctor_link/core/media_probe.py` | `doctor-link probe` | Unit tests and CI smoke |
| Test result recording | `doctor_link/core/test_recorder.py` | `doctor-link record` | Unit tests and CI smoke |
| Vly proof matrix | `doctor_link/core/vly_adapter.py` | `doctor-link vly-proof` | Unit tests and CI smoke |
| Before/after report comparison | `doctor_link/core/report_comparator.py` | `doctor-link compare` | Unit tests and CI smoke |

## P1+ Scope

P1+ turns the evidence primitives into a CLI evidence pipeline.

### Capability Traceability

| Capability | Core file | CLI command | Validation |
| --- | --- | --- | --- |
| One-command package collection | `doctor_link/core/collector.py` | `doctor-link collect` | Unit tests and CI smoke |
| Verification planning | `doctor_link/core/verification_runner.py` | `doctor-link verify` | Unit tests and CI smoke |
| Package export | `doctor_link/core/package_exporter.py` | `doctor-link doctor-package` | Unit tests and CI smoke |
| Sensitive text redaction | `doctor_link/core/redactor.py` | used by `doctor-link collect` | Unit tests and CI smoke |
| Project configuration loading | `doctor_link/core/config_loader.py` | used by collect / verify / doctor-package | Unit tests and CI smoke |

## CLI Smoke Coverage

The CI workflow runs the following commands across Python 3.10, 3.11, and 3.12:

```bash
doctor-link env
doctor-link probe
doctor-link collect
doctor-link vly-proof
doctor-link record
doctor-link compare
doctor-link verify
doctor-link doctor-package
doctor-link view
```

This validates that the main diagnostic package pipeline can run end-to-end in CI.

## Completion Decision

P1 is complete for evidence primitives.

P1+ is complete for the CLI evidence pipeline.

## Known Follow-up Work

The next hardening step is not a P1/P1+ blocker, but it will improve the verification loop:

- allow test records to reference user assertions directly;
- allow verification to summarize assertion test coverage;
- document the assertion-to-test-to-verification loop.

These follow-up items are tracked separately after this audit.
