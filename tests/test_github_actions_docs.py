from __future__ import annotations

import re
from pathlib import Path

import yaml


ACTION_MAJORS = {
    "actions/checkout": "v7",
    "actions/download-artifact": "v8",
    "actions/setup-python": "v6",
    "actions/upload-artifact": "v7",
    "softprops/action-gh-release": "v3",
}


def test_pr_diagnostics_workflow_example_is_valid_yaml() -> None:
    path = Path("docs/examples/doctor-link-pr-diagnostics.yml")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    trigger = payload.get("on", payload.get(True, {}))

    assert payload["name"] == "Doctor link PR Diagnostics"
    assert "pull_request" in trigger
    assert "doctor-link" in payload["jobs"]
    steps = payload["jobs"]["doctor-link"]["steps"]
    run_blocks = "\n".join(str(step.get("run", "")) for step in steps)
    assert "doctor-link strategy validate" in run_blocks
    assert "doctor-link diagnose verify" in run_blocks
    assert "DoctorReports/**" in str(steps[-1])


def test_workflows_use_node24_action_majors_and_pinned_macos() -> None:
    paths = sorted(Path(".github/workflows").glob("*.yml"))
    paths.append(Path("docs/examples/doctor-link-pr-diagnostics.yml"))

    for path in paths:
        text = path.read_text(encoding="utf-8")
        yaml.safe_load(text)
        for action, major in re.findall(r"uses:\s*([^@\s]+)@(v\d+)", text):
            if action in ACTION_MAJORS:
                assert major == ACTION_MAJORS[action], f"{path}: {action}@{major}"

    ci_workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "macos-latest" not in ci_workflow
    assert "macos-15" in ci_workflow


def test_pypi_workflow_uses_isolated_trusted_publishing() -> None:
    text = Path(".github/workflows/pypi-publish.yml").read_text(encoding="utf-8")
    payload = yaml.safe_load(text)
    publish = payload["jobs"]["publish"]

    assert payload["permissions"] == {"contents": "read"}
    assert publish["needs"] == "validate"
    assert publish["environment"]["name"] == "pypi"
    assert publish["permissions"] == {"id-token": "write"}
    assert "pypa/gh-action-pypi-publish@release/v1" in text
    assert "PYPI_API_TOKEN" not in text
    assert "gh release download" in text
    assert "python -m build" not in text
