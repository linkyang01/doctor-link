from __future__ import annotations

from pathlib import Path

from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan


def diagnose_now(library: Path) -> Path:
    scan = scan_library(library)
    plan = generate_test_plan(scan)
    root = scan.root / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root / "summary.md"
    lines = ["# Doctor link diagnose-now", "", f"Files: {len(scan.files)}", "", "## Extensions"]
    for key, value in sorted(plan.detected_extensions.items()):
        lines.append(f"- {key}: {value}")
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary
