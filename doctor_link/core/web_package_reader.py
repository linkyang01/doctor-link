from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


TEXT_FILES = {
    "summary": "summary.md",
    "problem_map": "problem-map.md",
    "timeline": "timeline.md",
    "evidence_list": "evidence-list.md",
    "ai_task": "ai-task.md",
    "investigation_boundary": "investigation-boundary.md",
    "verification_checklist": "fix-verification-checklist.md",
    "verification_plan": "verification-plan.md",
    "redaction_report": "redaction-report.md",
    "package_readme": "package-readme.md",
    "report_comparison": "report-comparison.md",
}

JSON_FILES = {
    "doctor_report": "doctor-report.json",
    "ai_context": "ai-context.json",
    "user_assertions": "user-assertions.json",
    "verification_result": "verification-result.json",
    "manifest": "manifest.json",
    "redaction_report_json": "redaction-report.json",
    "report_comparison_json": "report-comparison.json",
}

PREVIEW_EXTENSIONS = {".txt", ".log", ".json", ".md", ".csv", ".yaml", ".yml"}
MAX_PREVIEW_BYTES = 32_000


@dataclass
class PackageSection:
    key: str
    title: str
    path: str
    exists: bool
    content: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PackageJsonSection:
    key: str
    title: str
    path: str
    exists: bool
    data: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidencePreview:
    path: str
    evidence_type: str
    preview_kind: str
    size_bytes: int
    redaction_status: str = "unknown"
    content: str = ""
    truncated: bool = False
    evidence_ids: list[str] = field(default_factory=list)
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosticPackageView:
    package_dir: str
    title: str
    sections: list[PackageSection] = field(default_factory=list)
    json_sections: list[PackageJsonSection] = field(default_factory=list)
    evidence_files: list[str] = field(default_factory=list)
    evidence_previews: list[EvidencePreview] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_dir": self.package_dir,
            "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
            "json_sections": [section.to_dict() for section in self.json_sections],
            "evidence_files": self.evidence_files,
            "evidence_previews": [preview.to_dict() for preview in self.evidence_previews],
            "warnings": self.warnings,
        }

    def text(self, key: str) -> str:
        section = next((item for item in self.sections if item.key == key), None)
        return section.content if section and section.exists else ""

    def json_data(self, key: str) -> Any:
        section = next((item for item in self.json_sections if item.key == key), None)
        return section.data if section and section.exists and not section.error else None


def read_package_view(package_dir: Path) -> DiagnosticPackageView:
    """Read a Doctor link diagnostic package for local web rendering.

    This function is intentionally read-only. It never writes to the package.
    """
    package_dir = package_dir.resolve()
    if not package_dir.exists() or not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    title = package_dir.name
    sections = [_read_text_section(package_dir, key, path) for key, path in TEXT_FILES.items()]
    json_sections = [_read_json_section(package_dir, key, path) for key, path in JSON_FILES.items()]
    evidence_files = _list_evidence_files(package_dir)
    evidence_previews = _read_evidence_previews(package_dir, json_sections)
    warnings = _warnings(sections, json_sections, evidence_files)

    return DiagnosticPackageView(
        package_dir=str(package_dir),
        title=title,
        sections=sections,
        json_sections=json_sections,
        evidence_files=evidence_files,
        evidence_previews=evidence_previews,
        warnings=warnings,
    )


def _read_text_section(package_dir: Path, key: str, relative_path: str) -> PackageSection:
    path = package_dir / relative_path
    if not path.is_file():
        return PackageSection(key=key, title=_title(key), path=relative_path, exists=False)
    return PackageSection(
        key=key,
        title=_title(key),
        path=relative_path,
        exists=True,
        content=path.read_text(encoding="utf-8", errors="replace"),
    )


def _read_json_section(package_dir: Path, key: str, relative_path: str) -> PackageJsonSection:
    path = package_dir / relative_path
    if not path.is_file():
        return PackageJsonSection(key=key, title=_title(key), path=relative_path, exists=False)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return PackageJsonSection(key=key, title=_title(key), path=relative_path, exists=True, data=data)
    except json.JSONDecodeError as exc:
        return PackageJsonSection(
            key=key,
            title=_title(key),
            path=relative_path,
            exists=True,
            data=None,
            error=str(exc),
        )


