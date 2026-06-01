# P7.6 Adapter SDK Runtime

Status: runtime implementation

## Scope

P7.6 turns the Adapter SDK planning specification into a local-first runtime layer.

The implementation supports discovering adapter manifests, validating adapter metadata and capabilities, and running configured local adapter commands under an explicit local execution boundary.

## Implemented runtime changes

### Adapter manifest

Adapters are declared with `adapter.yml` or `adapter.yaml` files under one of the default locations:

```text
.doctorlink/adapters/
adapters/
DoctorAdapters/
```

A minimal manifest:

```yaml
schema: doctor-link-adapter-v1
id: demo-adapter
name: Demo Adapter
version: 0.1.0
capabilities:
  - evidence_collector
  - verification
  - handoff
commands:
  evidence_collector:
    - python
    - -c
    - print('evidence-ok')
```

### Supported capabilities

P7.6 supports three runtime capability names:

- `evidence_collector`;
- `verification`;
- `handoff`.

### Adapter discovery

Command:

```bash
doctor-link adapter list .
```

JSON output:

```bash
doctor-link adapter list . --json
```

The command scans the default adapter roots or a supplied override:

```bash
doctor-link adapter list . --adapters-dir .doctorlink/adapters --json
```

### Adapter validation

Command:

```bash
doctor-link adapter validate .doctorlink/adapters/demo-adapter/adapter.yml
```

Validation checks:

- supported schema;
- adapter id;
- adapter name;
- adapter version;
- supported capabilities;
- at least one capability;
- command presence for declared capabilities.

Blocking findings make the adapter invalid. Missing commands for declared capabilities are warnings because some adapters may be metadata-only during early development.

### Local adapter execution

Command:

```bash
doctor-link adapter run demo-adapter verification .
```

The run command:

- discovers the adapter;
- validates the manifest;
- verifies the requested capability;
- runs the configured local command from the project root;
- captures stdout, stderr, return code, timestamps, and command arguments;
- writes a local run record;
- appends an audit record.

Generated files are written to:

```text
DoctorReports/adapters/
```

Example outputs:

```text
demo-adapter-verification-run.json
adapter-audit.jsonl
```

### Local execution boundary

Adapter execution is intentionally local. Doctor link does not provide network access, credentials, account systems, hosted execution, remote marketplace behavior, or remote plugin installation.

The audit record includes:

- adapter id;
- adapter name;
- adapter version;
- capability;
- command;
- status;
- timestamps;
- return code;
- local execution boundary flag.

## CLI examples

List adapters:

```bash
doctor-link adapter list . --json
```

Validate a manifest:

```bash
doctor-link adapter validate .doctorlink/adapters/demo-adapter/adapter.yml --json
```

Run an adapter capability:

```bash
doctor-link adapter run demo-adapter evidence_collector . --json
```

Run with explicit output directory:

```bash
doctor-link adapter run demo-adapter verification . --out DoctorReports/adapters --json
```

## Safety boundaries

P7.6 does not:

- install third-party code;
- download remote adapters;
- grant extra permissions;
- manage secrets;
- provide sandbox isolation beyond explicit local process execution;
- claim network isolation for child processes;
- implement a hosted adapter marketplace.

Adapter commands are local commands configured by the user. Users should review adapter manifests before running them.

## Validation

P7.6 includes tests for:

- adapter manifest loading;
- schema validation;
- capability validation;
- adapter discovery;
- local adapter execution;
- adapter audit records;
- `doctor-link adapter list`;
- `doctor-link adapter validate`;
- `doctor-link adapter run`.
