from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.test_recorder import record_test_result
from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="P2+", category="web", summary="Workbench enhancements"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_workbench_shows_evidence_reverse_references_and_verification_reasons(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    log_path = package_dir / "evidence" / "logs" / "app.log"
    log_path.write_text("hello", encoding="utf-8")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [{"evidence_id": "ev-1", "path": "evidence/logs/app.log"}]
    report["timeline"] = [{"title": "read log", "evidence_id": "ev-1"}]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "missing_evidence",
                "missing_evidence": ["ev-1"],
                "tests_to_rerun": ["rerun log test"],
                "next_commands": ["doctor-link verify package"],
            }
        ),
        encoding="utf-8",
    )

    html = render_package_detail_html(read_package_view(package_dir))

    assert "Referenced by:" in html
    assert "timeline 1" in html
    assert "verification 1" in html
    assert "Verification Status Reasons" in html
    assert "missing evidence" in html
    assert "Suggested Next Commands" in html
    assert "doctor-link verify package" in html
    assert "Back to index" in html


def test_workbench_shows_ai_handoff_blocks_and_test_statuses(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    record = record_test_result(
        package_dir,
        name="handoff test",
        status="failed",
        related_assertion_ids=["assertion-1"],
    )
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "missing_evidence",
                "assertion_test_coverage": [
                    {
                        "assertion_id": "assertion-1",
                        "statement": "Needs handoff",
                        "status": "covered",
                        "covered_by_test_records": [record.test_id],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html = render_package_detail_html(read_package_view(package_dir))

    assert "AI Handoff Blocks" in html
    assert "Task Block" in html
    assert "Boundary Block" in html
    assert "Verification Checklist Block" in html
    assert f"{record.test_id} (failed)" in html
