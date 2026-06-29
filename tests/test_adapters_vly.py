from __future__ import annotations

from pathlib import Path

from doctor_link.adapters.registry import detect_adapter, resolve_adapter_name
from doctor_link.adapters.vly import VlyAdapter
from doctor_link.core.scanner import scan_library


def test_vly_adapter_detects_project_type(tmp_path: Path) -> None:
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "diagnosis.yml").write_text("project_type: vly\n", encoding="utf-8")
    adapter = detect_adapter(tmp_path)
    assert isinstance(adapter, VlyAdapter)


def test_vly_adapter_detects_media_samples(tmp_path: Path) -> None:
    (tmp_path / "clip.mp4").write_text("x", encoding="utf-8")
    (tmp_path / "track.srt").write_text("subtitle", encoding="utf-8")
    adapter = detect_adapter(tmp_path)
    assert isinstance(adapter, VlyAdapter)


def test_vly_adapter_build_core_proof_delegates(tmp_path: Path) -> None:
    (tmp_path / "clip.mp4").write_text("x", encoding="utf-8")
    adapter = VlyAdapter()
    report = adapter.build_core_proof(scan_library(tmp_path))
    assert report.go_no_go in {"GO", "NO-GO"}


def test_resolve_adapter_name_uses_detection(tmp_path: Path) -> None:
    (tmp_path / "clip.mp4").write_text("x", encoding="utf-8")
    (tmp_path / "track.srt").write_text("subtitle", encoding="utf-8")
    assert resolve_adapter_name(tmp_path) == "vly"