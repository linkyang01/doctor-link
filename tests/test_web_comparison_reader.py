from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_comparison_reader import read_web_comparison
from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link comparison", category="web", summary="Comparison sample"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_read_web_comparison_from_package_root(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "report-comparison.json").write_text(
        json.dumps(
            {
                "before_report": "before.json",
                "after_report": "after.json",
                "status": "not_verified",
                "summary": "Comparison summary",
                "resolved_user_assertions": ["fixed assertion"],
                "remaining_user_assertions": ["still open"],
                "new_user_assertions": ["new concern"],
                "evidence_delta": 2,
                "timeline_delta": 1,
                "test_record_delta": 0,
                "notes": ["Needs review"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (package_dir / "report-comparison.md").write_text("# Comparison Markdown", encoding="utf-8")

    comparison = read_web_comparison(package_dir)

    assert comparison.exists is True
    assert comparison.status == "not_verified"
    assert comparison.summary == "Comparison summary"
    assert comparison.before_report == "before.json"
    assert comparison.after_report == "after.json"
    assert comparison.resolved_signals == ["fixed assertion"]
    assert comparison.unresolved_signals == ["still open"]
    assert comparison.new_signals == ["new concern"]
    assert comparison.evidence_delta == 2
    assert comparison.test_record_delta == 0
    assert comparison.markdown == "# Comparison Markdown"


def test_read_web_comparison_from_evidence_test_results(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    target = package_dir / "evidence" / "test-results"
    target.mkdir(parents=True, exist_ok=True)
    (target / "report-comparison.json").write_text(
        json.dumps({"status": "candidate_verified", "resolved_user_assertions": ["done"]}),
        encoding="utf-8",
    )

    comparison = read_web_comparison(package_dir)

    assert comparison.exists is True
    assert comparison.status == "candidate_verified"
    assert comparison.json_path == "evidence/test-results/report-comparison.json"
    assert comparison.resolved_signals == ["done"]


def test_read_web_comparison_missing_and_invalid(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    missing = read_web_comparison(package_dir)
    assert missing.exists is False
    assert missing.status == "missing"

    (package_dir / "report-comparison.json").write_text("not json", encoding="utf-8")
    invalid = read_web_comparison(package_dir)
    assert invalid.exists is True
    assert invalid.status == "invalid_json"
    assert invalid.error


def test_detail_renderer_uses_structured_comparison(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "report-comparison.json").write_text(
        json.dumps(
            {
                "status": "not_verified",
                "summary": "Structured comparison",
                "resolved_user_assertions": ["resolved A"],
                "remaining_user_assertions": ["remaining B"],
                "new_user_assertions": ["new C"],
                "changed_signals": ["changed D"],
                "evidence_delta": 3,
                "test_record_delta": 1,
                "notes": ["Check manually"],
            }
        ),
        encoding="utf-8",
    )

    html = render_package_detail_html(read_package_view(package_dir))

    assert "Before / After Comparison" in html
    assert "Structured comparison" in html
    assert "Resolved Signals" in html
    assert "resolved A" in html
    assert "Unresolved Signals" in html
    assert "remaining B" in html
    assert "New Signals" in html
    assert "new C" in html
    assert "Changed Signals" in html
    assert "changed D" in html
    assert "Test record delta" in html
