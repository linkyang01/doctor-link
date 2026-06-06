from pathlib import Path

from doctor_link.core.scanner import scan_library


def diagnose_now(library: Path) -> Path:
    scan = scan_library(library)
    root = scan.root / ".doctor-link"
    root.mkdir(exist_ok=True)
    p = root / "summary.md"
    text = "# Doctor link diagnose-now\n\n"
    text += "Files: " + str(len(scan.files)) + "