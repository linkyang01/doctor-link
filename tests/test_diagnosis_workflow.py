from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.diagnosis_workflow import create_after_package, create_before_package, read_workflow_metadata
from doctor_link.p4_cli import main


def test_create_before_and_after_packages_are_linked(tmp_path: Path) -> None:
    output = tmp_path / "DoctorReports"

    before = create_before_package("Demo Project", "before issue", output)
    after = create_after_package("Demo Project", "after fix", output, before)

    before_meta = read_workflow_metadata(before)
    after_meta = read_workflow_metadata(after)

    assert before_meta is not None
    assert after_meta is not None
    assert before_meta.phase == "before"
    assert after_meta.phase == "after"
    assert before_meta.workflow_id == after_meta.workflow_id
    assert after_meta.before_package == str(before)
    assert after_meta.before_report == str(before / "doctor-report.json")
    assert after_meta.after_report == str(after / "doctor-report.json")
    assert (before / "diagnosis-workflow.json").exists()
    assert (after / "diagnosis-workflow.md").exists()

    after_report = json.loads((after / "doctor-report.json").read_text(encoding="utf-8"))
    assert after_report["diagnosis_workflow"]["before_report"] == str(before / "doctor-report.json")


def test_diagnose_before_after_cli(tmp_path: Path) -> None:
    output = tmp_path / "DoctorReports"
    runner = CliRunner()

    before_result = runner.invoke(
        main,
        ["diagnose", "before", "--project", "Demo", "--summary", "before issue", "--out", str(output)],
    )

    assert before_result.exit_code == 0, before_result.output
    assert "Created before package" in before_result.output
    before_line = next(line for line in before_result.output.splitlines() if line.startswith("Created before package:"))
    before_package = Path(before_line.split(":", 1)[1].strip())

    after_result = runner.invoke(
        main,
        [
            "diagnose",
            "after",
            "--project",
            "Demo",
            "--summary",
            "after fix",
            "--before-package",
            str(before_package),
            "--out",
            str(output),
        ],
    )

    assert after_result.exit_code == 0, after_result.output
    assert "Created after package" in after_result.output
    after_line = next(line for line in after_result.output.splitlines() if line.startswith("Created after package:"))
    after_package = Path(after_line.split(":", 1)[1].strip())
    assert (after_package / "diagnosis-workflow.json").exists()
    meta = json.loads((after_package / "diagnosis-workflow.json").read_text(encoding="utf-8"))
    assert meta["before_report"] == str(before_package / "doctor-report.json")
