from pathlib import Path
from typing import Any


def build_report(files: list[Path]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for p in files:
        key = p.suffix.lstrip(".") or "none"
        counts[key] = counts.get(key, 0) + 1
    return {
        "files": len(files),
        "extensions": dict(sorted(counts.items())),
        "recommendations": ["Add fixture coverage."],
    }
