from __future__ import annotations

from pathlib import Path

from doctor_link.core.models import LibraryFile, ScanResult


IGNORED_DIRS = {".git", "__pycache__", ".DS_Store"}


def scan_library(root: Path) -> ScanResult:
    """Scan a directory and return basic file information."""
    root = root.resolve()
    files: list[LibraryFile] = []

    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        try:
            size_bytes = path.stat().st_size
        except OSError:
            size_bytes = -1
        files.append(LibraryFile(path=path, root=root, size_bytes=size_bytes))

    return ScanResult(root=root, files=sorted(files, key=lambda item: item.relative_path))
