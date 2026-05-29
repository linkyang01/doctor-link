# P6.1 Diagnostic Package Schema v1

Status: implemented for local package validation

## Scope

P6.1 defines the first compatibility policy for Doctor link diagnostic package files.

This phase intentionally starts with schema standardization only. It does not implement a Web platform, cloud service, external account system, marketplace, adapter SDK, or plugin SDK.

## Schema version

Current schema version:

```text
1.0.0
```

Schema version is represented by the project constant:

```python
SCHEMA_VERSION = "1.0.0"
```

Generated and historical packages without `schema_version` are treated as pre-v1 compatible payloads and produce warnings rather than hard failures. This keeps P6.1 compatible with packages created before schema versioning was introduced.

## Core diagnostic package files

The validator treats the following files as core files:

```text
doctor-report.json
ai-context.json
user-assertions.json
```

These files must exist in a diagnostic package.

## Optional package files

The validator checks the following files when present:

```text
verification-result.json
ai-repair-result.json
diagnosis-history.json
handoff-manifest.json
manifest.json
```

## Validation command

Run:

```bash
doctor-link schema validate <package_dir>
```

Write validation artifacts into the package:

```bash
doctor-link schema validate <package_dir> --write
```

Print machine-readable output:

```bash
doctor-link schema validate <package_dir> --json
```

The `--write` option writes:

```text
schema-validation-result.json
schema-validation-result.md
```

## Compatibility policy

P6.1 uses the following compatibility policy:

1. Missing core files are errors.
2. Invalid JSON is an error.
3. Required structural fields are errors.
4. Wrong container type is an error, for example an object where an array is required.
5. Missing `schema_version` is a warning for pre-v1 compatibility.
6. Unsupported future `schema_version` is an error.
7. Optional package files are validated only when present.

## Migration policy

P6.1 does not automatically rewrite older packages. Migration is currently manual and conservative:

- run schema validation;
- inspect warnings;
- regenerate the diagnostic package if possible;
- keep historical packages readable;
- do not silently alter user evidence.

Future migration commands can be planned in P6.2 or later.

## Non-goals

P6.1 does not include:

- cloud service integration;
- hosted Web platform;
- account system;
- marketplace;
- adapter SDK implementation;
- plugin SDK implementation;
- public release publishing;
- PyPI publishing.
