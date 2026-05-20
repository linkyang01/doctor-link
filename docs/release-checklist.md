# Release Checklist

This checklist is for release readiness only. Do not publish without explicit authorization.

## Preparation

- [ ] Confirm target semantic version.
- [ ] Confirm `pyproject.toml` version.
- [ ] Confirm `CHANGELOG.md` has target version notes or Unreleased notes.
- [ ] Confirm draft release notes exist.
- [ ] Confirm README files are current.
- [ ] Confirm user docs are current.
- [ ] Confirm examples are current.

## Quality

- [ ] CI passes on all supported Python versions.
- [ ] Local install smoke passes.
- [ ] Wheel build smoke passes.
- [ ] CLI smoke passes.
- [ ] P4 pipeline smoke passes.

## Privacy and security

- [ ] Redaction tests pass.
- [ ] Sensitive information handling docs are current.
- [ ] Exported package security checklist is current.
- [ ] No secrets are committed.

## Approval boundary

- [ ] Explicit user authorization has been received for publishing.
- [ ] If authorization is not present, stop before tagging, GitHub Release creation, or package registry publication.
