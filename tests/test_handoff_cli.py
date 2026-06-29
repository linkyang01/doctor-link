from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.entrypoint import main
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Handoff CLI", category="p3", summary="handoff cli"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_handoff_cli_generates_tool_package(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    output = tmp_path / "handoff-out"
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["handoff", str(package_dir), "--tool", "codex", "--out", str(output)],
    )

    assert result.exit_code == 0, result.output
    assert "Generated AI handoff package" in result.output
    assert (output / "handoff-manifest.json").exists()
    assert (output / "CODEX_TASK.md").exists()
    manifest = json.loads((output / "handoff-manifest.json").read_text(encoding="utf-8"))
    assert manifest["tool"] == "codex"
    assert "ai-task.md" in manifest["included_files"]


def test_handoff_cli_json_output(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["handoff", str(package_dir), "--tool", "grok", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["tool"] == "grok"
    assert payload["manifest_path"]
    assert payload["instruction_path"]


def test_handoff_list_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["handoff", "list"])
    assert result.exit_code == 0, result.output
    assert "grok" in result.output
    assert "windsurf" in result.output
    assert "cline" in result.output


def test_handoff_list_json_output() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["handoff", "list", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    tools = {item["tool"] for item in payload["profiles"]}
    assert "codex" in tools
    assert "grok" in tools


def test_handoff_check_command(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["handoff", "check", str(package_dir), "--tool", "cursor", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["tool"] == "cursor"
    assert "status" in payload


def test_handoff_cli_rejects_unknown_tool(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["handoff", str(package_dir), "--tool", "unknown"])

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_p3_collaboration_cli_commands(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "user-assertions.json").write_text(
        json.dumps([{"assertion_id": "assertion-1", "user_statement": "human issue"}]),
        encoding="utf-8",
    )
    runner = CliRunner()

    ai_result = runner.invoke(
        main,
        [
            "ai-result",
            str(package_dir),
            "--summary",
            "changed parser",
            "--claimed-fix",
            "fixed parser branch",
            "--file",
            "doctor_link/parser.py",
            "--evidence-id",
            "ev-1",
            "--assertion-id",
            "assertion-1",
            "--verification-step",
            "pytest",
            "--risk",
            "parser regression",
            "--assumption",
            "fixture is representative",
        ],
    )
    history = runner.invoke(
        main,
        [
            "diagnosis-history",
            str(package_dir),
            "--ai-pass",
            "pass 1",
            "--user-correction",
            "still wrong",
            "--evidence-id",
            "ev-2",
            "--verification-attempt",
            "pytest failed",
        ],
    )
    compliance = runner.invoke(main, ["assertion-check", str(package_dir)])
    risk = runner.invoke(
        main,
        [
            "risk-review",
            str(package_dir),
            "--file",
            "doctor_link/parser.py",
            "--file",
            "README.md",
            "--boundary",
            "doctor_link/",
        ],
    )

    assert ai_result.exit_code == 0, ai_result.output
    assert history.exit_code == 0, history.output
    assert compliance.exit_code == 0, compliance.output
    assert risk.exit_code == 0, risk.output
    assert "Recorded AI result" in ai_result.output
    assert "Recorded diagnosis round" in history.output
    assert "Assertion compliance status" in compliance.output
    assert "Repair risk level" in risk.output
    assert (package_dir / "ai-repair-result.json").exists()
    assert (package_dir / "diagnosis-history.json").exists()
    assert (package_dir / "assertion-compliance-report.json").exists()
    assert (package_dir / "repair-risk-review.json").exists()
