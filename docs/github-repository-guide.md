# GitHub Repository and Workflow Guide

This guide explains how the Doctor link GitHub repository is organized, how contributors should use issues and pull requests, what each workflow validates, and where release authority stops.

## Repository entrypoints

- Repository: `https://github.com/linkyang01/doctor-link`
- Default branch: `main`
- Issues: `https://github.com/linkyang01/doctor-link/issues`
- Actions: `https://github.com/linkyang01/doctor-link/actions`
- Pull requests: `https://github.com/linkyang01/doctor-link/pulls`
- Releases: `https://github.com/linkyang01/doctor-link/releases`

The root README is the user entrypoint. `CONTRIBUTING.md` defines contribution requirements, `SECURITY.md` defines private reporting and trust boundaries, and `docs/validation/` contains evidence-backed certification records.

## Issue workflow

Use the Diagnostic Issue form for reproducible software problems. A useful issue contains:

1. a concise problem summary;
2. expected and actual behavior;
3. exact reproduction steps;
4. Doctor link and Python versions;
5. operating system;
6. safe evidence or report paths;
7. a human-confirmed assertion when AI output missed the issue;
8. a proposed verification method.

Do not upload secrets, customer data, private diagnostic packages, access tokens, or unredacted logs. Security vulnerabilities belong in GitHub private vulnerability reporting, not a public issue.

## Pull request workflow

PRs should target `main` from a focused branch. The PR template asks for the problem, implementation, impact, validation, security review, documentation updates, and release boundary.

Recommended lifecycle:

```text
issue or evidence → focused branch → local gates → draft PR → cloud matrix → review → merge
```

Use a draft PR while implementation or validation is incomplete. Mark it ready only when the description is complete, documentation is aligned, the worktree is clean, and all expected checks pass.

## Continuous integration workflow

Workflow file: `.github/workflows/ci.yml`

Triggers:

- pushes to `main`;
- pull requests targeting `main`;
- manual workflow dispatch.

The workflow uses read-only repository contents permission and cancels superseded runs for the same ref.

### Python matrix

Python 3.10, 3.11, and 3.12 jobs each run:

- editable installation with development dependencies;
- dependency consistency check;
- Ruff;
- 273-test regression suite;
- branch-aware coverage with an 85% minimum;
- CLI smoke checks;
- E2E validation;
- wheel and sdist build;
- distribution content and Twine checks;
- P7 runtime validation;
- installed-wheel smoke validation;
- artifact upload even when a validation step fails.

### Package job

The package job independently builds wheel and sdist artifacts, validates archive contents, checks metadata, installs the wheel into a clean environment, runs `pip check`, executes preflight, and runs project/P7 validation.

This job catches packaging defects that an editable source installation can hide.

### Security job

The security job runs Bandit against `doctor_link/` and audits installed dependencies. It is intentionally separate from the test matrix so security failures remain visible as a distinct gate.

### Cross-platform job

Ubuntu, macOS, and Windows runners install the source package with Python 3.12 and run version, strategy, preflight, and focused regression checks. This proves basic CLI and configuration portability across GitHub-hosted operating systems.

### Artifacts

CI may upload:

- test output and `coverage.xml`;
- wheel and source distribution archives;
- E2E and P7 runtime directories;
- diagnostic reports;
- package validation artifacts.

Artifacts can contain diagnostic evidence. Review them before downloading to or sharing from another environment.

## Manual validation workflow

Workflow file: `.github/workflows/manual-validation.yml`

The manual workflow runs the full Ubuntu/Python 3.12 validation sequence and uploads a dedicated summary, coverage, distributions, usability-validation output, and E2E evidence. Use it for an explicit release-candidate refresh or after repository settings change.

Manual validation does not publish anything.

## Self-validation workflow

Workflow file: `.github/workflows/self-validation.yml`

Doctor link diagnoses its own repository and preserves the resulting reports as workflow evidence. This checks the real user-facing path in addition to unit tests.

## Release workflow

Workflow file: `.github/workflows/release.yml`

The release workflow is manual and accepts a source ref, tag, release-note path, prerelease flag, and optional PyPI switch. It:

1. checks out the requested ref;
2. installs development and build tools;
3. reruns tests, coverage, Ruff, Bandit, and dependency audit;
4. verifies the tag matches the package version;
5. rejects an existing tag instead of moving it;
6. builds and validates wheel/sdist artifacts;
7. creates the immutable tag and GitHub Release assets;
8. uploads to PyPI only when explicitly requested and configured.

Do not dispatch this workflow merely because CI is green. A release requires explicit authorization for the exact version and destination.

## Dependabot

`.github/dependabot.yml` monitors Python packages and GitHub Actions. Dependabot PRs must pass the same CI gates as human-authored changes. Review behavioral and supply-chain impact; do not merge solely because the version is newer.

## Current validation evidence

The current `0.1.3` implementation was validated in PR `#140`.

- final PR CI: `29245883700`;
- Release workflow: `29246045227`;
- result: eight of eight jobs passed;
- operating systems: Ubuntu, macOS, Windows;
- Python versions: 3.10, 3.11, 3.12;
- installed-package capability coverage: 62/62 routes, 70 invocations, eight complex scenarios.

See the [cloud certificate](validation/cloud-validation-certificate.md), [evidence index](validation/validation-evidence-index.md), and [100-point scorecard](validation/local-quality-scorecard.md).

## Recommended repository protections

For a protected `main` branch, repository administrators should consider requiring:

- pull requests before merging;
- all Doctor link CI jobs;
- conversation resolution;
- non-force-push history;
- restricted tag creation for release tags;
- review of workflow-file changes by a trusted maintainer.

These are repository-setting recommendations, not claims that every protection is currently enabled.

## Publication boundary

Merging code, passing CI, tagging a version, creating a GitHub Release, and publishing to PyPI are separate states. Documentation must name the state that has actually occurred and link to evidence. Never describe an unpublished version as the latest release.
