# Local Workbench Guide

Doctor link includes a local read-only workbench for diagnostic packages.

## Open a package

```bash
doctor-link view <package_dir>
```

Build static HTML only:

```bash
doctor-link view <package_dir> --build-only
```

## Open a reports directory

```bash
doctor-link view DoctorReports --build-only
```

This creates an index for multiple packages.

## What the workbench shows

- Summary
- Timeline
- Evidence
- User assertions
- AI task
- Verification
- Comparison
- Redaction and manifest information
- AI handoff blocks

## Read-only boundary

The workbench is read-only by default. It does not write back to diagnostic packages unless a future ADR explicitly changes that behavior.

## Project health panel

A dedicated project health panel is deferred to a future visual refresh. P4 still provides `doctor-link health` and `project-health.json/md`.
