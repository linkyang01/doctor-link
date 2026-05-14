from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.report_comparator import compare_doctor_reports, write_report_comparison


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
