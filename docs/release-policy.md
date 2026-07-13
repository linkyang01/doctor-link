# Release Policy

Doctor link uses semantic versioning and an explicit-authorization release model. Successful tests, a merged PR, and a published package are different states and must be documented separately.

## Versioning

Version format:

```text
MAJOR.MINOR.PATCH
```

- MAJOR: incompatible protocol, schema, package, or CLI behavior changes.
- MINOR: backward-compatible features, commands, package fields, or documented capability groups.
- PATCH: backward-compatible fixes, security hardening, documentation corrections, and test improvements.

Pre-release identifiers may be used for validation:

```text
0.2.0-alpha.1
0.2.0-rc.1
```

## Release states

Use these terms precisely:

| State | Meaning |
| --- | --- |
| Source candidate | Version exists in the repository but may not have complete validation. |
| Locally validated | Named commit passed recorded local gates. |
| Cloud validated | Named commit passed the configured GitHub Actions matrix. |
| Merged | Candidate commit is reachable from `main`. |
| Tagged | Immutable `v<version>` tag exists. |
| GitHub Release published | Release page and assets exist for the tag. |
| Registry published | Package exists on PyPI or another named registry. |

Do not call a version “Latest” unless GitHub Releases shows it as the current published release.

## Sources of truth

The package version in `pyproject.toml` is authoritative for build metadata. Release preparation must align:

- `pyproject.toml`;
- `CHANGELOG.md`;
- version-specific release notes;
- README and installation status;
- project and validation status documents;
- the requested Git tag.

The GitHub Release page is authoritative for GitHub publication. The package registry is authoritative for registry availability.

## Authorization rule

No publishing is allowed without explicit user authorization.

No public distribution is allowed without explicit authorization for the exact version and destination.

Separate authorization is required before:

- creating a release tag;
- creating a GitHub Release;
- uploading release assets;
- publishing to PyPI or another registry.

A request to fix code, open a PR, merge a PR, or make CI green does not implicitly authorize publication.

## Required engineering gates

Before requesting a release:

- the candidate commit is identified;
- the PR is reviewed and merged unless a different ref is explicitly authorized;
- Python 3.10, 3.11, and 3.12 jobs pass;
- Ubuntu, macOS, and Windows smoke jobs pass;
- Ruff and branch-aware coverage pass;
- Bandit and dependency audit pass;
- E2E and P7 runtime validation pass;
- wheel and sdist content checks pass;
- Twine metadata passes;
- isolated wheel installation and dependency consistency pass;
- changelog, release notes, installation, security, and validation documents are current;
- no secrets or private evidence are present in tracked files or release assets.

## Automated release workflow

`.github/workflows/release.yml` is manually dispatched with:

- `ref`: branch or commit to release;
- `tag`: expected `v<package-version>` tag;
- `body_path`: release-note Markdown file;
- `prerelease`: GitHub prerelease flag;
- `publish_pypi`: optional registry upload switch.

The workflow reruns quality/security gates, confirms the requested tag matches `pyproject.toml`, rejects an existing tag, builds and validates distributions, creates an annotated immutable tag, and publishes GitHub assets. PyPI upload occurs only when requested and when `PYPI_API_TOKEN` exists.

## Immutable tags

An existing release tag must never be moved or overwritten. If a published artifact is wrong:

1. stop further distribution;
2. document the problem;
3. prepare a new patch version;
4. rerun the complete validation sequence;
5. publish the new version with explicit authorization.

## Post-release verification

After publication, verify:

- the tag points to the intended commit;
- release notes render correctly;
- wheel and sdist assets are attached;
- checksums match locally validated artifacts when checksums are published;
- installation from the actual published location succeeds;
- README and validation status name the published version accurately.

## Current boundary

Version `0.1.3` was locally and cloud validated, merged through PR `#140` as commit `fa779da`, and published as [GitHub Release `v0.1.3`](https://github.com/linkyang01/doctor-link/releases/tag/v0.1.3) on 2026-07-13. Release workflow [29246045227](https://github.com/linkyang01/doctor-link/actions/runs/29246045227) installed the final wheel, passed the full capability lab, created the immutable tag, and uploaded the wheel and source distribution. PyPI publication was disabled and was not performed.
