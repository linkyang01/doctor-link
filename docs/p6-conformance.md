# P6.2 Compatibility and Conformance Test Suite

Status: implemented for local schema compatibility checks

## Scope

P6.2 adds a local conformance suite for Doctor link diagnostic packages.

It validates whether packages conform to the P6.1 schema compatibility policy and records a compatibility score.

This phase does not implement a Web platform, cloud service, account system, marketplace, Adapter SDK, or Plugin SDK.

## Fixture groups

The conformance runner recognizes four fixture groups:

```text
valid/
invalid/
backward-compatible/
migration/
```

Expected behavior:

- `valid/`: packages must pass schema validation.
- `invalid/`: packages must fail schema validation.
- `backward-compatible/`: pre-v1 compatible packages must pass with warnings when appropriate.
- `migration/`: migration candidate packages must remain readable and schema-compatible.

## Command

Run:

```bash
doctor-link conformance run <fixtures_root>
```

Write reports to a specific directory:

```bash
doctor-link conformance run <fixtures_root> --out DoctorReports/conformance
```

Print JSON:

```bash
doctor-link conformance run <fixtures_root> --json
```

## Output files

The command writes:

```text
conformance-report.json
conformance-report.md
```

## Compatibility score

The compatibility score is calculated as:

```text
passed_cases / total_cases * 100
```

The suite passes only when all discovered cases match their expected result.

## CI coverage

P6.2 is covered by:

- unit tests for conformance scoring;
- CLI tests for report writing;
- `scripts/validate_doctor_link.sh` integration.

## Boundary

P6.2 is local validation and compatibility work only. It does not authorize release publishing, cloud services, external accounts, SDK implementation, or marketplace functionality.
