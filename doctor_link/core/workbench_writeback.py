from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso


@dataclass
class WorkbenchWritebackResult:
    package_dir: str
    enabled: bool
    wrote: bool
    target_file: str | None = None
    backup_file: str | None = None
    audit_file: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def append_workbench_note(
    package_dir: Path,
    note: str,
    section: str = "workbench-notes.md",
    enable_write_back: bool = False,
) -> WorkbenchWritebackResult:
    """Append a local workbench note with explicit opt-in, backup, and audit.

    The function is intentionally disabled by default. It is a controlled local
    write-back primitive for P7.2 and never writes unless enable_write_back=True.
    """
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")
    safe_section = _safe_section_name(section)
    target = package_dir / safe_section
    audit = package_dir / "workbench-writeback-audit.jsonl"
    result = WorkbenchWritebackResult(package_dir=str(package_dir), enabled=enable_write_back, wrote=False, target_file=str(target.relative_to(package_dir)), audit_file=str(audit.relative_to(package_dir)))
    if not enable_write_back:
        result.warnings.append("Write-back disabled. Re-run with explicit enable_write_back=True or CLI --enable-write-back.")
        return result

    target.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if target.exists():
        backup = target.with_suffix(target.suffix + f".{utc_now_iso().replace(':', '-')}.bak")
        shutil.copy2(target, backup)
        result.backup_file = str(backup.relative_to(package_dir))
    entry = f"\n## Workbench note - {utc_now_iso()}\n\n{note.strip()}\n"
    current = target.read_text(encoding="utf-8") if target.exists() else "# Workbench Notes\n"
    target.write_text(current.rstrip() + "\n" + entry.lstrip(), encoding="utf-8")
    audit_record = {
        "timestamp": utc_now_iso(),
        "action": "append_workbench_note",
        "target_file": str(target.relative_to(package_dir)),
        "backup_file": str(backup.relative_to(package_dir)) if backup else None,
        "note_length": len(note),
    }
    with audit.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(audit_record, ensure_ascii=False) + "\n")
    result.wrote = True
    return result


def _safe_section_name(section: str) -> str:
    normalized = section.replace("\\", "/").strip().lstrip("/") or "workbench-notes.md"
    parts = [part for part in normalized.split("/") if part not in {"", ".", ".."}]
    if not parts:
        return "workbench-notes.md"
    safe = "/".join(parts)
    if not safe.endswith(".md"):
        safe += ".md"
    return safe
