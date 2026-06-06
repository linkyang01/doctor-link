from __future__ import annotations

from pathlib import Path

from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan


def diagnose_now(library: Path) -> Path:
    scan = scan_library(library)
    plan = generate_test_plan(scan)
    root = scan.root / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root