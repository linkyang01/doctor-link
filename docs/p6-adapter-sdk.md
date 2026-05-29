# P6.3 Adapter SDK Planning

Status: planning specification only

## Scope

P6.3 defines the Adapter SDK planning specification for future Doctor link integrations.

This phase does not implement the runtime SDK, dynamic plugin loading, a hosted platform, cloud services, external accounts, marketplace distribution, or public release publishing.

## Goals

Adapter SDK planning defines how future adapters should describe their capabilities, collect evidence, contribute verification signals, and produce AI handoff context without weakening Doctor link's local-first diagnostic model.

## Adapter lifecycle

A future adapter should follow this lifecycle:

1. Declare metadata and capabilities.
2. Validate its local environment requirements.
3. Collect evidence from a target project or tool.
4. Normalize collected evidence into Doctor link package files.
5. Add reproduction, test, or verification signals when available.
6. Build AI handoff context only from recorded package evidence.
7. Report completion, warnings, and unsupported capabilities.

## Adapter metadata format

Every adapter should provide an `adapter-manifest.json` file.

Required fields:

```text
adapter_id
name
version
target
capabilities
entrypoints
supported_schema_versions
privacy
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

## Capability declaration

Capabilities should be explicit booleans or structured lists. An adapter must not imply support for capabilities that are not implemented.

Recommended capability groups:

```text
evidence_collection
reproduction
verification
handoff
redaction
project_health
schema_validation
```

## Evidence collector interface

A future evidence collector should accept:

```text
project_root
package_dir
adapter_options
```

It should return:

```text
status
evidence_items
warnings
unsupported_items
```

Rules:

- Evidence must be local or explicitly provided by the user.
- Sensitive material must be redacted before export.
- Evidence must be written into the diagnostic package rather than held only in memory.
- The adapter must not modify target project source files unless explicitly authorized.

## Verification provider interface

A future verification provider should accept:

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

Rules:

- Verification must be evidence-based.
- Candidate verification must not be presented as final acceptance without human review.
- Failed or missing evidence must remain visible in package outputs.

## Handoff provider interface

A future handoff provider should accept:

```text
package_dir
target_tool
handoff_options
```

It should return:

```text
output_dir
manifest_path
included_files
missing_files
warnings
```

Rules:

- Handoff content must reference package files.
- Handoff output must preserve investigation boundaries.
- Handoff output must warn when user-confirmed problems exist.
- Handoff output must not invent evidence.

## Adapter test requirements

Every future adapter should include:

- metadata validation tests;
- capability declaration tests;
- evidence collection dry-run tests;
- redaction boundary tests;
- schema compatibility tests;
- conformance fixture tests;
- unsupported capability behavior tests;
- documentation examples.

## First-party adapter rules

First-party adapters maintained in the Doctor link repository should:

- follow the current schema version policy;
- be covered by CI;
- include sample fixtures;
- keep local-first behavior;
- avoid hidden network calls;
- avoid paid cloud dependencies;
- document all limitations.

## Third-party adapter rules

Third-party adapters should:

- provide an `adapter-manifest.json` file;
- declare supported Doctor link schema versions;
- document external dependencies;
- document privacy behavior;
- include local conformance fixtures;
- avoid modifying Doctor link core package files outside supported extension points;
- be considered untrusted until reviewed.

## Non-goals

P6.3 does not include:

- adapter runtime implementation;
- plugin loading implementation;
- hosted adapter registry;
- cloud execution;
- account system;
- marketplace;
- public release publishing;
- PyPI publishing.
