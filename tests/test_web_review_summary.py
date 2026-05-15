from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.test_recorder import record_test_result
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.web_review_summary import (
    build_evidence_reference_summaries,
    test_record_status_map,
    verification_status_reasons,
)


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="P2+", category="web", summary="Review summary"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_build_evidence_reference_summaries(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    log_path = package_dir / "evidence" / "logs" / "app.log"
    log_path.write_text("hello", encoding="utf-8")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [{"evidence_id": "ev-1", "path": "evidence/logs/app.log"}]
    report["timeline"] = [{"title": "log step", "evidence_id": "ev-1"}]
    report["test_records"] = [{"test_id": "test-1", "status": "failed", "evidence_ids": ["ev-1"]}]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")
    (package_dir / "verification-result.json").write_text(
        json.dumps({"status": "missing_evidence", "missing_evidence": ["ev-1"]}),
        encoding="utf-8",
    )

    view = read_package_view(package_dir)
    summaries = build_evidence_reference_summaries(view)
    summary = summaries["evidence/logs/app.log"]

    assert summary.evidence_ids == ["ev-1"]
    assert summary.timeline_refs
    assert summary.test_record_refs
    assert summary.verification_refs == ["verification-result"]


def test_verification_status_reasons_and_test_status_map(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    record = record_test_result(package_dir, name="linked test", status="failed", related_assertion_ids=["assertion-1"])
    (package_dir / "user-assertions.json").write_text(
        json.dumps([{"assertion_id": "assertion-1", "user_statement": "needs coverage"}]),
        encoding="utf-8",
    )
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "missing_evidence",
                "missing_evidence": ["report_comparison"],
                "tests_to_rerun": ["rerun linked test"],
                "report_comparison_status": "unknown",
                "assertion_test_coverage": [
                    {
                        "assertion_id": "assertion-1",
                        "status": "covered",
                        "covered_by_test_records": [record.test_id],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    view = read_package_view(package_dir)
    reasons = verification_status_reasons(view)
    statuses = test_record_status_map(view)

    assert any("missing evidence" in reason for reason in reasons)
    assert any("test" in reason for reason in reasons)
    assert statuses[record.test_id] == "failed"
