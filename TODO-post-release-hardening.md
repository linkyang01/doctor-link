# Post-release hardening TODO

Tracking issue: [#156](https://github.com/linkyang01/doctor-link/issues/156)

- [x] Define one authoritative current roadmap and mark historical plans clearly.
- [x] Align the release policy and project status with published v0.5.1.
- [x] Add public support, security reporting, compatibility, and deprecation guidance.
- [x] Add structured bug and feature-request intake.
- [x] Add a scheduled public PyPI installation smoke test.
- [x] Add a pinned, repeatable public-project validation set and local runner.
- [x] Fix high-priority external-test usability issues from #156 comments:
  - collection/setup failures are not `reproduced`
  - stop-word noise in problem matching
  - dirty worktree only blocks `--allow-repair`
  - robust `--tool` validation without fragile `click.Choice`
  - richer guided result HTML
- [x] Run the public-project validation and record evidence (`docs/validation/evidence/public-project-validation-2026-07-14/`, 6/6).
- [x] Pass complete local validation (ruff + 372 tests, coverage ≥ 85%).
- [ ] Merge the PR and close Issue #156 after CI succeeds.
