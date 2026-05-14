from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_PACKAGE_FILES = [
    "summary.md",
    "timeline.md",
    "evidence-list.md",
    "doctor-report.json",
    "ai-task.md",
    "user-assertions.json",
]


@dataclass
class DiagnosticPackageIndexItem:
    name: str
    path: str
    relative_path: str
    project: str = "Unknown project"
    summary: str = "No summary available."
    created_at: str | None = None
    updated_at: str | None = None
    evidence_count: int = 0
    timeline_count: int = 0
    user_assertion_count: int = 0
    verification_status: str = "unknown"
    redaction_status: str = "missing"
    package_export_status: str = "not_exported"
    warning_count: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosticReportsIndex:
    reports_root: str
    generated_at: str
    packages: list[DiagnosticPackageIndexItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_packages(self) -> int:
        return len(self.packages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reports_root": self.reports_root,
            "generated_at": self.generated_at,
            "total_packages": self.total_packages,
            "packages": [package.to_dict() for package in self.packages],
            "warnings": self.warnings,
        }


def index_reports(reports_root: Path) -> DiagnosticReportsIndex:
    """Index a DoctorReports directory without modifying package contents."""
    reports_root = reports_root.resolve()
    warnings: list[str] = []
    if not reports_root.exists() or not reports_root.is_dir():
        raise FileNotFoundError(f"Reports directory not found: {reports_root}")

    packages: list[DiagnosticPackageIndexItem] = []
    for candidate in sorted(item for item in reports_root.iterdir() if item.is_dir()):
        if _looks_like_package(candidate):
            packages.append(_index_package(reports_root, candidate))
    if not packages:
        warnings.append("No diagnostic packages found under reports directory.")

    return DiagnosticReportsIndex(
        reports_root=str(reports_root),
        generated_at=datetime.now(timezone.utc).isoformat(),
        packages=packages,
        warnings=warnings,
    )


def filter_packages(
    index: DiagnosticReportsIndex,
    verification_status: str | None = None,
    has_user_assertions: bool | None = None,
    has_redaction_warning: bool | None = None,
) -> list[DiagnosticPackageIndexItem]:
    packages = index.packages
    if verification_status:
        packages = [item for item in packages if item.verification_status == verification_status]
    if has_user_assertions is not None:
        packages = [item for item in packages if (item.user_assertion_count > 0) == has_user_assertions]
    if has_redaction_warning is not None:
        packages = [item for item in packages if _has_redaction_warning(item) == has_redaction_warning]
    return packages


def _looks_like_package(path: Path) -> bool:
    return (path / "doctor-report.json").is_file() or (path / "summary.md").is_file()


def _index_package(reports_root: Path, package_dir: Path) -> DiagnosticPackageIndexItem:
    report = _read_json(package_dir / "doctor-report.json")
    verification = _read_json(package_dir / "verification-result.json")
    redaction = _read_json(package_dir / "redaction-report.json")
    manifest = _read_json(package_dir / "manifest.json")
    user_assertions = _read_json(package_dir / "user-assertions.json")

    evidence_count = _count_list(report.get("evidence")) or _count_evidence_files(package_dir)
    timeline_count = _count_list(report.get("timeline"))
    user_assertion_count = _count_assertions(user_assertions)

    warnings = _package_warnings(package_dir, verification, redaction, manifest)
    summary = _summary(report, package_dir)

    return DiagnosticPackageIndexItem(
        name=package_dir.name,
        path=str(package_dir.resolve()),
        relative_path=str(package_dir.resolve().relative_to(reports_root.resolve())),
        project=_project(report),
        summary=summary,
        created_at=_created_at(report, package_dir),
        updated_at=_updated_at(package_dir),
        evidence_count=evidence_count,
        timeline_count=timeline_count,
        user_assertion_count=user_assertion_count,
        verification_status=_verification_status(verification, report),
        redaction_status=_redaction_status(redaction, package_dir),
        package_export_status=_package_export_status(manifest),
        warning_count=len(warnings),
        warnings=warnings,
    )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {"_root": payload}
    except json.JSONDecodeError:
        return {"_error": f"Invalid JSON: {path.name}"}


def _count_list(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _count_assertions(payload: dict[str, Any]) -> int:
    root = payload.get("_root")
    if isinstance(root, list):
        return len(root)
    if isinstance(payload.get("assertions"), list):
        return len(payload["assertions"])
    if isinstance(payload.get("user_assertions"), list):
        return len(payload["user_assertions"])
    return 0


def _count_evidence_files(package_dir: Path) -> int:
    evidence_dir = package_dir / "evidence"
    if not evidence_dir.is_dir():
        return 0
    return sum(1 for item in evidence_dir.rglob("*") if item.is_file())


def _project(report: dict[str, Any]) -> str:
    for key in ["project", "project_name"]:
        if isinstance(report.get(key), str) and report[key]:
            return report[key]
    event = report.get("event")
    if isinstance(event, dict) and isinstance(event.get("project"), str):
        return event["project"]
    return "Unknown project"


def _summary(report: dict[str, Any], package_dir: Path) -> str:
    for key in ["summary", "title", "issue_summary"]:
        if isinstance(report.get(key), str) and report[key]:
            return report[key]
    event = report.get("event")
    if isinstance(event, dict) and isinstance(event.get("summary"), str):
        return event["summary"]
    summary_md = package_dir / "summary.md"
    if summary_md.is_file():
        for line in summary_md.read_text(encoding="utf-8", errors="replace").splitlines():
            cleaned = line.strip("# ").strip()
            if cleaned:
                return cleaned[:200]
    return "No summary available."


def _created_at(report: dict[str, Any], package_dir: Path) -> str | None:
    for key in ["created_at", "timestamp", "generated_at"]:
        if isinstance(report.get(key), str):
            return report[key]
    try:
        return datetime.fromtimestamp(package_dir.stat().st_ctime, tz=timezone.utc).isoformat()
    except OSError:
        return None


def _updated_at(package_dir: Path) -> str | None:
    try:
        latest = max(item.stat().st_mtime for item in package_dir.rglob("*") if item.is_file())
        return datetime.fromtimestamp(latest, tz=timezone.utc).isoformat()
    except ValueError:
        return None


def _verification_status(verification: dict[str, Any], report: dict[str, Any]) -> str:
    if isinstance(verification.get("status"), str):
        return verification["status"]
    embedded = report.get("verification_result")
    if isinstance(embedded, dict) and isinstance(embedded.get("status"), str):
        return embedded["status"]
    return "missing"


def _redaction_status(redaction: dict[str, Any], package_dir: Path) -> str:
    if not (package_dir / "redaction-report.md").is_file() and not redaction:
        return "missing"
    if redaction.get("_error"):
        return "invalid"
    replacements = redaction.get("total_replacements")
    if isinstance(replacements, int):
        return "redacted" if replacements > 0 else "clean"
    return "present"


def _package_export_status(manifest: dict[str, Any]) -> str:
    if not manifest:
        return "not_exported"
    if manifest.get("_error"):
        return "invalid_manifest"
    validation = manifest.get("validation")
    if isinstance(validation, dict) and validation.get("is_valid") is False:
        return "exported_with_warnings"
    return "exported"


def _package_warnings(package_dir: Path, verification: dict[str, Any], redaction: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for relative in REQUIRED_PACKAGE_FILES:
        if not (package_dir / relative).is_file():
            warnings.append(f"Missing required file: {relative}")
    for payload in [verification, redaction, manifest]:
        if payload.get("_error"):
            warnings.append(str(payload["_error"]))
    if _verification_status(verification, {}) in {"missing", "missing_evidence", "not_verified"}:
        warnings.append("Verification is missing, incomplete, or not verified.")
    if _redaction_status(redaction, package_dir) == "missing":
        warnings.append("No redaction report found.")
    return warnings


def _has_redaction_warning(item: DiagnosticPackageIndexItem) -> bool:
    return item.redaction_status in {"missing", "invalid"} or any("redaction" in warning.lower() for warning in item.warnings)
