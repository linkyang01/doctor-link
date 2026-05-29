# P6.4 Plugin SDK Planning

Status: planning specification only

## Scope

P6.4 defines the Plugin SDK planning specification for future Doctor link extension points.

This phase does not implement plugin runtime loading, marketplace distribution, a hosted platform, cloud services, external accounts, or public release publishing.

## Goals

Plugin SDK planning defines how future plugins should describe their package structure, permissions, loading boundaries, security restrictions, and extension points.

The goal is to make future plugin work auditable, local-first, and compatible with Doctor link diagnostic package schema rules.

## Plugin package structure

A future plugin package should include:

```text
plugin-manifest.json
README.md
examples/
tests/
```

Optional directories:

```text
schemas/
templates/
fixtures/
```

## Plugin manifest format

Required manifest fields:

```text
plugin_id
name
version
kind
capabilities
entrypoints
permissions
supported_schema_versions
security
```

Recommended fields:

```text
description
author
homepage
license
minimum_doctor_link_version
requirements
limitations
```

## Permission model

Plugin permissions should be explicit and conservative.

Recommended permission groups:

```text
read_package
write_package
read_project
run_local_command
network_access
export_files
```

Default policy:

- `network_access` should default to false.
- `run_local_command` should require explicit user approval.
- `write_package` should be limited to supported output files.
- `read_project` should be limited to the user-selected project root.

## Loading boundary

A future plugin loader should enforce:

- manifest validation before plugin execution;
- explicit capability checks;
- explicit permission checks;
- local-only execution by default;
- no hidden network access;
- no mutation of target project source files without user approval;
- no modification of Doctor link core schema files at runtime.

## Security restrictions

Plugins should not be trusted by default.

Security rules:

- Treat third-party plugins as untrusted until reviewed.
- Require manifest-declared permissions.
- Preserve redaction boundaries.
- Preserve diagnostic package evidence provenance.
- Record plugin warnings and unsupported behavior.
- Avoid loading arbitrary remote code.
- Avoid storing credentials in diagnostic packages.

## Extension points

Future plugin extension points may include:

```text
collector
renderer
handoff
verification
```

### Collector plugin extension point

A collector plugin may add evidence to a diagnostic package.

It should accept:

```text
project_root
package_dir
plugin_options
```

It should return:

```text
status
evidence_items
warnings
unsupported_items
```

### Renderer plugin extension point

A renderer plugin may produce derived local reports from existing package data.

It should accept:

```text
package_dir
output_dir
renderer_options
```

It should return:

```text
status
output_files
warnings
```

### Handoff plugin extension point

A handoff plugin may prepare package evidence for a target AI coding tool.

It should accept:

```text
package_dir
target_tool
output_dir
handoff_options
```

It should return:

```text
status
manifest_path
included_files
missing_files
warnings
```

### Verification plugin extension point

A verification plugin may add test records or verification notes.

It should accept:

```text
package_dir
verification_options
```

It should return:

```text
status
test_records
verification_notes
next_commands
```

## Plugin compatibility checklist

A future plugin should be considered compatible only if it:

- includes a valid `plugin-manifest.json`;
- declares supported schema versions;
- declares all required permissions;
- avoids hidden network behavior;
- preserves local-first operation;
- includes conformance fixtures;
- includes documentation examples;
- includes tests for unsupported behavior;
- keeps output files inside approved locations.

## Non-goals

P6.4 does not include:

- plugin runtime implementation;
- dynamic plugin loading;
- plugin marketplace;
- hosted registry;
- external account system;
- cloud execution;
- public release publishing;
- PyPI publishing.
