from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.scanner import scan_library
from doctor_link.core.vly_adapter import build_vly_core_proof_matrix, write_vly_core_proof_to_package


def test_vly_core_proof_returns_no_go_when_required_samples_missing(tmp_path: Path) -> None:
    (tmp_path / "sample.mp4").write_text("placeholder", encoding="utf-8")

    report = build_vly_core_proof_matrix(scan_library(tmp_path))

    assert report.go_no_go == "NO-GO"
    missing = {case.case_id for case in report.cases if case.status == "missing" and case.required}
    assert "external_subtitle" in missing
    assert "audio_track_sample" in missing


def test_vly_core_proof_returns_go_when_required_samples_exist(tmp_path: Path) -> None:
    (tmp_path / "basic.mp4").write_text("placeholder", encoding="utf-8")
    (tmp_path / "complex.mkv").write_text("placeholder", encoding="utf-8")
    (tmp_path / "subtitle.srt").write_text("placeholder", encoding="utf-8")
    (tmp_path / "audio.dts").write_text("placeholder", encoding="utf-8")

    report = build_vly_core_proof_matrix(scan_library(tmp_path))

    assert report.go_no_go == "GO"
    required_cases = [case for case in report.cases if case.required]
    assert all(case.status == "ready" for case in required_cases)
    assert "Vly Core Proof Report" in report.to_markdown()


def test_write_vly_core_proof_to_package_adds_evidence_and_ai_context(tmp_path: Path) -> None:
    library = tmp_path / "VlyTestLibrary"
    library.mkdir()
    (library / "basic.mp4").write_text("placeholder", encoding="utf-8")

    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="vly_readiness", summary="Vly proof readiness"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None

    report = build_vly_core_proof_matrix(scan_library(library))
    evidence = write_vly_core_proof_to_package(package.root_dir, report)

    assert (package.root_dir / "evidence" / "test-results" / "vly-core-proof.json").exists()
    assert (package.root_dir / "evidence" / "test-results" / "vly-core-proof.md").exists()

    payload = json.loads((package.root_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert payload["vly_core_proof"]["go_no_go"] == "NO-GO"
    assert payload["evidence"][-1]["evidence_id"] == evidence.evidence_id
    assert payload["timeline"][-1]["action"] == "vly_core_proof"
    assert payload["timeline"][-1]["is_failure_point"] is True
    assert "Vly Core Proof readiness evidence" in (package.root_dir / "ai-task.md").read_text(encoding="utf-8")
    assert "Vly Core Proof readiness" in (package.root_dir / "summary.md").read_text(encoding="utf-8")
