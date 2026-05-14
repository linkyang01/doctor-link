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
}

JSON_FILES = {
    "doctor_report": "doctor-report.json",
    "ai_context": "ai-context.json",
    "user_assertions": "user-assertions.json",
    "verification_result": "verification-result.json",
    "manifest": "manifest.json",
    "redaction_report_json": "redaction-report.json",
}


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
class DiagnosticPackageView:
    package_dir: str
    title: str
    sections: list[PackageSection] = field(default_factory=list)
    json_sections: list[PackageJsonSection] = field(default_factory=list)
    evidence_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_dir": self.package_dir,
            "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
            "json_sections": [section.to_dict() for section in self.json_sections],
            "evidence_files": self.evidence_files,
            "warnings": self.warnings,
        }


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
    warnings = _warnings(sections, json_sections, evidence_files)

    return DiagnosticPackageView(
        package_dir=str(package_dir),
        title=title,
        sections=sections,
        json_sections=json_sections,
        evidence_files=evidence_files,
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
