# Adapter Concept

Doctor link adapters are a documentation-level concept for connecting project-specific tools, evidence sources, and AI Coding workflows to the Doctor link diagnostic package format.

P5 documents adapter boundaries. It does not introduce a stable SDK or plugin runtime.

## Adapter goals

Adapters should help teams:

- collect project-specific evidence;
- generate project-specific reproduction commands;
- normalize tool outputs into diagnostic evidence;
- create AI handoff profiles;
- preserve verification-first closure.

## Adapter types

Potential future adapter types:

- collector adapters;
- media or artifact probe adapters;
- AI handoff profile adapters;
- verification adapters;
- project template adapters.

## Current boundary

Current Doctor link extension is configuration-first:

- `.doctorlink/diagnosis.yml`
- `.doctorlink/reproduce.yml`
- `.doctorlink/test-matrix.yml`
- `.doctorlink/collect.yml`
- `.doctorlink/verification.yml`

Future SDK work must be planned separately and should not be implied as stable in P5.
