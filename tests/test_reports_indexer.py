from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.reports_indexer import filter_packages, index_reports
from doctor_link.core.web_renderer import render_reports_index_html
from doctor_link.core.web_server import build_reports_index_view, build_web_view


def _build_package(root: Path, summary: str) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="index", summary=summary),
        root,
    )
    assert package.root_dir is not None
    return package.root_dir


def test_index_reports_extracts_package_status_counts_and_warnings(tmp_path: Path) -> None:
    reports_root = tmp_path / "DoctorReports"
    first = _build_package(reports_root, "First issue")
    second = _build_package(reports_root, "Second issue")

    (first / "verification-result.json").write_text(
        json.dumps({"status": "candidate_verified"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (first / "redaction-report.json").write_text(
        json.dumps({"total_replacements": 2}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (first / "user-assertions.json").write_text(
        json.dumps([{"user_statement": "User confirmed issue signal"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (second / "verification-result.json").write_text(
        json.dumps({"status": "missing_evidence"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    index = index_reports(reports_root)

    assert index.total_packages == 2
    first_item = next(item for item in index.packages if item.summary == "First issue")
    assert first_item.verification_status == "candidate_verified"
    assert first_item.redaction_status == "redacted"
    assert first_item.user_assertion_count == 1

    second_item = next(item for item in index.packages if item.summary == "Second issue")
    assert second_item.verification_status == "missing_evidence"
    assert second_item.redaction_status == "missing"
    assert second_item.warning_count >= 1


def test_filter_packages_by_verification_assertions_and_redaction(tmp_path: Path) -> None:
    reports_root = tmp_path / "DoctorReports"
    first = _build_package(reports_root, "Verified issue")
    second = _build_package(reports_root, "Blocked issue")
    (first / "verification-result.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")
    (first / "redaction-report.json").write_text(json.dumps({"total_replacements": 0}), encoding="utf-8")
    (second / "verification-result.json").write_text(json.dumps({"status": "not_verified"}), encoding="utf-8")
    (second / "user-assertions.json").write_text(json.dumps([{"user_statement": "Confirmed issue signal"}]), encoding="utf-8")

    index = index_reports(reports_root)

    assert [item.summary for item in filter_packages(index, verification_status="ready")] == ["Verified issue"]
    assert [item.summary for item in filter_packages(index, has_user_assertions=True)] == ["Blocked issue"]
    assert [item.summary for item in filter_packages(index, has_redaction_warning=True)] == ["Blocked issue"]


def test_render_reports_index_html_and_build_reports_view(tmp_path: Path) -> None:
    reports_root = tmp_path / "DoctorReports"
    package_dir = _build_package(reports_root, "Index render issue")
    (package_dir / "redaction-report.json").write_text(json.dumps({"total_replacements": 0}), encoding="utf-8")

    index = index_reports(reports_root)
    html = render_reports_index_html(index)

    assert "Doctor link Diagnostic Workbench" in html
    assert "Index render issue" in html
    assert "Status Filters" in html

    built = build_reports_index_view(reports_root)
    index_path = Path(built.index_path)
    assert index_path.exists()
    assert "Index render issue" in index_path.read_text(encoding="utf-8")
    assert (Path(built.output_dir) / "packages" / package_dir.name / "index.html").exists()

    built_auto = build_web_view(reports_root)
    assert Path(built_auto.index_path).exists()
