# P7.9 Local Knowledge Base and Enterprise Archive Runtime

Status: runtime implementation

## Scope

P7.9 implements local-first diagnostic knowledge indexing and enterprise archive runtime helpers.

The implementation stays local. It does not introduce a hosted knowledge base, external account system, remote archive service, telemetry, or centralized enterprise platform.

## Implemented runtime changes

### Local diagnostic knowledge index

Command:

```bash
doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json --json
```

The knowledge index records:

- source root;
- generated timestamp;
- normalized diagnostic records;
- recurring failure signatures;
- repair outcome aggregation;
- project health trend aggregation.

Supported input files include:

```text
**/doctor-report.json
**/diagnosis-pipeline-summary.json
**/verification-result.json
```

### Recurring failure signature extraction

P7.9 extracts recurring local signatures from diagnostic payload text, including signals such as:

- `error`;
- `failed`;
- `missing`;
- `regression`;
- `blocked`;
- `unresolved`.

Signatures appearing in multiple records are aggregated with occurrence count and source paths.

### Repair outcome aggregation

The knowledge index summarizes local outcomes into:

- passed;
- blocked;
- unknown;
- total.

### Project health trend aggregation

Each normalized record receives a simple local score:

- `100` for passed / verified statuses;
- `50` for unknown;
- `0` for blocked or failed statuses.

The index records point-level scores and an average score.

### Knowledge query

Command:

```bash
doctor-link knowledge query DoctorReports/knowledge-index.json "missing evidence" --json
```

The query command performs local text matching over normalized records and returns matching records up to a configurable limit.

### Knowledge export

Command:

```bash
doctor-link knowledge export DoctorReports/knowledge-index.json DoctorReports/knowledge-export.json --json
```

The export command writes a copy of the local index for sharing or archival review.

## Enterprise archive runtime helpers

### Archive create

Command:

```bash
doctor-link archive create DoctorReports DoctorReports/archive --metadata owner=team --json
```

The archive command copies files into a local archive folder and writes:

```text
archive-record.json
archive-audit.jsonl
files/
```

### Archive inspect

Command:

```bash
doctor-link archive inspect DoctorReports/archive --json
```

Inspection reads the local archive record and appends an audit event.

### Archive policy check

Command:

```bash
doctor-link archive policy-check DoctorReports/archive --max-files 1000 --max-size-bytes 104857600 --json
```

The policy check supports:

- maximum file count;
- maximum total size.

Blocking policy findings return a non-zero CLI exit.

### Archive export

Command:

```bash
doctor-link archive export DoctorReports/archive DoctorReports/archive.zip --json
```

The export command creates a local zip file and appends an audit event.

## CLI examples

Build and query knowledge:

```bash
doctor-link knowledge build DoctorReports --out DoctorReports/knowledge-index.json
doctor-link knowledge query DoctorReports/knowledge-index.json "regression"
```

Create and inspect archive:

```bash
doctor-link archive create DoctorReports DoctorReports/archive --metadata owner=qa
doctor-link archive inspect DoctorReports/archive
```

Policy check and export:

```bash
doctor-link archive policy-check DoctorReports/archive --max-files 1000
doctor-link archive export DoctorReports/archive DoctorReports/archive.zip
```

## Safety boundaries

P7.9 does not:

- introduce hosted storage;
- upload archives;
- transmit telemetry;
- provide real enterprise RBAC;
- provide real retention enforcement beyond local policy checks;
- replace customer governance review.

It provides local files and local evidence that can be reviewed or integrated into a larger governance process.

## Validation

P7.9 includes tests for:

- knowledge index generation;
- recurring failure signature extraction;
- repair outcome aggregation;
- health trend aggregation;
- knowledge query;
- knowledge export;
- archive creation;
- archive inspection;
- archive retention policy check;
- audit trail append behavior;
- local archive export;
- `doctor-link knowledge build`;
- `doctor-link knowledge query`;
- `doctor-link knowledge export`;
- `doctor-link archive create`;
- `doctor-link archive inspect`;
- `doctor-link archive policy-check`.
