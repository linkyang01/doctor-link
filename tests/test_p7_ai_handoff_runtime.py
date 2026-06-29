from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.cli import main
from doctor_link.core.ai_handoff import (
    SUPPORTED_TOOLS,
    add_ai_result,
    add_history_round,
    build_handoff_package,
    check_handoff_compatibility,
    get_handoff_profile,
)
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="P7.3", category="handoff", summary="AI handoff runtime"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_p7_profiles_include_all_target_tools() -> None:
    assert "claude-code" in SUPPORTED_TOOLS
    for tool in [
        "codex",
        "cursor",
        "continue",
        "aider",
        "openhands",
        "claude-code",
        "grok",
        "windsurf",
        "cline",
        "generic",
    ]:
        profile = get_handoff_profile(tool)
        assert profile.tool == tool
        assert profile.display_name
        assert profile.instruction_file.endswith(".md")
        assert profile.required_files
        assert profile.max_recommended_files > 0


def test_p7_handoff_writes_tool_specific_manifest_and_compatibility(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "verification-result.json").write_text(
        json.dumps({"status": "missing_evidence", "missing_evidence": ["ev-missing"], "tests_to_rerun": ["pytest"]}),
        encoding="utf-8",
    )
    (package_dir / "evidence" / "logs" / "app.log").write_text("token=abc123", encoding="utf-8")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [{"evidence_id": "ev-1", "path": "evidence/logs/app.log"}]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")

    result = build_handoff_package(package_dir, tool="claude-code")

    output = Path(result.output_dir)
    assert (output / "CLAUDE_CODE_TASK.md").exists()
    assert (output / "handoff-compatibility.json").exists()
    assert result.compatibility_path is not None
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["tool"] == "claude-code"
    assert manifest["compatibility_status"] == "needs_review"
    assert any("ev-missing" in item for item in manifest["missing_evidence_warnings"])
    assert any("possible_secret" in item for item in manifest["privacy_warnings"])
    instruction = Path(result.instruction_path).read_text(encoding="utf-8")
    assert "Doctor link Handoff for Claude Code" in instruction
    assert "Privacy warnings" in instruction
    assert "Missing evidence warnings" in instruction
    assert "Do not dismiss user-confirmed problems" in instruction


def test_p7_grok_handoff_writes_tool_specific_instruction(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    result = build_handoff_package(package_dir, tool="grok")

    output = Path(result.output_dir)
    assert (output / "GROK_TASK.md").exists()
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["tool"] == "grok"
    assert manifest["display_name"] == "Grok Build"
    instruction = Path(result.instruction_path).read_text(encoding="utf-8")
    assert "Doctor link Handoff for Grok Build" in instruction


def test_p7_handoff_enforces_file_inclusion_policy(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    binary = package_dir / "evidence" / "attachments" / "screen.png"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_bytes(b"fake png")
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["evidence"] = [{"evidence_id": "ev-bin", "path": "evidence/attachments/screen.png"}]
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")

    result = build_handoff_package(package_dir, tool="codex")
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))

    assert "evidence/attachments/screen.png" not in result.included_files
    assert any(item["path"] == "evidence/attachments/screen.png" for item in manifest["skipped_files"])


def test_p7_compatibility_blocks_missing_required_files(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "ai-task.md").unlink()

    report = check_handoff_compatibility(package_dir, tool="aider")

    assert report.status == "blocked_missing_required_files"
    assert "ai-task.md" in report.required_missing


def test_p7_repair_session_tracks_ai_results_and_history(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    result = add_ai_result(
        package_dir,
        summary="patched parser",
        claimed_fix="parser branch fixed",
        files_changed=["doctor_link/parser.py"],
        evidence_used=["ev-1"],
        related_assertion_ids=["assertion-1"],
        verification_steps=["pytest"],
        repair_session_id="repair_session_custom",
        tool="codex",
    )
    history = add_history_round(
        package_dir,
        ai_pass="pass 2",
        user_correction="still wrong on edge case",
        evidence_added=["ev-2"],
        verification_attempt="pytest failed",
        repair_session_id="repair_session_custom",
        tool="codex",
    )

    assert result["repair_session_id"] == "repair_session_custom"
    assert history["repair_session_id"] == "repair_session_custom"
    sessions = json.loads((package_dir / "ai-repair-sessions.json").read_text(encoding="utf-8"))
    assert sessions[0]["repair_session_id"] == "repair_session_custom"
    assert result["result_id"] in sessions[0]["ai_result_ids"]
    assert history["round_id"] in sessions[0]["history_round_ids"]
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert "ai_repair_sessions" in report


def test_p7_cli_supports_tool_and_repair_session_options(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    handoff = runner.invoke(main, ["handoff", str(package_dir), "--tool", "claude-code"])
    assert handoff.exit_code == 0, handoff.output
    assert "Compatibility:" in handoff.output
    assert (package_dir / "ai-handoff" / "claude-code" / "CLAUDE_CODE_TASK.md").exists()

    ai = runner.invoke(
        main,
        [
            "ai-result",
            str(package_dir),
            "--summary",
            "patched",
            "--repair-session-id",
            "repair_session_cli",
            "--tool",
            "claude-code",
        ],
    )
    assert ai.exit_code == 0, ai.output
    assert "repair_session_cli" in ai.output

    history = runner.invoke(
        main,
        [
            "diagnosis-history",
            str(package_dir),
            "--ai-pass",
            "second pass",
            "--repair-session-id",
            "repair_session_cli",
            "--tool",
            "claude-code",
        ],
    )
    assert history.exit_code == 0, history.output
    assert "repair_session_cli" in history.output
