from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.cli import main
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


def test_handoff_cli_rejects_unknown_tool(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["handoff", str(package_dir), "--tool", "unknown"])

    assert result.exit_code != 0
    assert "Invalid value" in result.output
