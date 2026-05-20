# Release Policy

Doctor link uses semantic versioning for public releases.

## Versioning

Version format:

```text
MAJOR.MINOR.PATCH
```

Rules:

- MAJOR: incompatible protocol or CLI behavior changes.
- MINOR: backward-compatible features, commands, package fields, or documentation groups.
- PATCH: backward-compatible bug fixes, documentation fixes, and test-only changes.

Pre-release identifiers may be used for internal validation:

```text
0.2.0-alpha.1
0.2.0-rc.1
```

## Source of truth

The package version in `pyproject.toml` is the source of truth.

Any release preparation PR must keep these files aligned:

- `pyproject.toml`
- `CHANGELOG.md`
- draft release notes under `docs/release-notes/`

## Approval rule

No publishing is allowed without explicit user authorization.

This includes:

- creating a GitHub Release;
- uploading release assets;
- publishing to PyPI or another package registry;
- tagging a release intended for public distribution.

P5 may prepare draft release notes and release checklists only. It must stop before publishing.

## Release readiness checks

Before a release can be requested:

- tests pass in CI;
- package build smoke passes;
- README and user docs are current;
- CHANGELOG has an entry for the target version;
- privacy and redaction documentation are current;
- examples are runnable or clearly marked as documentation examples.
