from __future__ import annotations

from pathlib import Path

from doctor_link.core.scanner import scan_library


def diagnose_now(library: Path) -> Path:
    scan = scan_library(library)
    root = scan.root / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root / "summary.md"
    text = f"# Doctor link diagnose-now\n\nFiles: {len(scan.files)}\n"
    summary.write_text(text, encoding="utf-8")
    return summary
