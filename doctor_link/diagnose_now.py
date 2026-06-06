from pathlib import Path


def diagnose_now(library: Path) -> Path:
    files = [p for p in library.rglob("*") if p.is_file()]
    counts: dict[str, int] = {}
    for p in files:
        k = p.suffix[1:] or "no-extension"
        counts[k] = counts.get(k, 0) + 1
    text = "# Doctor link diagnose-now\n\nFiles: " + str(len(files))
    text += "\n\n## Extensions\n"
    for k in sorted(counts):
        text += "- " + k + ": " + str(counts[k]) + "\n"
    text += "\n## Recommendations\n- Add fixture coverage.\n"
    root = library / ".doctor-link"
    root.mkdir(exist_ok=True)
    out = root / "summary.md"
    out.write_text(text, encoding="utf-8")
    return out
