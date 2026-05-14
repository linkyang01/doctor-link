from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.report_comparator import (
    compare_doctor_reports,
    write_report_comparison,
    write_report_comparison_to_package,
)


def _write_report(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_compare_reports_marks_remaining_assertions_not_verified(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    _write_report(
        before,
        {
            "category": "playback_failure",
            "status": "ai_ready",
            "user_assertions": [{"user_statement": "Video has no audio"}],
            "evidence": [{"evidence_id": "evd_before"}],
            "timeline": [{"order": 1}],
            "test_records": [],
        },
    )
    _write_report(
        after,
        {
            "category": "playback_failure",
            "status": "ai_ready",
            "user_assertions": [{"user_statement": "Video has no audio"}],
            "evidence": [{"evidence_id": "evd_before"}, {"evidence_id": "evd_after"}],
            "timeline": [{"order": 1}, {"order": 2}],
            "test_records": [{"name": "rerun"}],
        },
    )

    comparison = compare_doctor_reports(before, after)

    assert comparison.status == "not_verified"
    assert comparison.remaining_user_assertions == ["Video has no audio"]
    assert comparison.evidence_delta == 1
    assert comparison.test_record_delta == 1


def test_compare_reports_marks_resolved_assertions_candidate_verified(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    _write_report(
        before,
        {
            "category": "playback_failure",
            "status": "ai_ready",
            "user_assertions": [{"user_statement": "Subtitle missing"}],
            "evidence": [{"evidence_id": "evd_before"}],
            "timeline": [{"order": 1}],
            "test_records": [],
        },
    )
    _write_report(
        after,
        {
            "category": "playback_fixed_candidate",
            "status": "verification_ready",
            "user_assertions": [],
            "evidence": [{"evidence_id": "evd_before"}, {"evidence_id": "evd_after"}],
            "timeline": [{"order": 1}, {"order": 2}],
            "test_records": [{"name": "rerun subtitle"}],
        },
    )

    comparison = compare_doctor_reports(before, after)

    assert comparison.status == "candidate_verified"
    assert comparison.resolved_user_assertions == ["Subtitle missing"]
    assert comparison.remaining_user_assertions == []
    assert "confirm with recorded test evidence" in " ".join(comparison.notes)


def test_write_report_comparison_outputs_json_and_markdown(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    output = tmp_path / "comparison"
    _write_report(before, {"user_assertions": [], "evidence": [], "timeline": [], "test_records": []})
    _write_report(after, {"user_assertions": [], "evidence": [], "timeline": [], "test_records": []})

    comparison = write_report_comparison(before, after, output)

    assert comparison.status == "needs_review"
    assert (output / "report-comparison.json").exists()
    assert (output / "report-comparison.md").exists()
    assert "Doctor link Report Comparison" in (output / "report-comparison.md").read_text(encoding="utf-8")


def test_write_report_comparison_to_package_adds_verification_evidence(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    _write_report(
        before,
        {
            "category": "playback_failure",
            "status": "ai_ready",
            "user_assertions": [{"user_statement": "Audio missing"}],
            "evidence": [{"evidence_id": "evd_before"}],
            "timeline": [{"order": 1}],
            "test_records": [],
        },
    )

    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="after_fix", summary="After fix report"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None

    after_report = package.root_dir / "doctor-report.json"
    payload = json.loads(after_report.read_text(encoding="utf-8"))
    payload["user_assertions"] = []
    payload["evidence"].append({"evidence_id": "evd_after"})
    payload["test_records"] = [{"name": "rerun audio"}]
    after_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    evidence = write_report_comparison_to_package(before, package.root_dir)

    assert (package.root_dir / "evidence" / "test-results" / "report-comparison.json").exists()
    assert (package.root_dir / "evidence" / "test-results" / "report-comparison.md").exists()

    updated = json.loads(after_report.read_text(encoding="utf-8"))
    assert updated["report_comparison"]["status"] == "candidate_verified"
    assert updated["evidence"][-1]["evidence_id"] == evidence.evidence_id
    assert updated["timeline"][-1]["action"] == "compare_doctor_reports"
    assert "Report comparison verification evidence" in (package.root_dir / "ai-task.md").read_text(encoding="utf-8")
    assert "Report comparison verification" in (package.root_dir / "summary.md").read_text(encoding="utf-8")
