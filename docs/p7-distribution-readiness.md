# P7.5 Distribution Readiness Checks

Status: runtime implementation

## Scope

P7.5 adds a local-first distribution readiness check for built package artifacts.

It validates local artifact files and writes reviewable readiness evidence. The command is intentionally limited to local file inspection and report generation.

## Implemented runtime changes

### Distribution readiness command

```bash
doctor-link distribution check <project_root> --dist dist --out DoctorReports/distribution
```

Generated files:

```text
distribution-report.json
distribution-report.md
distribution-manifest.json
checksums.sha256
target-environment.json
```

### Local dry-run semantics

The command checks whether the local project and local `dist/` artifacts are ready for downstream distribution review.

It does not create remote records, push tags, upload files, require credentials, call external services, or change version numbers.

### Artifact checksum generation

`checksums.sha256` records SHA-256 hashes for supported artifacts:

- `.whl`;
- `.tar.gz`;
- `.zip`.

### Wheel metadata verification

Wheel files are inspected as zip archives. The check verifies:

- `.dist-info/METADATA` exists;
- `.dist-info/WHEEL` exists;
- `.dist-info/RECORD` exists;
- metadata fields can be parsed.

### Source archive metadata verification

Source archives are inspected as gzipped tar archives. The check verifies:

- `PKG-INFO` exists;
- `pyproject.toml` is present when available;
- package metadata can be parsed.

### Distribution manifest

`distribution-manifest.json` records:

- project root;
- dist directory;
- output directory;
- status;
- artifact records;
- checklist results;
- target environment;
- safety boundary stating that remote publication is blocked by design.

### Blocking checklist automation

The checklist covers:

- `pyproject.toml` presence;
- required project metadata fields;
- distribution directory presence;
- wheel artifact presence;
- source archive artifact presence;
- checksum generation ability;
- artifact metadata readability;
- target Python detection.

The report status is:

- `passed` when no blocking checks fail;
- `blocked` when one or more blocking checks fail.

### Target environment helper

`target-environment.json` records:

- Python version;
- Python executable;
- platform;
- project name;
- project version;
- `requires-python`;
- dist directory status.

## CLI examples

Build artifacts and run readiness checks:

```bash
python -m build
doctor-link distribution check . --dist dist --out DoctorReports/distribution
```

Print JSON:

```bash
doctor-link distribution check . --dist dist --json
```

## Safety boundaries

P7.5 avoids irreversible distribution actions. It only generates local evidence files that can be reviewed before any separate human-authorized distribution step.

## Validation

P7.5 includes tests for:

- valid wheel and source archive readiness;
- missing distribution artifacts;
- checksum output;
- manifest output;
- target environment output;
- CLI JSON output;
- CLI blocking behavior.
