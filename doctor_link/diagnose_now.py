from pathlib import Path


def diagnose_now(library: Path) -> Path:
    files = []
    for p in library.rglob("*"):
        if not p.is_file():
            continue
        if ".doctor-link" in p.relative_to(library).parts:
            continue
        files.append(p)
    counts = {}
    for p in files:
        e = p.suffix[1:] or "no-extension"
        counts