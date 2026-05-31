# P7.1 Evidence Hardening

Status: runtime implementation

## Scope

P7.1 hardens P1/P1+ evidence collection with production-oriented metadata, safer log handling, richer environment capture, command output separation, and evidence integrity indexing.

## Implemented runtime changes

### Command capture metadata

Command evidence now records:

- command list;
- return code;
- stdout and stderr;
- started and completed timestamps;
- duration in seconds;
- cwd;
- timeout seconds;
- stdout and stderr byte counts;
- executable name;
- executable availability;
- structured error marker for timeout or missing executable.

When command output is collected through `doctor-link collect`, stdout and stderr are also written to separate files when present.

### Environment capture

Environment evidence now includes:

- Python version details;
- process metadata;
- common tool availability;
- project marker detection;
- top-level project entry summary.

This remains local-only and read-only.

### Log ingestion hardening

Log collection now writes `evidence/logs/log-collection-manifest.json` with per-file metadata:

- source path;
- target path;
- source size;
- collected byte count;
- truncation status;
- skipped status;
- skip reason.

Large text logs are truncated from the end. Binary-looking files are skipped.

### Evidence integrity index

After evidence collection, Doctor link writes:

```text
evidence/evidence-integrity-index.json
```

The index records:

- hash algorithm;
- file count;
- package-relative evidence paths;
- file sizes;
- SHA-256 hashes.

The same summary is also written back into `doctor-report.json` as `evidence_integrity`.

## Safety boundaries

P7.1 does not:

- execute shell commands through a shell;
- upload evidence;
- introduce cloud services;
- introduce external accounts;
- create releases;
- publish packages;
- implement P6 signing or privacy gates.

## Validation

P7.1 includes tests for:

- command runtime metadata;
- environment tool/project marker capture;
- large log truncation;
- binary log skipping;
- redacted command stdout path;
- evidence integrity index generation;
- doctor-report evidence integrity write-back.
