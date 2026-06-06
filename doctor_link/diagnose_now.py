from __future__ import annotations

from pathlib import Path

from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan


def diagnose_now(library: Path) -> tuple[Path, int]:
    scan = scan_library(library)
    plan = generate_test_plan(scan)
    event =