from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.cli import main
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.test_recorder import create_test_record, record_test_result


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link assertions", category="record", summary="Assertion linked record"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_create_test_record_deduplicates_related_assertions() -> None:
    record = create_test_record(
        name="Regression check",
        status="partial",
        related_assertion_ids=["assertion-1", "assertion-1", " assertion-2 "],
    )

    assert record.related_assertion_ids == ["assertion-1", "assertion-2"]


def test_record_test_result_writes_related_assertions(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    record = record_test_result(
        package_dir=package_dir,
        name="Regression check",
        status="failed",
        expected_behavior="Expected result",
        actual_behavior="Actual result",
        related_assertion_ids=["assertion-1", "assertion-2"],
        user_note="Human confirmation",
        related_file="sample.txt",
    )

    result_path = package_dir / "evidence" / "test-results" / f"{record.test_id}.json"
    result_payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert result_payload["related_assertion_ids"] == ["assertion-1", "assertion-2"]

    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert report["test_records"][-1]["related_assertion_ids"] == ["assertion-1", "assertion-2"]
    assert report["ai_task"]["related_assertion_ids"] == ["assertion-1", "assertion-2"]

    assert "Related user assertions: `assertion-1`, `assertion-2`" in (package_dir / "summary.md").read_text(encoding="utf-8")
    assert "Related user assertions: `assertion-1`, `assertion-2`" in (package_dir / "ai-task.md").read_text(encoding="utf-8")


def test_record_cli_accepts_assertion_ids(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "record",
            str(package_dir),
            "--name",
            "CLI regression",
            "--status",
            "partial",
            "--assertion-id",
            "assertion-a",
            "--assertion-id",
            "assertion-b",
        ],
    )

    assert result.exit_code == 0, result.output
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert report["test_records"][-1]["related_assertion_ids"] == ["assertion-a", "assertion-b"]
