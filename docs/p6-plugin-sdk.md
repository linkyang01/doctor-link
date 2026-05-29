# P6.4 Plugin SDK Planning

Status: planning specification only

## Scope

P6.4 defines the Plugin SDK planning specification for future Doctor link extension points.

This phase does not implement plugin runtime loading, dynamic execution, sandboxing, a hosted platform, cloud services, external accounts, marketplace distribution, or public release publishing.

## Goals

Plugin SDK planning defines how future plugins should declare metadata, request permissions, expose extension points, respect security boundaries, and remain compatible with Doctor link diagnostic package schema and conformance rules.

## Plugin package structure

A future plugin package should use a predictable local structure:

```text
plugin-root/
  plugin-manifest.json
  README.md
  examples/
  fixtures/
  tests/
  src/
```

Required file:

```text
plugin-manifest.json
```

Recommended files:

```text
README.md
LICENSE
CHANGELOG.md
fixtures/
tests/
```

## Plugin manifest format

Required manifest fields:

```text
plugin_id
name
version
kind
extension_points
permissions
supported_schema_versions
entrypoints
compatibility
security
```

Recommended manifest fields:

```text
description
author
homepage
license
minimum_doctor_link_version
requirements
limitations
```

## Plugin permission model

Plugins should declare requested permissions explicitly. A plugin must not receive capabilities that are not listed in its manifest.

Recommended permission groups:

```text
read_package
write_package
read_project
write_project
network
execute_command
render_output
export_package
```

Default future policy should be deny-by-default.

## Plugin loading boundary

A future plugin loader should enforce:

- explicit manifest validation;
- schema version compatibility checks;
- permission review before activation;
- local-only execution unless network permission is explicitly granted;
- clear unsupported behavior when a plugin requires unavailable capabilities;
- failure isolation so one plugin cannot corrupt diagnostic package state.

## Plugin security restrictions

Future plugins should follow these restrictions:

- no hidden network calls;
- no source modification without explicit authorization;
- no credential export;
- no unredacted sensitive evidence export;
- no silent package deletion or rewriting;
- no execution outside declared entrypoints;
- no privilege escalation through plugin metadata.

## Collector plugin extension point

Collector plugins may contribute additional evidence.

Input:

```text
project_root
package_dir
plugin_options
```

Output:

```text
status
evidence_items
warnings
unsupported_items
```

Rules:

- collected evidence must be written to the diagnostic package;
- redaction must run before export;
- unsupported items must be visible in output;
- collector plugins must not modify target source files by default.

## Renderer plugin extension point

Renderer plugins may produce additional local output views.

Input:

```text
package_dir
output_dir
renderer_options
```

Output:

```text
status
rendered_files
warnings
```

Rules:

- renderer output must be derived from package files;
- renderer output must not hide failed verification signals;
- renderer output must preserve user assertions and warnings.

## Handoff plugin extension point

Handoff plugins may format diagnostic packages for a target AI tool.

Input:

```text
package_dir
target_tool
handoff_options
```

Output:

```text
output_dir
manifest_path
included_files
missing_files
warnings
```

Rules:

- handoff output must preserve investigation boundaries;
- user-confirmed assertions must remain visible;
- missing evidence must remain visible;
- handoff plugins must not invent evidence.

## Verification plugin extension point

Verification plugins may contribute test or validation signals.

Input:

```text
package_dir
verification_options
```

Output:

```text
status
test_records
verification_notes
next_commands
```

Rules:

- verification must be reproducible where possible;
- partial or failed verification must remain visible;
- plugin results must not overwrite core verification results without explicit merge policy.

## Plugin compatibility checklist

Every future plugin should provide:

- valid `plugin-manifest.json`;
- supported schema versions;
- declared permissions;
- local fixtures;
- conformance tests;
- security notes;
- privacy behavior notes;
- unsupported capability behavior;
- example usage.

## Non-goals

P6.4 does not include:

- plugin runtime implementation;
- dynamic loading implementation;
- sandbox implementation;
- hosted registry;
- marketplace;
- cloud execution;
- account system;
- public release publishing;
- PyPI publishing.
