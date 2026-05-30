# P6.10 Public Ecosystem Assets

Status: planning specification only

## Scope

P6.10 defines public ecosystem asset structures for Doctor link.

This phase does not publish a marketplace, hosted registry, cloud service, external account system, public release, GitHub Release, release tag, or PyPI package.

## Goals

P6.10 defines:

- public example diagnostic package library;
- template catalog structure;
- adapter catalog structure;
- plugin catalog structure;
- compatibility badge rules;
- contribution guide for examples;
- contribution guide for adapters;
- contribution guide for plugins;
- ecosystem documentation index.

## Public example diagnostic package library

A future public example library should contain sanitized diagnostic packages for documentation, testing, and onboarding.

Recommended structure:

```text
examples/
  diagnostic-packages/
    basic-build-failure/
    schema-validation-demo/
    human-assertion-demo/
    conformance-demo/
```

Rules:

- Examples must not contain secrets.
- Examples must not contain customer or private project data.
- Examples should pass schema validation.
- Examples should document what scenario they demonstrate.
- Examples should be safe for public review.

## Template catalog structure

A future template catalog should organize reusable package, report, and handoff templates.

Recommended structure:

```text
templates/
  diagnostic-package/
  handoff/
  verification/
  privacy-review/
  governance-review/
```

Each template should include:

```text
template_id
name
version
purpose
required_inputs
output_files
supported_schema_versions
```

## Adapter catalog structure

A future adapter catalog should list first-party and reviewed third-party adapters.

Recommended fields:

```text
adapter_id
name
target
version
status
supported_schema_versions
capabilities
privacy_notes
review_status
```

Status values:

```text
planned
experimental
reviewed
deprecated
unsupported
```

## Plugin catalog structure

A future plugin catalog should list collector, renderer, handoff, and verification plugins.

Recommended fields:

```text
plugin_id
name
kind
version
status
permissions
supported_schema_versions
security_notes
review_status
```

Rules:

- Plugins should be treated as untrusted until reviewed.
- Permissions must be explicit.
- Network access must be visible.
- Compatibility must reference schema versions.

## Compatibility badge rules

A future compatibility badge should summarize whether an ecosystem asset works with a Doctor link schema version.

Recommended badges:

```text
schema-v1-compatible
conformance-tested
privacy-reviewed
security-reviewed
local-only
requires-network
experimental
```

Rules:

- Badges must be evidence-backed.
- Badges must not imply security certification unless reviewed.
- Experimental assets must be labeled clearly.

## Contribution guide for examples

Example contributions should include:

- scenario description;
- sanitized diagnostic package files;
- expected schema validation result;
- expected conformance result when applicable;
- privacy review note;
- no secrets or customer data.

## Contribution guide for adapters

Adapter contributions should include:

- `adapter-manifest.json`;
- supported schema versions;
- capability declaration;
- local-only and network behavior;
- evidence collection boundaries;
- tests or fixtures;
- privacy and security notes.

## Contribution guide for plugins

Plugin contributions should include:

- `plugin-manifest.json`;
- permission declaration;
- extension point declaration;
- unsupported behavior documentation;
- tests or fixtures;
- privacy and security notes.

## Ecosystem documentation index

A future ecosystem documentation index should link:

```text
P6 schema documentation
conformance suite documentation
adapter planning specification
plugin planning specification
AI coding integration specification
signing and integrity specification
privacy and security specification
enterprise governance specification
diagnostic knowledge base specification
public ecosystem asset specification
quality and closure checklist
```

## Non-goals

P6.10 does not include:

- marketplace implementation;
- hosted registry;
- cloud catalog service;
- account system;
- release publishing;
- PyPI publishing;
- third-party asset certification.
