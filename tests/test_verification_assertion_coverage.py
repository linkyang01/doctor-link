from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.test_recorder import record_test_result
from doctor_link.core.verification_runner import run_verification


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link coverage", category="verify", summary="Assertion coverage"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_verification_marks_assertion_covered_by_linked_test_record(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "user-assertions.json").write_text(
        json.dumps(
            [
                {"assertion_id": "assertion-1", "user_statement": "First user confirmed issue"},
                {"assertion_id": "assertion-2", "user_statement": "Second user confirmed issue"},
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    record = record_test_result(
        package_dir=package_dir,
        name="Regression check",
        status="passed",
        related_assertion_ids=["assertion-1"],
    )

    result = run_verification(package_dir)

    coverage = result.assertion_test_coverage
    assert coverage[0]["assertion_id"] == "assertion-1"
    assert coverage[0]["status"] == "covered"
    assert coverage[0]["covered_by_test_records"] == [record.test_id]
    assert coverage[1]["assertion_id"] == "assertion-2"
    assert coverage[1]["status"] == "missing"
    assert "assertion_test_coverage" in result.missing_evidence
    assert any("--assertion-id assertion-2" in command for command in result.next_commands)

    payload = json.loads((package_dir / "verification-result.json").read_text(encoding="utf-8"))
    assert payload["assertion_test_coverage"] == coverage
    plan = (package_dir / "verification-plan.md").read_text(encoding="utf-8")
    assert "Assertion test coverage" in plan
    assert "assertion-1" in plan
    assert record.test_id in plan


def test_verification_write_back_preserves_assertion_coverage(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "user-assertions.json").write_text(
        json.dumps([{"assertion_id": "assertion-a", "user_statement": "Needs linked test"}]),
        encoding="utf-8",
    )
    record = record_test_result(
        package_dir=package_dir,
        name="Assertion check",
        status="passed",
        related_assertion_ids=["assertion-a"],
    )

    result = run_verification(package_dir, write_back=True)

    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    stored = report["verification_result"]["assertion_test_coverage"]
    assert stored == result.assertion_test_coverage
    assert stored[0]["covered_by_test_records"] == [record.test_id]


def test_verification_without_user_assertions_has_no_coverage(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    result = run_verification(package_dir)

    assert result.assertion_test_coverage == []
    assert "assertion_test_coverage" not in result.missing_evidence
