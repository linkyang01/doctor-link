from pathlib import Path


def diagnose_now(library: Path) -> Path:
    files = [p for p in library.rglob("*") if p.is_file()]
    root = library / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root / "summary.md"
    text = "# Doctor link diagnose-now\n\nFiles: "
    text += str(len(files))
    text += "\n\n## Extensions\n"
    text += "\n## Recommendations\n- Add fixture coverage.\n"
    summary.write_text(text, encoding="utf-8")
    return summary
