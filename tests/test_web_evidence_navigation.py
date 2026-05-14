from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link evidence", category="web", summary="Evidence navigation sample"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_evidence_cards_have_stable_anchors_and_id_links(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    log_path = package_dir / "evidence" / "logs" / "app.log"
    log_path.write_text("sample log", encoding="utf-8")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [
        {
            "evidence_id": "ev-log-1",
            "path": "evidence/logs/app.log",
            "type": "log",
        }
    ]
    report["timeline"] = [
        {
            "title": "Open log evidence",
            "status": "unknown",
            "evidence_id": "ev-log-1",
            "path": "evidence/logs/app.log",
        }
    ]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")

    html = render_package_detail_html(read_package_view(package_dir))

    assert 'id="evidence-evidence-logs-app-log"' in html
    assert 'id="evidence-id-ev-log-1"' in html
    assert 'href="#evidence-evidence-logs-app-log"' in html
    assert "ev-log-1" in html
    assert "evidence/logs/app.log" in html


def test_verification_and_ai_task_link_to_evidence(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    output_path = package_dir / "evidence" / "command-output" / "cmd.json"
    output_path.write_text('{"ok": true}', encoding="utf-8")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [
        {
            "id": "cmd-1",
            "path": "evidence/command-output/cmd.json",
        }
    ]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "missing_evidence",
                "missing_evidence": ["cmd-1"],
                "tests_to_rerun": ["check evidence/command-output/cmd.json"],
                "next_commands": ["doctor-link verify package"],
            }
        ),
        encoding="utf-8",
    )
    (package_dir / "ai-task.md").write_text("Review cmd-1 before changing code.", encoding="utf-8")

    html = render_package_detail_html(read_package_view(package_dir))

    assert 'id="evidence-evidence-command-output-cmd-json"' in html
    assert 'href="#evidence-evidence-command-output-cmd-json"' in html
    assert "Review" in html
    assert "cmd-1" in html


def test_unsupported_evidence_is_listed_not_embedded(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    binary_path = package_dir / "evidence" / "attachments" / "sample.bin"
    binary_path.write_bytes(b"\x00\x01\x02")

    html = render_package_detail_html(read_package_view(package_dir))

    assert "evidence/attachments/sample.bin" in html
    assert "binary_or_unsupported" in html
    assert "Preview disabled" in html
