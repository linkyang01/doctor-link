from __future__ import annotations

from pathlib import Path

from doctor_link.core.scanner import scan_library
from doctor_link.core.vly_adapter import build_vly_core_proof_matrix


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
