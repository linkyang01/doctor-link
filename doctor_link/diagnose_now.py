from __future__ import annotations

from pathlib import Path


def diagnose_now(library: Path) -> tuple[Path, int]:
    root = library / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root / "summary.md"
    summary.write_text("# Doctor link diagnose-now\n", encoding="utf-8")
    count = sum(1 for item in library.rglob("*") if item.is_file())
    return summary, count
