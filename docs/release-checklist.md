# Release Checklist

This checklist prepares and verifies a release. Stop before tag creation, GitHub Release publication, or registry upload unless explicit authorization names the target version and destination.

Do not publish without explicit authorization.

## Candidate identity

- [ ] Target semantic version is approved.
- [ ] Candidate branch and full commit SHA are recorded.
- [ ] `pyproject.toml` matches the target version.
- [ ] Requested tag is exactly `v<package-version>`.
- [ ] Tag does not already exist.
- [ ] Candidate is merged to `main`, or a different release ref is explicitly authorized.

## Documentation

- [ ] `CHANGELOG.md` contains complete target-version changes.
- [ ] Version-specific release notes exist and describe user impact, compatibility, validation, and known limitations.
- [ ] Root, English, and Chinese README status is accurate.
- [ ] Installation and quick-start commands match the candidate.
- [ ] Security policy and sensitive-data guidance are current.
- [ ] Project status, cloud certificate, evidence index, and scorecard cite the correct commit and Actions run.
- [ ] Documentation does not describe an unpublished version as Latest.

## Local quality gates

- [ ] `git diff --check` passes.
- [ ] `ruff check doctor_link tests scripts` passes.
- [ ] Tests pass with branch-aware coverage at or above 85%.
- [ ] Bandit reports no blocking medium/high findings.
- [ ] Dependency audit reports no unresolved known vulnerability.
- [ ] E2E validation passes.
- [ ] Self-validation passes.
- [ ] Project validation passes.
- [ ] P7 runtime validation passes.

## Distribution gates

- [ ] Wheel and source distribution build successfully.
- [ ] Distribution content validation passes.
- [ ] Generated/cache/runtime files are absent from the sdist.
- [ ] Twine metadata validation passes.
- [ ] Wheel installs into a clean environment.
- [ ] `pip check`, CLI version, preflight, and installed-wheel smoke checks pass.
- [ ] Release notes and license are present in the expected distribution scope.

## GitHub cloud gates

- [ ] Python 3.10 passes.
- [ ] Python 3.11 passes.
- [ ] Python 3.12 passes.
- [ ] Security job passes.
- [ ] Package build/install job passes.
- [ ] Ubuntu smoke passes.
- [ ] macOS smoke passes.
- [ ] Windows smoke passes.
- [ ] Workflow run URL and head SHA are recorded.

## Privacy and supply-chain review

- [ ] No secret, token, private key, customer data, or unredacted private evidence is tracked.
- [ ] Release archives contain only intended source and documentation.
- [ ] Dependency and GitHub Action updates have been reviewed.
- [ ] Artifact sharing and retention are appropriate for any diagnostic evidence.
- [ ] Release workflow permissions remain limited to required publication actions.

## Authorization and execution

- [ ] Explicit authorization names the version.
- [ ] Explicit authorization names GitHub Release publication.
- [ ] PyPI or other registry authorization is separately confirmed when applicable.
- [ ] Release workflow inputs are reviewed before dispatch.
- [ ] Existing tags are not moved or reused.

## Post-release verification

- [ ] Tag points to the intended commit.
- [ ] GitHub Release page exists and renders the approved notes.
- [ ] Expected wheel and sdist assets are attached.
- [ ] Installation from the published destination succeeds.
- [ ] README, project status, release notes, and validation documents are updated from candidate to published state.
- [ ] Any failed or partial publication is documented and followed by a new patch version rather than tag mutation.
