from pathlib import Path


def diagnose_now(library: Path) -> Path:
    root = library / ".doctor-link"
    files = [p for p in library.rglob("*") if p.is_file() and root not in p.parents]
    text = "# Doctor link diagnose-now\n\nFiles: " + str(len(files))
    text += "\n\n## Extensions\n\n## Recommendations\n- Add fixture coverage.\n"
    root.mkdir(exist_ok=True)
    out = root / "summary.md"
    out.write_text(text, encoding="utf-8")
    return out
