from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.project_health import build_project_health, write_project_health
from doctor_link.p4_cli import main


def _package(reports_dir: Path, summary: str) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Health", category="p4", summary=summary),
        reports_dir,
    )
    assert package.root_dir is not None
    return package.root_dir


def test_build_project_health_counts_packages_and_missing_verification(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    package_dir = _package(reports_dir, "health check")
    (package_dir / "user-assertions.json").write_text(
        json.dumps([{"assertion_id": "assertion-1", "user_statement": "still broken"}]),
        encoding="utf-8",
    )

    summary = build_project_health(reports_dir)

    assert summary.package_count == 1
    assert summary.status == "needs_attention"
    assert summary.unresolved_assertions == 1
    assert summary.failed_or_missing_verifications == 1
    assert summary.packages[0]["verification_status"] == "missing"


def test_write_project_health_outputs_json_and_markdown(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    _package(reports_dir, "health output")

    summary = write_project_health(reports_dir)

    assert summary.package_count == 1
    assert (reports_dir / "project-health.json").exists()
    assert (reports_dir / "project-health.md").exists()
    payload = json.loads((reports_dir / "project-health.json").read_text(encoding="utf-8"))
    assert payload["package_count"] == 1
    assert "Project Health Summary" in (reports_dir / "project-health.md").read_text(encoding="utf-8")


def test_health_cli_outputs_json(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    _package(reports_dir, "health cli")
    runner = CliRunner()

    result = runner.invoke(main, ["health", str(reports_dir), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["package_count"] == 1
    assert payload["status"] == "needs_attention"
    assert (reports_dir / "project-health.json").exists()


def test_health_cli_allows_output_directory(tmp_path: Path) -> None:
    reports_dir = tmp_path / "DoctorReports"
    output_dir = tmp_path / "HealthOut"
    _package(reports_dir, "health cli out")
    runner = CliRunner()

    result = runner.invoke(main, ["health", str(reports_dir), "--out", str(output_dir)])

    assert result.exit_code == 0, result.output
    assert "Project health status" in result.output
    assert (output_dir / "project-health.json").exists()
    assert (output_dir / "project-health.md").exists()
