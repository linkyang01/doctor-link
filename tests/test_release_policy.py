from __future__ import annotations

import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def test_pyproject_version_is_semver() -> None:
    payload = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    version = payload["project"]["version"]

    assert SEMVER_RE.match(version), version


def test_changelog_has_unreleased_section() -> None:
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

    assert "## Unreleased" in changelog
    assert "semantic versioning" in changelog.lower()


def test_release_policy_requires_explicit_authorization() -> None:
    policy = Path("docs/release-policy.md").read_text(encoding="utf-8").lower()
    checklist = Path("docs/release-checklist.md").read_text(encoding="utf-8").lower()

    assert "no publishing is allowed without explicit user authorization" in policy
    assert "do not publish without explicit authorization" in checklist
    assert "pypi" in policy
    assert "github release" in policy


def test_release_workflow_uses_version_matched_immutable_tags() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
    payload = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    version = payload["project"]["version"]

    assert f"default: v{version}" in workflow
    assert "git push origin \"${RELEASE_TAG}\"" in workflow
    assert "--force" not in workflow
    assert "Release tag already exists and will not be moved" in workflow
