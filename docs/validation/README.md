# Doctor link Validation Certification

This directory contains the evidence, checklists, certificates, and release-status records used to distinguish a locally tested source tree from a cloud-validated commit and a published release.

## Current status

```text
Local repaired-source validation: passed (2026-07-13)
GitHub Actions cloud validation: passed (PR #134)
100-point certification matrix: 8/8 jobs passed (run 29221918410)
Evidence-based repository readiness: 100/100
PR merge: completed (commit 862281f)
GitHub Release v0.1.2: published (2026-07-13)
PyPI publication: not performed
```

## Start here

- [Validation evidence index](validation-evidence-index.md) — exact commits, workflow runs, jobs, commands, results, historical evidence, and interpretation boundaries.
- [Cloud validation certificate](cloud-validation-certificate.md) — scope certified by the current GitHub Actions run.
- [100-point quality scorecard](local-quality-scorecard.md) — weighted repository-readiness rubric and receipts.
- [Release checklist](release-candidate-checklist.md) — completed engineering, merge, and GitHub publication gates.
- [v0.1.2 release notes](v0.1.2-release-notes.md) — published release contents and installation guidance.
- [GitHub Release v0.1.2](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.2) — authoritative publication page and assets.

## Supporting records

- `p5.10-local-validation.md` in the parent docs directory records the historical local Mac validation.
- `local-validation-pending.md` is a historical planning record and should not override newer evidence.
- `v0.1.0-rc.1-release-notes.md` and `v0.1.1-release-notes.md` describe previously published or prepared versions.

## Interpretation rule

Use the newest evidence that names the exact commit or PR head being assessed. Never convert a successful local build into a cloud certificate, a successful Actions run into a merged state, or a merged state into a published release without direct GitHub evidence.
