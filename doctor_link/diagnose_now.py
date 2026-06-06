from pathlib import Path


def diagnose_now(library: Path) -> Path:
    root = library / ".doctor-link"
    fs = [p for p in library.rglob("*") if p.is_file() and root not in p.parents]
    cs = {}
    for p in fs:
        e = p.suffix[1:] or "no-extension"
        cs[e] = cs.get(e, 0) + 1
    text = "# Doctor link diagnose-now\n\nFiles: " + str(len(fs))
    text += "\n\n## Extensions\n"
    for e