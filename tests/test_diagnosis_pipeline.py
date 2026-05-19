from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.diagnosis_pipeline import run_diagnosis_compare, run_diagnosis_verify
from doctor_link.core.diagnosis_workflow import create_after_package, create_before_package
from doctor_link.p4_cli import main


def _before_after(tmp_path: Path) -> tuple[Path, Path]:
    output = tmp_path / "DoctorReports"
    before = create_before_package("Demo", "before issue", output)
    after = create_after_package("Demo", "after fix", output, before)
    return before, after


def test_diagnosis_compare_generates_pipeline_summary(tmp_path: Path) -> None:
    _, after = _before_after(tmp_path)

    summary = run_diagnosis_compare(after)

    assert summary.comparison_status == "generated"
    assert summary.success is False
    assert summary.before_report is not None
    assert (after / "diagnosis-pipeline-summary.json").exists()
    assert (after / "diagnosis-pipeline-summary.md").exists()
    report = json.loads((after / "doctor-report.json").read_text(encoding="utf-8"))
    assert "diagnosis_pipeline_summary" in report


def test_diagnosis_verify_does_not_succeed_without_verification_evidence(tmp_path: Path) -> None:
    _, after = _before_after(tmp_path)

    summary = run_diagnosis_verify(after, write_back=True)

    assert summary.comparison_status == "generated"
    assert summary.success is False
    assert summary.verification_status != "verified" or summary.missing_evidence
    assert "pipeline is not successful" in "\n".join(summary.notes)
    assert (after / "verification-result.json").exists()


def test_diagnose_compare_and_verify_cli(tmp_path: Path) -> None:
    _, after = _before_after(tmp_path)
    runner = CliRunner()

    compare_result = runner.invoke(main, ["diagnose", "compare", str(after), "--json"])
    verify_result = runner.invoke(main, ["diagnose", "verify", str(after), "--json"])

    assert compare_result.exit_code == 0, compare_result.output
    assert verify_result.exit_code == 0, verify_result.output
    compare_payload = json.loads(compare_result.output)
    verify_payload = json.loads(verify_result.output)
    assert compare_payload["comparison_status"] == "generated"
    assert verify_payload["success"] is False
    assert (after / "diagnosis-pipeline-summary.json").exists()
