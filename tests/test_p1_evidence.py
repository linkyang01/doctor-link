from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.environment_collector import collect_environment
from doctor_link.core.media_probe import probe_media, summarize_media_probe
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.test_recorder import create_test_record, record_test_result


def test_collect_environment_includes_project_root(tmp_path: Path) -> None:
    payload = collect_environment(tmp_path)

    assert payload["project"]["root"] == str(tmp_path.resolve())
    assert payload["project"]["exists"] is True
    assert "python" in payload
    assert "system" in payload


def test_media_probe_preserves_failed_command_as_evidence(tmp_path: Path) -> None:
    sample = tmp_path / "sample.mp4"
    sample.write_text("not a real media file", encoding="utf-8")

    payload = probe_media(sample, ffprobe_binary="missing-ffprobe-for-test")
    summary = summarize_media_probe(payload)

    assert payload["ok"] is False
    assert payload["command"]["returncode"] == 127
    assert summary["ok"] is False
    assert summary["error"]


def test_create_test_record_rejects_invalid_status() -> None:
    try:
        create_test_record(name="invalid", status="blocked")
    except ValueError as exc:
        assert "passed, failed, partial, unknown" in str(exc)
    else:
        raise AssertionError("invalid status should raise ValueError")


def test_record_test_result_updates_diagnostic_package(tmp_path: Path) -> None:
    event = DiagnosticEvent(project="Doctor link", category="test_recording", summary="Record test result")
    package = build_diagnostic_package(event, tmp_path / "DoctorReports")
    assert package.root_dir is not None

    record = record_test_result(
        package.root_dir,
        name="Playback smoke",
        status="failed",
        expected_behavior="Media plays with video, audio, and subtitles.",
        actual_behavior="Video plays but audio is missing.",
        user_note="User confirms this is a playback problem.",
        related_file="VlyTestLibrary/sample.mkv",
    )

    result_path = package.root_dir / "evidence" / "test-results" / f"{record.test_id}.json"
    assert result_path.exists()

    payload = json.loads((package.root_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert payload["test_records"][0]["name"] == "Playback smoke"
    assert payload["timeline"][-1]["is_failure_point"] is True
    assert payload["evidence"][-1]["kind"] == "test_result"
    assert "Playback smoke" in (package.root_dir / "ai-task.md").read_text(encoding="utf-8")
    assert "Playback smoke" in (package.root_dir / "summary.md").read_text(encoding="utf-8")
