from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan


@dataclass
class CreatedReport:
    package_dir: Path


def create_report(project_folder: Path, out_dir: Path) ->