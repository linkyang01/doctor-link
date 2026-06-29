from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doctor_link.core.models import EvidenceItem, TimelineStep


@dataclass
class ReproductionEntry:
    reproduction_id: str
    title: str
    kind: str = "manual"
    command: str = ""
    description: str = ""
    expected: str = ""
    related_assertion_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReproductionCatalog:
    path: str
    entries: list[ReproductionEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "entries": [entry.to_dict() for entry in self.entries], "warnings": self.warnings}


@dataclass
class ReproductionRunResult:
    reproduction_id: str
    status: str
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    evidence_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def reproduce_path(project_root: Path) -> Path:
    return project_root / ".doctorlink" / "reproduce.yml"


def load_reproduction_catalog(project_root: Path) -> ReproductionCatalog:
    path = reproduce_path(project_root)
    if not path.exists():
        return ReproductionCatalog(path=str(path), warnings=["Missing .doctorlink/reproduce.yml"])
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries_raw = raw.get("reproductions", raw.get("entries", [])) if isinstance(raw, dict) else []
    warnings: list[str] = []
    entries: list[ReproductionEntry] = []
    if not isinstance(entries_raw, list):
        return ReproductionCatalog(path=str(path), warnings=["reproductions must be a list"])
    for index, item in enumerate(entries_raw, start=1):
        if not isinstance(item, dict):
            warnings.append(f"reproductions[{index}] must be a mapping")
            continue
        kind = str(item.get("kind", "manual"))
        if kind not in {"manual", "command", "test"}:
            warnings.append(f"{item.get('id', index)} uses unknown kind {kind}; treating as manual")
            kind = "manual"
        command_value = item.get("command") or ""
        if isinstance(command_value, list):
            command_text = " && ".join(str(part) for part in command_value)
        else:
            command_text = str(command_value)
        entries.append(
            ReproductionEntry(
                reproduction_id=str(item.get("id") or item.get("reproduction_id") or f"repro-{index}"),
                title=str(item.get("title") or item.get("name") or f"Reproduction {index}"),
                kind=kind,
                command=command_text,
                description=str(item.get("description") or ""),
                expected=str(item.get("expected") or ""),
                related_assertion_ids=[str(value) for value in item.get("related_assertion_ids", []) or []],
            )
        )
    return ReproductionCatalog(path=str(path), entries=entries, warnings=warnings)


def find_reproduction_entry(catalog: ReproductionCatalog, reproduction_id: str) -> ReproductionEntry:
    for entry in catalog.entries:
        if entry.reproduction_id == reproduction_id:
            return entry
    raise ValueError(f"Unknown reproduction id: {reproduction_id}")


def run_reproduction(project_root: Path, reproduction_id: str, package_dir: Path | None = None, timeout_seconds: int = 60) -> ReproductionRunResult:
    catalog = load_reproduction_catalog(project_root)
    entry = find_reproduction_entry(catalog, reproduction_id)
    if entry.kind == "manual":
        result = ReproductionRunResult(reproduction_id=entry.reproduction_id, status="manual")
    elif not entry.command:
        result = ReproductionRunResult(reproduction_id=entry.reproduction_id, status="missing_command")
    else:
        completed = subprocess.run(entry.command, shell=True, cwd=project_root, text=True, capture_output=True, timeout=timeout_seconds, check=False)
        result = ReproductionRunResult(
            reproduction_id=entry.reproduction_id,
            status="passed" if completed.returncode == 0 else "failed",
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    if package_dir is not None:
        result.evidence_id = write_reproduction_evidence(package_dir, entry, result)
    return result


def write_reproduction_evidence(package_dir: Path, entry: ReproductionEntry, result: ReproductionRunResult) -> str:
    evidence_dir = package_dir / "evidence" / "reproductions"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_id = f"reproduction-{entry.reproduction_id}"
    output_path = evidence_dir / f"{entry.reproduction_id}.json"
    relative_path = str(output_path.relative_to(package_dir))
    output_path.write_text(json.dumps({"entry": entry.to_dict(), "result": result.to_dict()}, ensure_ascii=False, indent=2), encoding="utf-8")
    evidence = EvidenceItem(evidence_id=evidence_id, kind="reproduction", title=f"Reproduction {entry.reproduction_id}", source="doctor-link reproduce", path=relative_path, content=f"Status: {result.status}")
    _append_evidence(package_dir, evidence)
    step = TimelineStep(step_id=evidence_id, action="run_reproduction", target=entry.reproduction_id, actual_result=f"Status: {result.status}", status=result.status, evidence_ids=[evidence_id])
    _append_timeline(package_dir, step)
    return evidence_id


def default_reproduce_yaml() -> str:
    return """reproductions:
  - id: repro-help
    title: CLI help should run
    kind: command
    command: doctor-link --help
    expected: Command exits successfully
  - id: repro-manual
    title: Manual reproduction placeholder
    kind: manual
    description: Describe manual steps here
"""


def _append_evidence(package_dir: Path, item: EvidenceItem) -> None:
    path = package_dir / "evidence-list.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Evidence List\n\n"
    path.write_text(existing.rstrip() + f"\n- `{item.evidence_id}` ({item.kind}): {item.title} — {item.path}\n", encoding="utf-8")


def _append_timeline(package_dir: Path, step: TimelineStep) -> None:
    path = package_dir / "timeline.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Timeline\n\n"
    label = step.target or step.step_id
    path.write_text(existing.rstrip() + f"\n- `{step.step_id}` Run reproduction {label}: {step.actual_result}\n", encoding="utf-8")
