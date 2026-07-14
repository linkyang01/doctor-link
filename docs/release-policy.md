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
- Python 3.10 through 3.14 jobs pass;
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
- `prerelease`: GitHub prerelease flag.

The workflow reruns quality/security gates, confirms the requested tag matches `pyproject.toml`, rejects an existing tag, builds and validates distributions, creates an annotated immutable tag, and publishes GitHub assets.

Registry publication is a separate operation. `.github/workflows/pypi-publish.yml` downloads an existing immutable GitHub Release, validates the exact distributions, and transfers them to an isolated publish job. The publish job uses the protected `pypi` GitHub environment and short-lived PyPI Trusted Publishing credentials; it does not use a stored `PYPI_API_TOKEN`, rebuild distributions, or move tags. See `docs/pypi-publishing.md`.

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

Version `0.5.1` is the current published release. It was locally and cloud validated, merged through PR `#154` as commit `ed7d2400036c862db198e9c269507d503ef606f6`, and published as [GitHub Release `v0.5.1`](https://github.com/linkyang01/doctor-link/releases/tag/v0.5.1) by workflow [29325885785](https://github.com/linkyang01/doctor-link/actions/runs/29325885785). Trusted Publishing workflow [29325997537](https://github.com/linkyang01/doctor-link/actions/runs/29325997537) published identical artifacts to [PyPI](https://pypi.org/project/doctor-link/0.5.1/). A clean public-index `pipx install doctor-link==0.5.1` and installed CLI preflight passed.

Future source changes, tags, GitHub Releases, and registry publications remain separate states and require the gates and explicit authorization above.
