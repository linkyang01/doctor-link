# P7 Acceptance Criteria

P7 is a runtime implementation phase. Documentation alone is not enough to mark a P7 runtime item complete.

## Universal completion criteria

A P7 item is complete only when the applicable checklist is satisfied:

- implementation code exists;
- CLI or runtime behavior exists where applicable;
- schema or configuration validation exists where applicable;
- tests exist;
- fixtures or sample inputs exist where useful;
- documentation is updated;
- CI passes;
- project tracking files are updated;
- audit or closure notes are added for the phase.

## Runtime feature criteria

Runtime features must include:

- deterministic local behavior;
- structured output files where appropriate;
- clear error and warning behavior;
- safe defaults;
- no hidden network calls;
- no source mutation unless explicitly requested;
- tests for success and failure paths.

## CLI feature criteria

CLI features must include:

- command registration;
- help text;
- JSON output mode when appropriate;
- non-zero exit behavior for errors where appropriate;
- tests using the CLI runner;
- documentation examples.

## Schema/configuration criteria

Schema or configuration work must include:

- loader behavior;
- validation behavior;
- invalid fixture coverage;
- backward-compatible or unsupported behavior documentation;
- clear warnings for unknown or unsupported fields.

## Workbench/UI criteria

Local workbench work must include:

- generated static output that can be opened locally;
- no default cloud dependency;
- no default write-back behavior;
- accessibility-oriented structure where feasible;
- tests that verify generated output contains expected controls or content.

If write-back is implemented, it must include:

- explicit opt-in;
- backup behavior;
- audit record;
- clear user-facing warning;
- tests for disabled-by-default behavior.

## Integration criteria

AI tool, adapter, or plugin integrations must include:

- local-first behavior;
- manifest or profile validation;
- capability checks;
- unsupported behavior warnings;
- privacy warnings when external tools may receive data;
- tests that do not require external accounts or cloud services.

## Integrity and privacy criteria

Integrity and privacy gates must include:

- deterministic reports;
- hash or policy verification where applicable;
- warnings vs errors clearly separated;
- unsafe path handling;
- missing file handling;
- redaction or privacy policy test fixtures.

## Release/distribution criteria

Release/distribution tooling may be implemented as dry-run automation.

Actual release actions remain blocked unless explicitly authorized:

- GitHub Release;
- release tag;
- PyPI publishing;
- repository permission changes.

Dry-run tooling must prove:

- dist artifacts can be built;
- metadata can be inspected;
- checksums can be generated;
- release manifest can be produced;
- blocking checklist can identify missing requirements.

## Final P7 closure criteria

P7 cannot be closed until:

- all selected P7 TODO items are complete;
- CI passes;
- runtime e2e validation passes;
- self-validation passes;
- README files are updated;
- `docs/project-status.md` is updated;
- `TODO-P7.md` is updated;
- final P7 audit is written;
- Issue #95 is closed only after explicit final authorization.
