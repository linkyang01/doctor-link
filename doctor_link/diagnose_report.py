from pathlib import Path
from typing import Any


def build_report(files: list[Path]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for path in files:
        key = path.suffix.lstrip(".") or "none"
        counts[key] = counts.get(key, 0) + 1
    return {
        "files": len(files),
        "extensions": dict(sorted(counts.items())),
        "recommendations": _recommendations(counts, files),
    }


def _recommendations(extensions: dict[str, int], files: list[Path]) -> list[str]:
    recommendations: list[str] = []
    if extensions.get("py", 0) > 0:
        recommendations.append("Run `doctor-link report .` to generate a full diagnostic package.")
        recommendations.append("Capture tests with `doctor-link collect <package> --command \"pytest -q\"`.")
    if extensions.get("log", 0) > 0 or any("logs" in path.parts for path in files):
        recommendations.append("Include logs with `doctor-link collect <package> --logs \"logs/*.log\"`.")
    if extensions.get("mp4", 0) or extensions.get("mov", 0) or extensions.get("mkv", 0):
        recommendations.append("Probe media with `doctor-link collect <package> --probe <media-file>`.")
    if extensions.get("js", 0) or extensions.get("ts", 0) or extensions.get("tsx", 0):
        recommendations.append("Collect runtime evidence from your web app logs or browser console.")
    if not recommendations:
        recommendations.append("Run `doctor-link report <folder>` to start a structured diagnosis.")
    if not any("test" in path.parts or path.name.startswith("test_") for path in files):
        recommendations.append("Add fixture coverage or sample tests to improve diagnosis quality.")
    return recommendations