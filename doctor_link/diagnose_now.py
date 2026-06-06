from pathlib import Path


def diagnose_now(library: Path) -> Path:
    files = [p for p in library.rglob("*") if p.is_file()]
    root = library / ".doctor-link"
    root.mkdir(exist_ok=True)
    counts: dict[str, int] = {}
    for p in files:
        key = p.suffix.lstrip(".") or "no-extension"
        counts[key] = counts.get(key, 0) + 1
    lines = ["# Doctor link diagnose-now", "", f"Files: {len(files)}", "", "## Extensions"]
    for key in sorted(counts):
        lines.append(f"- {key