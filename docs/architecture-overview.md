# Architecture Overview

Doctor link is organized as a local diagnostic pipeline.

```mermaid
flowchart LR
  User[User / Developer] --> CLI[Doctor link CLI]
  CLI --> Package[Diagnostic Package]
  CLI --> Evidence[Evidence Collectors]
  CLI --> Verify[Verification Runner]
  CLI --> Handoff[AI Handoff]
  CLI --> Pipeline[P4 Pipeline]

  Evidence --> Package
  Verify --> Package
  Handoff --> AITool[AI Coding Tool]
  AITool --> Result[AI Repair Result]
  Result --> Package
  Pipeline --> Health[Project Health Summary]
  Package --> Workbench[Local Read-only Workbench]
```

## Layers

1. CLI entry layer.
2. Evidence and package generation layer.
3. AI Coding collaboration layer.
4. Automated diagnosis pipeline layer.
5. Local read-only workbench layer.

## Boundary

Doctor link is local-first. Cloud sync, external accounts, paid services, and release publishing are outside the default architecture.
