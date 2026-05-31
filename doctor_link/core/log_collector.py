from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from doctor_link.core.models import utc_now_iso


@dataclass
class CollectedLogFile:
    source: str
    target: str | None
    size_bytes: int
    collected_bytes: int = 0
    truncated: bool = False
    skipped: bool = False
    reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LogCollectionResult:
    collected_at: str = field(default_factory=utc_now_iso)
    files: list[CollectedLogFile] = field(default_factory=list)
    manifest_path: str | None = None

    @property
    def collected_paths(self) -> list[Path]:
        return [Path(item.target) for item in self.files if item.target and not item.skipped]

    def to_dict(self) -> dict:
        return {
            "collected_at": self.collected_at,
            "files": [item.to_dict() for item in self.files],
            "manifest_path": self.manifest_path,
        }


def collect_log_files(patterns: Iterable[str], output_dir: Path, max_bytes: int = 512_000) -> list[Path]:
    """Backward-compatible helper returning only collected paths."""
    return collect_log_files_with_manifest(patterns, output_dir, max_bytes=max_bytes).collected_paths


def collect_log_files_with_manifest(patterns: Iterable[str], output_dir: Path, max_bytes: int = 512_000) -> LogCollectionResult:
    """Collect log files with truncation, binary-skip, and manifest metadata.

    Large logs are truncated from the end because recent entries are usually the
    most useful for diagnosis. Binary-looking files are skipped to avoid corrupt
    text evidence and accidental large binary ingestion.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    result = LogCollectionResult()

    for pattern in patterns:
        for source in _expand_pattern(pattern):
            if not source.is_file():
                continue
            try:
                raw = source.read_bytes()
            except OSError as exc:
                result.files.append(CollectedLogFile(source=str(source), target=None, size_bytes=0, skipped=True, reason=f"read_failed: {exc}"))
                continue
            size = len(raw)
            if _looks_binary(raw):
                result.files.append(CollectedLogFile(source=str(source), target=None, size_bytes=size, skipped=True, reason="binary_file"))
                continue
            truncated = size > max_bytes
            data = raw[-max_bytes:] if truncated else raw
            text = data.decode("utf-8", errors="replace")
            target = output_dir / _safe_filename(source)
            target.write_text(text, encoding="utf-8")
            result.files.append(CollectedLogFile(source=str(source), target=str(target), size_bytes=size, collected_bytes=len(text.encode("utf-8")), truncated=truncated))

    manifest_dir = output_dir.parent / "test-results"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_dir / "log-collection-manifest.json"
    result.manifest_path = str(manifest)
    manifest.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def _looks_binary(data: bytes, sample_size: int = 4096) -> bool:
    sample = data[:sample_size]
    return b"\x00" in sample


def _expand_pattern(pattern: str) -> list[Path]:
    expanded = Path(pattern).expanduser()
    if any(ch in pattern for ch in ["*", "?", "["]):
        base = expanded.anchor or "."
        parent = expanded.parent if str(expanded.parent) else Path(base)
        return list(parent.glob(expanded.name))
    return [expanded]


def _safe_filename(path: Path) -> str:
    return "__".join(part for part in path.parts if part not in {path.anchor, "/"}).replace(" ", "_")
