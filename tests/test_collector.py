from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.collector import collect_into_package
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package


def _build_package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="collect", summary="Collect test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_collect_environment_updates_package(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)

    result = collect_into_package(package_dir, project_root=tmp_path)

    assert len(result.evidence) == 1
    assert result.evidence[0].kind == "environment"
    assert (package_dir / "evidence" / "environment.json").exists()

    payload = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert payload["collections"]
    assert payload["evidence"][-1]["kind"] == "environment"
    assert "Evidence collection" in (package_dir / "summary.md").read_text(encoding="utf-8")
    assert "Newly collected evidence" in (package_dir / "ai-task.md").read_text(encoding="utf-8")


def test_collect_logs_commands_probe_and_attachment(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    log_file = tmp_path / "app.log"
    log_file.write_text("error line", encoding="utf-8")
    attachment = tmp_path / "input.txt"
    attachment.write_text("attachment", encoding="utf-8")
    media_file = tmp_path / "sample.mp4"
    media_file.write_text("not a real media file", encoding="utf-8")

    result = collect_into_package(
        package_dir,
        log_patterns=[str(log_file)],
        commands=["python --version", "missing-command-for-doctor-link-test"],
        probes=[media_file],
        attachments=[attachment],
        ffprobe_binary="missing-ffprobe-for-doctor-link-test",
        note="self test note",
    )

    kinds = [item.kind for item in result.evidence]
    assert "logs" in kinds
    assert kinds.count("command_output") == 2
    assert "media_probe" in kinds
    assert "attachment" in kinds
    assert result.warnings == ["User note: self test note"]

    assert any((package_dir / "evidence" / "logs").iterdir())
    assert (package_dir / "evidence" / "command-output" / "command-1.json").exists()
    assert (package_dir / "evidence" / "command-output" / "command-2.json").exists()
    assert (package_dir / "evidence" / "test-results" / "media-probe-1.json").exists()
    assert any((package_dir / "evidence" / "attachments").iterdir())

    payload = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert payload["collections"][-1]["warnings"] == ["User note: self test note"]
    assert any(step["is_failure_point"] for step in payload["timeline"])


def test_collect_logs_warns_when_no_pattern_matches(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)

    result = collect_into_package(package_dir, log_patterns=[str(tmp_path / "missing.log")])

    assert "No log files matched the provided patterns." in result.warnings
    assert result.evidence[0].kind == "logs"
    assert result.timeline_steps[0].status == "unknown"
