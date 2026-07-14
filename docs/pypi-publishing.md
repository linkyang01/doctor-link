# PyPI Trusted Publishing

Doctor link publishes to PyPI only after explicit authorization for an exact version. The repository uses PyPI Trusted Publishing instead of a stored API token. Version `0.5.0` was first published by workflow `29324916796` on 2026-07-14; `0.5.1` is the first documentation-consistent patch release.

## One-time PyPI account setup

For the initial publication, a pending GitHub publisher was configured with these exact values:

| Field | Value |
| --- | --- |
| PyPI project name | `doctor-link` |
| GitHub owner | `linkyang01` |
| GitHub repository | `doctor-link` |
| Workflow filename | `pypi-publish.yml` |
| Environment name | `pypi` |

PyPI converted the pending publisher into the project's active trusted publisher during the first successful upload.

## GitHub environment

Create the GitHub Actions environment `pypi`. Restrict deployment to the default branch and require manual approval when repository policy supports it. No PyPI password or API token is stored in GitHub.

## Publish an existing immutable release

Run the `Publish GitHub release to PyPI` workflow with:

```text
tag: v0.5.1
confirmation: publish-doctor-link-to-pypi
```

The workflow downloads the existing GitHub Release distributions, checks that the tag matches package metadata, validates archive contents and Twine metadata, installs the wheel in isolation, and transfers only those validated files to a separate OIDC-enabled publish job. It does not rebuild the package or move the Git tag.

PyPI rejects replacement files for an existing version. If a published artifact is wrong, fix the source and publish a new semantic version.

## Verify publication

After the workflow succeeds:

```bash
python -m pip index versions doctor-link
pipx install doctor-link==0.5.1
doctor-link --version
```

Verify that the PyPI file hashes match the workflow output and that the project page reports Trusted Publishing and attestations.
