from __future__ import annotations

from pathlib import Path

from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.web_server import build_web_view


def test_package_view_handles_missing_files_and_empty_evidence(tmp_path: Path) -> None:
    package_dir = tmp_path / "DoctorReports" / "minimal-package"
    package_dir.mkdir(parents=True)
    (package_dir / "doctor-report.json").write_text('{"project":"Minimal"}', encoding="utf-8")
    (package_dir / "user-assertions.json").write_text("[]", encoding="utf-8")

    view = read_package_view(package_dir)
    html = render_package_detail_html(view)

    assert view.warnings
    assert "No evidence files found" in html
    assert "Missing ai-task.md" in html


def test_package_view_handles_json_parse_error(tmp_path: Path) -> None:
    package_dir = tmp_path / "DoctorReports" / "json-error-package"
    package_dir.mkdir(parents=True)
    (package_dir / "summary.md").write_text("JSON parse package", encoding="utf-8")
    (package_dir / "timeline.md").write_text("No steps", encoding="utf-8")
    (package_dir / "evidence-list.md").write_text("No evidence", encoding="utf-8")
    (package_dir / "ai-task.md").write_text("Task", encoding="utf-8")
    (package_dir / "doctor-report.json").write_text("not-json", encoding="utf-8")
    (package_dir / "user-assertions.json").write_text("[]", encoding="utf-8")

    view = read_package_view(package_dir)
    html = render_package_detail_html(view)

    assert any("Invalid JSON file" in warning for warning in view.warnings)
    assert "Invalid JSON file" in html


def test_build_web_view_for_minimal_package(tmp_path: Path) -> None:
    package_dir = tmp_path / "DoctorReports" / "minimal-view-package"
    package_dir.mkdir(parents=True)
    (package_dir / "doctor-report.json").write_text('{"project":"Minimal"}', encoding="utf-8")
    (package_dir / "user-assertions.json").write_text("[]", encoding="utf-8")

    built = build_web_view(package_dir)

    assert Path(built.index_path).exists()
    assert "Minimal" in Path(built.index_path).read_text(encoding="utf-8")
