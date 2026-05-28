# Project Freeze before P6

Status: active until P5.10 local validation is recorded and P6 is separately authorized

## Purpose

This document defines the project freeze boundary after P5.9/P5.10 remote closeout and before any P6 implementation work.

The purpose is to prevent accidental scope creep, premature release publishing, or unapproved ecosystem/platform work.

## Current phase boundary

Doctor link is currently in a P5.10 validation state:

- P0 through P5.9 are complete.
- P5.10 remote closeout is complete.
- P5.10 local validation result is pending.
- P6 is not started.

## Allowed during freeze

The following work is allowed:

- documentation consistency fixes;
- CI stability fixes;
- validation script fixes;
- test reliability fixes;
- security and privacy corrections;
- corrections to tracking documents;
- local validation result recording;
- issue or PR cleanup for stale work.

## Not allowed during freeze

The following work is not allowed without separate explicit authorization:

- P6 implementation;
- schema implementation work;
- adapter SDK implementation;
- plugin SDK implementation;
- ecosystem platform or marketplace work;
- cloud service integration;
- external account system integration;
- GitHub Release creation;
- release tag creation;
- PyPI publishing;
- repository permission changes;
- product positioning changes;
- making the local read-only Web UI write back by default;
- unrelated product features.

## P6 gate

P6 may be discussed only after P5.10 local validation is recorded.

P6 implementation may begin only after separate explicit authorization.

If authorized later, P6 must begin with P6.1 Diagnostic Package Schema v1 and must not begin with Web platform, cloud service, external account system, marketplace, or ecosystem portal work.

## Release gate

No release publishing is authorized by P5.10.

Release publishing requires a separate release decision and should not occur until local validation has passed and been recorded.