def _list_evidence_files(package_dir: Path) -> list[str]:
    evidence_dir = package_dir / "evidence"
    if not evidence_dir.is_dir():
        return []
    files: list[str] = []
    for path in sorted(item for item in evidence_dir.rglob("*") if item.is_file()):
        files.append(str(path.relative_to(package_dir)))
    return files


def _read_evidence_previews(package_dir: Path, json_sections: list[PackageJsonSection]) -> list[EvidencePreview]:
    evidence_dir = package_dir / "evidence"
    if not evidence_dir.is_dir():
        return []
    evidence_id_map = _evidence_id_map(json_sections)
    previews: list[EvidencePreview] = []
    for path in sorted(item for item in evidence_dir.rglob("*") if item.is_file()):
        relative_path = str(path.relative_to(package_dir))
        size = path.stat().st_size
        evidence_type = _evidence_type(relative_path)
        evidence_ids = evidence_id_map.get(relative_path, [])
        redaction_status = _evidence_redaction_status(relative_path, package_dir)
        if path.suffix.lower() not in PREVIEW_EXTENSIONS:
            previews.append(
                EvidencePreview(
                    path=relative_path,
                    evidence_type=evidence_type,
                    preview_kind="binary_or_unsupported",
                    size_bytes=size,
                    redaction_status=redaction_status,
                    evidence_ids=evidence_ids,
                    warning="Preview disabled for unsupported or binary evidence. Open from the package only after reviewing sensitivity.",
                )
            )
            continue
        raw = path.read_bytes()[:MAX_PREVIEW_BYTES + 1]
        truncated = len(raw) > MAX_PREVIEW_BYTES
        content = raw[:MAX_PREVIEW_BYTES].decode("utf-8", errors="replace")
        preview_kind = "json" if path.suffix.lower() == ".json" else "text"
        previews.append(
            EvidencePreview(
                path=relative_path,
                evidence_type=evidence_type,
                preview_kind=preview_kind,
                size_bytes=size,
                redaction_status=redaction_status,
                content=content,
                truncated=truncated,
                evidence_ids=evidence_ids,
            )
        )
    return previews


def _evidence_id_map(json_sections: list[PackageJsonSection]) -> dict[str, list[str]]:
    report = next((item.data for item in json_sections if item.key == "doctor_report" and isinstance(item.data, dict)), {})
    evidence = report.get("evidence", []) if isinstance(report, dict) else []
    mapping: dict[str, list[str]] = {}
    if not isinstance(evidence, list):
        return mapping
    for item in evidence:
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("evidence_id") or item.get("id") or "").strip()
        possible_paths = [item.get("path"), item.get("file"), item.get("relative_path")]
        for possible in possible_paths:
            if not possible:
                continue
            normalized = str(possible).replace("\\", "/")
            if not normalized.startswith("evidence/") and "/evidence/" in normalized:
                normalized = "evidence/" + normalized.split("/evidence/", 1)[1]
            mapping.setdefault(normalized, [])
            if evidence_id and evidence_id not in mapping[normalized]:
                mapping[normalized].append(evidence_id)
    return mapping


def _evidence_type(relative_path: str) -> str:
    parts = relative_path.split("/")
    if len(parts) >= 2 and parts[0] == "evidence":
        return parts[1]
    return "unknown"


def _evidence_redaction_status(relative_path: str, package_dir: Path) -> str:
    if not (package_dir / "redaction-report.md").is_file() and not (package_dir / "redaction-report.json").is_file():
        return "no_redaction_report"
    if relative_path.startswith("evidence/logs/") or relative_path.startswith("evidence/command-output/"):
        return "redaction_report_present"
    return "not_text_redaction_target"


def _warnings(
    sections: list[PackageSection],
    json_sections: list[PackageJsonSection],
    evidence_files: list[str],
) -> list[str]:
    warnings: list[str] = []
    required_text = {"summary", "timeline", "evidence_list", "ai_task"}
    required_json = {"doctor_report", "user_assertions"}
    for section in sections:
        if section.key in required_text and not section.exists:
            warnings.append(f"Missing required package file: {section.path}")
    for section in json_sections:
        if section.key in required_json and not section.exists:
            warnings.append(f"Missing required package file: {section.path}")
        if section.error:
            warnings.append(f"Invalid JSON file: {section.path}: {section.error}")
    if not evidence_files:
        warnings.append("No evidence files found under evidence/.")
    return warnings


def _title(key: str) -> str:
    return key.replace("_", " ").title()
