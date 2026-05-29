# P6.5 Third-party AI Coding Integration Specification

Status: planning specification only

## Scope

P6.5 defines the integration specification for third-party AI coding tools.

This phase does not implement live integrations, cloud services, external accounts, API calls, hosted execution, marketplace distribution, or release publishing.

## Goals

The goal is to define a stable handoff protocol that allows Doctor link diagnostic packages to be prepared for external AI coding tools without losing evidence boundaries, user-confirmed problem signals, schema compatibility, privacy warnings, or verification requirements.

## Generic AI tool handoff protocol

Every integration should follow this protocol:

1. Read a Doctor link diagnostic package.
2. Validate schema compatibility.
3. Check user assertions and known missing evidence.
4. Select the target AI coding tool profile.
5. Generate tool-specific handoff instructions.
6. Include only package-backed evidence.
7. Record included and missing files.
8. Warn about unsupported capabilities.
9. Preserve privacy and redaction boundaries.
10. Write a handoff manifest.

## Integration manifest format

Every planned integration should provide an `ai-tool-integration.json` manifest.

Required fields:

```text
integration_id
name
target_tool
version
handoff_protocol
supported_schema_versions
minimum_tool_capabilities
unsupported_behavior
privacy
```

Recommended fields:

```text
description
author
homepage
license
examples
limitations
```

## Minimum tool capability requirements

A supported AI coding integration should document whether the target tool supports:

```text
read_file_context
multi_file_context
structured_instructions
test_command_execution
patch_generation
human_review_loop
local_only_mode
network_required
```

If a tool does not support a required capability, the integration must document fallback behavior.

## Unsupported integration behavior

Unsupported behavior should be explicit.

Examples:

- refusing to produce a handoff package;
- producing a reduced handoff package;
- warning that evidence cannot be attached;
- warning that the target tool cannot execute tests;
- warning that local-only execution is not supported;
- warning that the target tool may send context to an external service.

## Integration test package format

A future integration test package should contain:

```text
doctor-report.json
ai-context.json
user-assertions.json
verification-result.json
handoff-manifest.json
expected-handoff/
```

The expected handoff directory should include the target tool instruction file and expected manifest fields.

## Codex integration specification

Codex handoff should emphasize:

- structured task summary;
- evidence-backed problem statement;
- affected files;
- reproduction and verification commands;
- user assertions;
- constraints and non-goals.

Codex integration should not assume access to private files that are not included in the diagnostic package.

## Cursor integration specification

Cursor handoff should emphasize:

- workspace-local files;
- concise context summary;
- selected evidence files;
- recommended search paths;
- clear patch boundary.

Cursor integration should warn when package evidence is incomplete.

## Continue integration specification

Continue handoff should emphasize:

- model-agnostic instruction blocks;
- local context references;
- verification checklist;
- redaction warnings.

Continue integration should document model/provider limitations outside Doctor link control.

## Aider integration specification

Aider handoff should emphasize:

- files to add to chat;
- problem statement;
- expected patch scope;
- test commands;
- human review requirements.

Aider integration should avoid suggesting edits to files outside the declared scope.

## OpenHands integration specification

OpenHands handoff should emphasize:

- task goal;
- environment constraints;
- reproduction commands;
- verification commands;
- evidence files;
- expected deliverables.

OpenHands integration should warn when commands may require external services.

## Claude Code integration specification

Claude Code handoff should emphasize:

- repository context;
- evidence-backed diagnosis;
- constraints;
- files to inspect;
- tests to run;
- final verification requirements.

Claude Code integration should preserve local-first and privacy boundaries.

## Non-goals

P6.5 does not include:

- real API integration with third-party tools;
- cloud execution;
- OAuth or external account connection;
- hosted handoff service;
- marketplace listing;
- public release publishing;
- PyPI publishing.
