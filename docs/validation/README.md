# Doctor link Validation Certification

This directory contains the evidence, checklists, certificates, and release-status records used to distinguish a locally tested source tree from a cloud-validated commit and a published release.

## Current status

```text
Local v0.3.0 candidate validation: passed (2026-07-13)
v0.3.0 cloud validation: 8/8 jobs passed (run 29261286975, code commit 9cec5d1)
v0.3.0 merge / tag / release: pending
Local repaired-source validation: passed (2026-07-13)
GitHub Actions cloud validation: passed (PR #145)
Current certification matrix: 8/8 jobs passed (run 29256743976)
Evidence-based repository readiness: 100/100
PR merge: completed (commit 40a547c)
GitHub Release v0.2.0: published (2026-07-13)
PyPI publication: not performed
```

## Start here

- [Validation evidence index](validation-evidence-index.md) — exact commits, workflow runs, jobs, commands, results, historical evidence, and interpretation boundaries.
- [JavaScript/TypeScript solve validation](javascript-typescript-solve-validation.md) — local `v0.3.0` candidate regressions, live repair evidence, hashes, and honest limits.
- [v0.3.0 candidate release notes](v0.3.0-release-notes.md) — prepared release contents; not proof that the version has been published.
- [Cloud validation certificate](cloud-validation-certificate.md) — scope certified by the current GitHub Actions run.
- [100-point quality scorecard](local-quality-scorecard.md) — weighted repository-readiness rubric and receipts.
- [Release checklist](release-candidate-checklist.md) — completed engineering, merge, and GitHub publication gates.
- [v0.1.2 release notes](v0.1.2-release-notes.md) — published release contents and installation guidance.
- [v0.1.3 release notes](v0.1.3-release-notes.md) — historical reliability and privacy-safe export release contents.
- [v0.2.0 release notes](v0.2.0-release-notes.md) — current automatic problem-solving release contents and validation contract.
- [GitHub Release v0.2.0](https://github.com/linkyang01/doctor-link/releases/tag/v0.2.0) — authoritative current publication page and assets.

## Supporting records

- `p5.10-local-validation.md` in the parent docs directory records the historical local Mac validation.
- `local-validation-pending.md` is a historical planning record and should not override newer evidence.
- `v0.1.0-rc.1-release-notes.md` and `v0.1.1-release-notes.md` describe previously published or prepared versions.

## Interpretation rule

Use the newest evidence that names the exact commit or PR head being assessed. Never convert a successful local build into a cloud certificate, a successful Actions run into a merged state, or a merged state into a published release without direct GitHub evidence.
