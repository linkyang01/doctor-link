from __future__ import annotations

import json
from pathlib import Path

import pytest

from doctor_link.core.ai_handoff import SUPPORTED_TOOLS, build_handoff_package
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Handoff", category="p3", summary="handoff package"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_build_handoff_package_for_each_supported_tool(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    for tool in SUPPORTED_TOOLS:
        result = build_handoff_package(package_dir, tool=tool)
        output_dir = Path(result.output_dir)

        assert output_dir.exists()
        assert Path(result.manifest_path).exists()
        assert Path(result.instruction_path).exists()
        manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
        instruction = Path(result.instruction_path).read_text(encoding="utf-8")
        assert manifest["tool"] == tool
        assert "human_assertion_rule" in manifest
        assert "Do not dismiss user-confirmed problems" in instruction
        assert "Do not claim the fix is complete" in instruction
        assert "ai-task.md" in result.included_files
        assert "ai-context.json" in result.included_files


def test_build_handoff_package_reports_missing_files(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "ai-context.json").unlink()

    result = build_handoff_package(package_dir, tool="generic")

    assert "ai-context.json" in result.missing_files
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert "ai-context.json" in manifest["missing_files"]


def test_build_handoff_rejects_unknown_tool(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)

    with pytest.raises(ValueError) as exc_info:
        build_handoff_package(package_dir, tool="unknown")

    assert "Unsupported handoff tool" in str(exc_info.value)
