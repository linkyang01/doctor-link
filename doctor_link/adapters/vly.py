from __future__ import annotations

from pathlib import Path

from doctor_link.adapters.base import ProjectAdapter, ProjectContext
from doctor_link.core.diagnosis_strategy import load_diagnosis_strategy
from doctor_link.core.models import EvidenceItem, ScanResult
from doctor_link.core.vly_adapter import (
    VlyCoreProofReport,
    build_vly_core_proof_matrix,
    write_vly_core_proof_to_package,
)


class VlyAdapter(ProjectAdapter):
    """Vly media playback diagnostic adapter.

    Delegates Core Proof matrix generation to ``doctor_link.core.vly_adapter``.
    """

    name = "vly"

    def detect(self, root: Path) -> bool:
        root = root.resolve()
        if root.name.lower() in {"vly", "vlytestlibrary"}:
            return True
        strategy = load_diagnosis_strategy(root).strategy
        if strategy is not None and strategy.project_type == "vly":
            return True
        media_markers = {".mp4", ".mkv", ".mov", ".srt", ".ass", ".vtt"}
        media_count = 0
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in media_markers:
                media_count += 1
                if media_count >= 2:
                    return True
        return False

    def describe(self, root: Path) -> ProjectContext:
        strategy = load_diagnosis_strategy(root).strategy
        display_name = strategy.project if strategy and strategy.project else root.name
        return ProjectContext(name=display_name, root=root.resolve(), kind=self.name)

    def build_core_proof(self, scan_result: ScanResult) -> VlyCoreProofReport:
        return build_vly_core_proof_matrix(scan_result)

    def write_core_proof(self, package_dir: Path, report: VlyCoreProofReport) -> EvidenceItem:
        return write_vly_core_proof_to_package(package_dir, report)