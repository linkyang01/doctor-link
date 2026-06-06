from pathlib import Path

from doctor_link.core.scanner import scan_library


def diagnose_now(library: Path) -> Path:
    scan = scan_library(library)
    root = scan.root / ".doctor-link"
    root.mkdir(exist_ok=True)
    p = root / "summary.md"
    text = f"# Doctor link diagnose-now\n\nFiles: {len(scan.files)}\n\n## Recommendations\n- Add fixture coverage.\n