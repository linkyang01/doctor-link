from __future__ import annotations

from pathlib import Path

import yaml


def test_pr_diagnostics_workflow_example_is_valid_yaml() -> None:
    path = Path("docs/examples/doctor-link-pr-diagnostics.yml")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert payload["name"] == "Doctor link PR Diagnostics"
    assert "pull_request" in payload["on"]
    assert "doctor-link" in payload["jobs"]
    steps = payload["jobs"]["doctor-link"]["steps"]
    run_blocks = "\n".join(str(step.get("run", "")) for step in steps)
    assert "doctor-link strategy validate" in run_blocks
    assert "doctor-link diagnose verify" in run_blocks
    assert "DoctorReports/**" in str(steps[-1])
