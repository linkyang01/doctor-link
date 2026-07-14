# PyPI Trusted Publishing

Doctor link publishes to PyPI only after explicit authorization for an exact version. The repository uses PyPI Trusted Publishing instead of a stored API token.

## One-time PyPI account setup

Because `doctor-link` does not yet exist on PyPI, configure a pending GitHub publisher from the PyPI account publishing page with these exact values:

| Field | Value |
| --- | --- |
| PyPI project name | `doctor-link` |
| GitHub owner | `linkyang01` |
| GitHub repository | `doctor-link` |
| Workflow filename | `pypi-publish.yml` |
| Environment name | `pypi` |

The pending publisher does not reserve the project name. Dispatch the workflow immediately after registering it.

## GitHub environment

Create the GitHub Actions environment `pypi`. Restrict deployment to the default branch and require manual approval when repository policy supports it. No PyPI password or API token is stored in GitHub.

## Publish an existing immutable release

Run the `Publish GitHub release to PyPI` workflow with:

```text
tag: v0.5.0
confirmation: publish-doctor-link-to-pypi
```

The workflow downloads the existing GitHub Release distributions, checks that the tag matches package metadata, validates archive contents and Twine metadata, installs the wheel in isolation, and transfers only those validated files to a separate OIDC-enabled publish job. It does not rebuild the package or move the Git tag.

PyPI rejects replacement files for an existing version. If a published artifact is wrong, fix the source and publish a new semantic version.

## Verify publication

After the workflow succeeds:

```bash
python -m pip index versions doctor-link
pipx install doctor-link==0.5.0
doctor-link --version
```

Verify that the PyPI file hashes match the workflow output and that the project page reports Trusted Publishing and attestations.

