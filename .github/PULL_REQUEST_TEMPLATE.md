## Problem and root cause

Describe the user-visible problem or repository need and the underlying cause.

## Changes

Explain the implementation and list the important interfaces, commands, schemas, workflows, or documents affected.

## Impact

- User impact:
- Developer/maintainer impact:
- Compatibility considerations:

## Validation

- [ ] Relevant regression tests added or updated
- [ ] `pytest -q` passes
- [ ] Ruff passes when runtime code changed
- [ ] Coverage remains at or above 85% when runtime code changed
- [ ] E2E/P7 validation passes when command or workflow behavior changed
- [ ] Package checks pass when packaging or release behavior changed
- [ ] Documentation-only diff passes `git diff --check`

Commands and evidence:

```text
Add the commands, results, or Actions run links here.
```

## Security and privacy

- [ ] No secrets, customer data, or unredacted private evidence are included
- [ ] Command-execution changes preserve the reviewed shell-free/approval boundary
- [ ] Security and privacy implications are documented

## Documentation

- [ ] User-facing documentation updated
- [ ] English and Chinese entrypoints reviewed when status or usage changed
- [ ] Changelog and validation/release documents updated when applicable

## Release boundary

- [ ] This PR does not publish a release, move a tag, or upload to a package registry
- [ ] Any requested release action has separate explicit authorization

## Known limitations and follow-up

List anything intentionally left out of this PR.
