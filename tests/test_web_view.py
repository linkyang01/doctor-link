from __future__ import annotations

from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.web_renderer import render_package_html, write_package_html
from doctor_link.core.web_server import build_web_view


def _build_package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="web", summary="Web view test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_read_package_view_reads_core_sections(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    (package_dir / "evidence" / "logs" / "app.log").write_text("hello", encoding="utf-8")

    view = read_package_view(package_dir)

    assert view.title == package_dir.name
    assert any(section.key == "summary" and section.exists for section in view.sections)
    assert any(section.key == "doctor_report" and section.exists for section in view.json_sections)
    assert "evidence/logs/app.log" in view.evidence_files


def test_render_package_html_contains_diagnostic_sections(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    view = read_package_view(package_dir)

    html = render_package_html(view)

    assert "Doctor link Diagnostic Package Browser" in html
    assert "Summary" in html
    assert "Ai Task" in html
    assert "Doctor Report" in html


def test_write_and_build_web_view(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    view = read_package_view(package_dir)
    output = write_package_html(view, tmp_path / "view" / "index.html")

    assert output.exists()
    assert "Web view test" in output.read_text(encoding="utf-8")

    built = build_web_view(package_dir)
    index_path = Path(built.index_path)
    assert index_path.exists()
    assert index_path.name == "index.html"
    assert Path(built.output_dir).name == ".doctorlink-web"
