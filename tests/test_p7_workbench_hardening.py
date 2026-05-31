from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.cli import main
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.workbench_writeback import append_workbench_note


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="P7.2", category="workbench", summary="Workbench hardening"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_p7_workbench_renders_collapsible_filters_health_and_writeback_panel(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    log_path = package_dir / "evidence" / "logs" / "app.log"
    log_path.write_text("hello from app", encoding="utf-8")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [{"evidence_id": "ev-1", "path": "evidence/logs/app.log"}]
    report["timeline"] = [{"action": "read log", "status": "failed", "evidence_ids": ["ev-1"]}]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")
    (package_dir / "verification-result.json").write_text(
        json.dumps({"status": "missing_evidence", "missing_evidence": ["ev-1"], "tests_to_rerun": ["rerun"]}),
        encoding="utf-8",
    )

    html = render_package_detail_html(read_package_view(package_dir))

    assert "Project Health" in html
    assert "Controlled Write-back" in html
    assert "Evidence search" in html
    assert "evidence-type-filter" in html
    assert "evidence-visible-count" in html
    assert "Verification state: missing_evidence" in html
    assert "Skip to main content" in html
    assert '<details id="evidence"' in html
    assert 'data-evidence-type="logs"' in html
    assert 'data-search="' in html
    assert 'href="#evidence-id-ev-1"' in html or 'href="#evidence-evidence-logs-app-log"' in html


def test_workbench_writeback_is_disabled_by_default(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    result = append_workbench_note(package_dir, "review note")

    assert result.enabled is False
    assert result.wrote is False
    assert result.warnings
    assert not (package_dir / "workbench-notes.md").exists()
    assert not (package_dir / "workbench-writeback-audit.jsonl").exists()


def test_workbench_writeback_explicit_mode_writes_audit_and_backup(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    first = append_workbench_note(package_dir, "first note", enable_write_back=True)
    second = append_workbench_note(package_dir, "second note", enable_write_back=True)

    assert first.wrote is True
    assert second.wrote is True
    assert second.backup_file is not None
    notes = (package_dir / "workbench-notes.md").read_text(encoding="utf-8")
    assert "first note" in notes
    assert "second note" in notes
    audit = (package_dir / "workbench-writeback-audit.jsonl").read_text(encoding="utf-8")
    assert "append_workbench_note" in audit


def test_workbench_note_cli_requires_enable_writeback(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    dry = runner.invoke(main, ["workbench-note", str(package_dir), "--note", "dry note", "--json"])
    assert dry.exit_code == 0, dry.output
    dry_payload = json.loads(dry.output)
    assert dry_payload["wrote"] is False
    assert not (package_dir / "workbench-notes.md").exists()

    written = runner.invoke(main, ["workbench-note", str(package_dir), "--note", "real note", "--enable-write-back", "--json"])
    assert written.exit_code == 0, written.output
    written_payload = json.loads(written.output)
    assert written_payload["wrote"] is True
    assert (package_dir / "workbench-notes.md").exists()
