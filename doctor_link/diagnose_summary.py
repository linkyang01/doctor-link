from pathlib import Path


def build_summary(files: list[Path]) -> str:
    counts: dict[str, int] = {}
    for p in files:
        key = p.suffix.lstrip(".") or "none"
        counts[key] = counts.get(key, 0) + 1
    lines = ["# Doctor link diagnose-now", "", "Files: " + str(len(files)), "", "## Extensions"]
    lines += ["- " + key + ": " + str(counts[key]) for key in sorted(counts)]
    lines += ["", "## Recommendations", "- Add fixture coverage."]
    return chr