from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso

PROJECT_MARKERS = [
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Dockerfile",
    "docker-compose.yml",
]

TOOL_NAMES = ["git", "python", "python3", "pip", "pip3", "node", "npm", "pnpm", "yarn", "pytest", "ruff"]


def collect_environment(project_root: Path | None = None) -> dict[str, Any]:
    """Collect local environment information for a diagnostic package.

    P7.1 adds tool availability and project structure hints while keeping the
    collector local-only and read-only.
    """
    payload: dict[str, Any] = {
        "collected_at": utc_now_iso(),
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": sys.version,
            "version_info": list(sys.version_info[:3]),
            "executable": sys.executable,
            "implementation": platform.python_implementation(),
        },
        "process": {
            "cwd": os.getcwd(),
            "pid": os.getpid(),
        },
        "tools": _collect_tool_paths(),
    }

    if project_root is not None:
        root = project_root.resolve()
        payload["project"] = {
            "root": str(root),
            "exists": root.exists(),
            "is_git_repo": (root / ".git").exists(),
            "markers": _collect_project_markers(root),
            "top_level_entries": _collect_top_level_entries(root),
        }

    return payload


def _collect_tool_paths() -> dict[str, Any]:
    return {name: {"available": shutil.which(name) is not None, "path": shutil.which(name)} for name in TOOL_NAMES}


def _collect_project_markers(root: Path) -> dict[str, bool]:
    if not root.exists():
        return {name: False for name in PROJECT_MARKERS}
    return {name: (root / name).exists() for name in PROJECT_MARKERS}


def _collect_top_level_entries(root: Path, limit: int = 50) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    entries: list[dict[str, Any]] = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name.lower())[:limit]:
        try:
            stat = entry.stat()
        except OSError:
            entries.append({"name": entry.name, "kind": "unknown", "error": "stat_failed"})
            continue
        entries.append({
            "name": entry.name,
            "kind": "directory" if entry.is_dir() else "file",
            "size_bytes": stat.st_size if entry.is_file() else None,
        })
    return entries
