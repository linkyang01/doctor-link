# P7 Self-validation Scenario

Status: runtime validation scenario

## Purpose

This document describes the P7 self-validation scenario introduced in P7.10.

The scenario proves that Doctor link can exercise its P7 runtime capabilities through local CLI commands and CI without relying on hosted services, external accounts, remote publishing, telemetry, or paid cloud dependencies.

## Validation entrypoint

```bash
bash scripts/p7_runtime_validate.sh "$(pwd)"
```

The script creates an isolated local working directory:

```text
.doctorlink-p7-runtime/
```

It creates temporary sample inputs, temporary adapter and plugin manifests, local evidence, local reports, local archives, and local validation outputs.

## Runtime capabilities exercised

The script exercises the following command groups:

```bash
doctor-link strategy validate
doctor-link reproduce list
doctor-link reproduce run
doctor-link test list
doctor-link test run
doctor-link schema validate
doctor-link collect
doctor-link assert
doctor-link record
doctor-link ai-result
doctor-link diagnosis-history
doctor-link assertion-check
doctor-link risk-review
doctor-link verify
doctor-link handoff
doctor-link view
doctor-link workbench-note
doctor-link ci report
doctor-link distribution check
doctor-link adapter list
doctor-link adapter validate
doctor-link adapter run
doctor-link plugin list
doctor-link plugin validate
doctor-link plugin run
doctor-link integrity manifest
doctor-link integrity verify
doctor-link privacy scan
doctor-link privacy redaction-gate
doctor-link privacy export-gate
doctor-link knowledge build
doctor-link knowledge query
doctor-link knowledge export
doctor-link archive create
doctor-link archive inspect
doctor-link archive policy-check
doctor-link archive export
```

## Expected outputs

The script verifies representative output files, including:

```text
strategy-validation.json
reproduction-run.json
test-run.json
ci/ci-report.json
distribution/distribution-report.json
adapters/p7-adapter-verification-run.json
plugins/p7-plugin-verification-run.json
integrity-verify.json
privacy-scan.json
redaction-gate.json
export-gate.json
knowledge-index.json
knowledge-export.json
archive/archive-record.json
archive-audit.jsonl
archive.zip
handoff/handoff-manifest.json
p7-runtime-validation-summary.md
```

## CI integration

P7.10 adds the P7 runtime validation script to:

- the main CI matrix after E2E and package build;
- the package validation job after installed-wheel validation;
- the manual self-validation workflow.

## Interpretation

A successful P7 self-validation run means local P7 runtime capabilities are callable, generate expected files, and can run as part of automated repository validation.

It does not mean Doctor link has a hosted enterprise platform, real signing infrastructure, hosted archive, hosted knowledge base, marketplace, or publishing automation.
