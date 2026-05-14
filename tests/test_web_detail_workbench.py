from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_detail_renderer import render_package_detail_html, write_package_detail_html
from doctor_link.core.web_package_reader import read_package_view


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link detail", category="web", summary="Detail workbench sample"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_detail_workbench_renders_core_sections(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "missing_evidence",
                "missing_evidence": ["Need rerun evidence"],
                "tests_to_rerun": ["CLI smoke"],
                "next_commands": ["doctor-link verify package --write-back"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (package_dir / "redaction-report.json").write_text(json.dumps({"total_replacements": 1}), encoding="utf-8")
    (package_dir / "evidence" / "logs" / "app.log").write_text("sample log line", encoding="utf-8")
    (package_dir / "report-comparison.json").write_text(
        json.dumps({"status": "not_verified", "unresolved_signals": ["signal"]}),
        encoding="utf-8",
    )

    view = read_package_view(package_dir)
    html = render_package_detail_html(view)

    assert "Doctor link Diagnostic Package Workbench" in html
    assert "Overview" in html
    assert "Timeline" in html
    assert "Evidence" in html
    assert "User Assertions" in html
    assert "Verification Workbench" in html
    assert "Before / After Comparison" in html
    assert "Redaction" in html
    assert "Manifest / Export" in html
    assert "Need rerun evidence" in html
    assert "evidence/logs/app.log" in html


def test_detail_workbench_writes_html(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    view = read_package_view(package_dir)
    output = write_package_detail_html(view, tmp_path / "detail" / "index.html")

    assert output.exists()
    assert "Detail workbench sample" in output.read_text(encoding="utf-8")
