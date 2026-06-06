from __future__ import annotations

from pathlib import Path

from doctor_link.core.scanner import scan_library


def diagnose_now(library: Path) -> Path:
    scan = scan_library(library)
    root = scan.root / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root / "summary.md"
    lines = [
        "# Doctor link diagnose-now",
        "",
        f"Files: {len(scan.files)}",
