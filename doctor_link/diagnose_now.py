from pathlib import Path

from doctor_link.diagnose_summary import build_summary


def diagnose_now(library: Path, output: Path | None = None) -> Path:
    base = library.resolve()
    root = output.resolve() if output is not None else base / ".doctor-link"
    files = [
        p for p in base.rglob("*")
        if p.is_file() and root not in p.resolve().parents
    ]
    root.mkdir(parents=True, exist_ok=True)
    out = root / "summary.md"
    out.write_text(build_summary(files), encoding="utf-8")
    return out
