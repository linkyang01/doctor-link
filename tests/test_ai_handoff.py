from __future__ import annotations

import json
from pathlib import Path

import pytest

from doctor_link.core.ai_handoff import (
    SUPPORTED_TOOLS,
    add_ai_result,
    add_history_round,
    build_assertion_compliance,
    build_handoff_package,
    build_risk_review,
    list_handoff_profiles,
)
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Handoff", category="p3", summary="handoff package"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_list_handoff_profiles_covers_supported_tools() -> None:
    profiles = list_handoff_profiles()
    tools = {item["tool"] for item in profiles}
    assert tools == SUPPORTED_TOOLS
    assert any(item["tool"] == "grok" for item in profiles)


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


def test_p3_collaboration_records_write_expected_files(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "user-assertions.json").write_text(
        json.dumps([{"assertion_id": "assertion-1", "user_statement": "human issue"}]),
        encoding="utf-8",
    )

    ai_result = add_ai_result(
        package_dir,
        summary="changed parser",
        claimed_fix="fixed parsing branch",
        files_changed=["doctor_link/parser.py"],
        evidence_used=["ev-1"],
        related_assertion_ids=["assertion-1"],
        verification_steps=["pytest"],
        risks=["parser regression"],
        assumptions=["input fixture is representative"],
    )
    history = add_history_round(package_dir, ai_pass="pass 1", user_correction="still wrong", evidence_added=["ev-2"], verification_attempt="pytest failed")
    compliance = build_assertion_compliance(package_dir)
    risk = build_risk_review(package_dir, files_changed=["doctor_link/parser.py", "README.md"], boundary=["doctor_link/"])

    assert ai_result["result_id"] == "ai_result_001"
    assert history["round_id"] == "round_001"
    assert compliance["status"] == "covered"
    assert risk["risk_level"] == "high"
    assert (package_dir / "ai-repair-result.json").exists()
    assert (package_dir / "ai-repair-result.md").exists()
    assert (package_dir / "diagnosis-history.json").exists()
    assert (package_dir / "diagnosis-history.md").exists()
    assert (package_dir / "assertion-compliance-report.json").exists()
    assert (package_dir / "assertion-compliance-report.md").exists()
    assert (package_dir / "repair-risk-review.json").exists()
    assert (package_dir / "repair-risk-review.md").exists()

    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert "ai_repair_results" in report
    assert "diagnosis_history" in report
    assert "assertion_compliance" in report
    assert "repair_risk_review" in report
