from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.ci_automation import build_ci_report, write_ci_report
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.p4_cli import main


def _package(tmp_path: Path, name: str, status: str, missing: list[str] | None = None, test_status: str = "passed") -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project=name, category="ci", summary=f"{name} package"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    package_dir = package.root_dir
    (package_dir / "verification-result.json").write_text(
        json.dumps({"status": status, "missing_evidence": missing or [], "tests_to_rerun": ["pytest"] if missing else []}),
        encoding="utf-8",
    )
    evidence_dir = package_dir / "evidence" / "test-results"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / f"{name}-test.json").write_text(
        json.dumps({"job": {"job_id": f"{name}-job"}, "result": {"job_id": f"{name}-job", "status": test_status, "return_code": 0 if test_status == "passed" else 1}}),
        encoding="utf-8",
    )
    (package_dir / "diagnosis-pipeline-summary.json").write_text(
        json.dumps({"success": status in {"verified", "passed"}, "verification_status": status}),
        encoding="utf-8",
    )
    return package_dir


def test_p7_ci_report_builds_triage_score_matrix_trend_and_artifact_index(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    _package(tmp_path, "good", "verified", test_status="passed")
    _package(tmp_path, "bad", "missing_evidence", missing=["ev-1"], test_status="failed")

    report = build_ci_report(reports_dir)

    assert report.package_count == 2
    assert report.status == "needs_attention"
    assert report.regression_score < 100
    assert report.test_matrix_summary["total"] == 2
    assert report.test_matrix_summary["failed"] == 1
    assert report.health_trend["source_package_count"] == 2
    assert report.failure_triage
    assert any(item["category"] == "missing_evidence" for item in report.failure_triage)
    assert report.artifact_index["artifact_count"] > 0


def test_p7_ci_report_writes_expected_artifacts(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    _package(tmp_path, "bad", "missing_evidence", missing=["ev-1"], test_status="failed")
    output = tmp_path / "ci-out"

    report = write_ci_report(reports_dir, output_dir=output)

    assert report.status == "needs_attention"
    assert (output / "ci-report.json").exists()
    assert (output / "ci-report.md").exists()
    assert (output / "github-step-summary.md").exists()
    assert (output / "ci-artifact-index.json").exists()
    assert (output / "project-health-trend.json").exists()
    summary = (output / "github-step-summary.md").read_text(encoding="utf-8")
    assert "Doctor link CI Summary" in summary
    assert "Top failure triage" in summary
    index = json.loads((output / "ci-artifact-index.json").read_text(encoding="utf-8"))
    assert index["artifact_count"] > 0


def test_p7_ci_report_cli(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    _package(tmp_path, "bad", "missing_evidence", missing=["ev-1"], test_status="failed")
    output = tmp_path / "ci-out"
    runner = CliRunner()

    result = runner.invoke(main, ["ci", "report", str(reports_dir), "--out", str(output)])

    assert result.exit_code == 0, result.output
    assert "CI report status:" in result.output
    assert "GitHub summary:" in result.output
    assert (output / "github-step-summary.md").exists()


def test_p7_ci_report_cli_json(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    _package(tmp_path, "good", "verified", test_status="passed")
    runner = CliRunner()

    result = runner.invoke(main, ["ci", "report", str(reports_dir), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "passed"
    assert payload["test_matrix_summary"]["passed"] == 1
