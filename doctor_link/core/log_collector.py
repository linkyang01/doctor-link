from __future__ import annotations

from pathlib import Path
from typing import Iterable


def collect_log_files(patterns: Iterable[str], output_dir: Path, max_bytes: int = 512_000) -> list[Path]:
    """Collect log files matching glob patterns into an evidence directory.

    Large logs are truncated from the end because recent entries are usually the
    most useful for diagnosis.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    collected: list[Path] = []

    for pattern in patterns:
        for source in _expand_pattern(pattern):
            if not source.is_file():
                continue
            target = output_dir / _safe_filename(source)
            data = source.read_bytes()
            if len(data) > max_bytes:
                data = data[-max_bytes:]
            target.write_bytes(data)
            collected.append(target)

    return collected


def _expand_pattern(pattern: str) -> list[Path]:
    expanded = Path(pattern).expanduser()
    if any(ch in pattern for ch in ["*", "?", "["]):
        base = expanded.anchor or "."
        # pathlib does not glob absolute patterns directly in all cases, so use parent glob.
        parent = expanded.parent if str(expanded.parent) else Path(base)
        return list(parent.glob(expanded.name))
    return [expanded]


def _safe_filename(path: Path) -> str:
    return "__".join(part for part in path.parts if part not in {path.anchor, "/"}).replace(" ", "_")
