# Doctor link P5.9 TODO

Primary Issue: #71
Earlier tracker: #66

Goal: release hardening and usability validation before any future internal pre-release review.

Boundary: P5.9 does not publish a release, create a GitHub Release, publish to PyPI, change repository permissions, introduce paid cloud services, add external account systems, change Doctor link positioning, make the local read-only Web UI write back by default, or start P6 implementation.

## Work items

- [x] Create P5.9 tracking issue.
- [x] Add P5.9 tracker.
- [x] Add wheel build validation.
- [x] Add wheel install CLI smoke.
- [x] Add one-command local usability validation script.
- [x] Add local usability validation documentation.
- [x] Add end-to-end validation script.
- [x] Add end-to-end validation documentation.
- [x] Add ruff static checks.
- [x] Add coverage reporting.
- [x] Review CLI entrypoint structure.
- [x] Update README and tracking docs.
- [x] Add P5.9 final audit.
- [ ] Close or supersede duplicate P5.9 tracking issue after this closeout PR passes CI and merges.

## Completion criteria

P5.9 is considered complete when this closeout PR passes CI and merges. The remaining post-merge action is administrative issue cleanup only; no additional product code is required for P5.9.

## Implementation evidence

- PR #67 added the P5.9 tracker.
- PR #68 added wheel build and installed CLI smoke validation.
- PR #69 added local usability validation.
- PR #72 added release hardening validation, including ruff, coverage, wheel build, installed wheel smoke, and end-to-end validation.

## Remaining boundary

Publishing still requires separate explicit authorization. P6 implementation still requires separate explicit authorization.
