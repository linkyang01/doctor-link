from pathlib import Path

from doctor_link.diagnose_summary import build_summary


def diagnose_now(library: Path) -> Path:
    root = library / ".doctor-link"
    files = [p for p in library.rglob("*") if p.is_file() and root not in p.parents]
    root.mkdir(exist_ok=True)
    out = root / "summary.md"
    out.write_text(build_summary(files), encoding="utf-8")
    return out
