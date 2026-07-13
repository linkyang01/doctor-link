from __future__ import annotations

import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

from doctor_link.core.integrity_privacy import export_safety_gate
from doctor_link.core.models import utc_now_iso
from doctor_link.core.package_transaction import LOCK_NAME, atomic_write_json, atomic_write_text, package_transaction

REQUIRED_PACKAGE_FILES = [
    "summary.md",
    "problem-map.md",
    "timeline.md",
    "evidence-list.md",
    "doctor-report.json",
    "ai-context.json",
    "ai-task.md",
    "fix-verification-checklist.md",
    "user-assertions.json",
]

EXCLUDABLE_DIRS = {
    "attachments": Path("evidence/attachments"),
    "logs": Path("evidence/logs"),
    "screenshots": Path("evidence/screenshots"),
}


@dataclass
class PackageExportOptions:
    """Options for exporting a diagnostic package."""

    include_web_assets: bool = False
    exclude_attachments: bool = False
    exclude_logs: bool = False
    exclude_screenshots: bool = False
    max_file_size: int | None = None
    privacy_policy: Path | None = None
    allow_unsafe_export: bool = False


@dataclass
class PackageManifestFile:
    path: str
    size_bytes: int
    included: bool = True
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PackageValidationResult:
    package_dir: str
    is_valid: bool
    missing_required_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PackageExportResult:
    schema: str
    package_dir: str
    output_zip: str
    exported_at: str
    validation: PackageValidationResult
    included_files: list[PackageManifestFile]
    skipped_files: list[PackageManifestFile]
    manifest_path: str
    package_readme_path: str
    privacy_gate: dict[str, Any]
    redaction_report_present: bool = False
    redaction_report_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["validation"] = self.validation.to_dict()
        payload["included_files"] = [item.to_dict() for item in self.included_files]
        payload["skipped_files"] = [item.to_dict() for item in self.skipped_files]
        return payload

    def to_manifest_dict(self) -> dict[str, Any]:
        """Return a portable payload safe to store inside an exported archive."""
        payload = self.to_dict()
        payload["package_dir"] = "."
        payload["output_zip"] = _portable_name(self.output_zip)
        payload["validation"]["package_dir"] = "."
        payload["manifest_path"] = _portable_name(self.manifest_path)
        payload["package_readme_path"] = _portable_name(self.package_readme_path)
        if payload.get("redaction_report_path"):
            payload["redaction_report_path"] = _portable_name(str(payload["redaction_report_path"]))
        return payload


@dataclass
class PackageManifestMigrationResult:
    schema: str
    status: str
    package_dir: str
    source_path: str | None
    target_path: str
    backup_path: str | None
    readme_backup_path: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UnsafePackageExportError(RuntimeError):
    """Raised when the default privacy export gate blocks an archive."""

    def __init__(self, findings_count: int) -> None:
        self.findings_count = findings_count
        super().__init__(
            f"Privacy export gate blocked {findings_count} finding(s). "
            "Redact the package or explicitly pass --allow-unsafe-export after review."
        )


class InsufficientDiskSpaceError(RuntimeError):
    """Raised before export when the destination cannot hold a safe archive attempt."""


def validate_package(package_dir: Path) -> PackageValidationResult:
    """Validate that a directory looks like a Doctor link diagnostic package."""
    package_dir = package_dir.resolve()
    if not package_dir.exists() or not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    missing = [path for path in REQUIRED_PACKAGE_FILES if not (package_dir / path).is_file()]
    warnings: list[str] = []
    evidence_dir = package_dir / "evidence"
    if not evidence_dir.is_dir():
        warnings.append("Missing evidence directory.")
    for subdir in ["logs", "screenshots", "command-output", "test-results", "attachments"]:
        if not (evidence_dir / subdir).is_dir():
            warnings.append(f"Missing evidence subdirectory: evidence/{subdir}")
    if not (package_dir / "redaction-report.md").is_file():
        warnings.append("No redaction-report.md found. Sensitive information filtering may not have been run.")

    return PackageValidationResult(
        package_dir=str(package_dir),
        is_valid=not missing,
        missing_required_files=missing,
        warnings=warnings,
    )


def export_package(
    package_dir: Path,
    output_zip: Path | None = None,
    options: PackageExportOptions | None = None,
) -> PackageExportResult:
    """Export a Doctor link diagnostic package as a zip file.

    The exporter keeps the package structure intact, writes a manifest and a
    package readme into the package before export, and records skipped files.
    """
    package_dir = package_dir.resolve()
    options = options or PackageExportOptions()
    output_zip = output_zip or package_dir.with_suffix(".zip")
    output_zip = output_zip.resolve()
    if _is_relative_to(output_zip, package_dir):
        raise ValueError("Output zip must be outside the diagnostic package directory.")
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    with package_transaction(package_dir):
        files = _collect_files(package_dir, options)
        export_paths = {item.path for item in files if item.included}
        gate = export_safety_gate(
            package_dir,
            options.privacy_policy,
            include_paths=export_paths,
        )
        gate_summary = _privacy_gate_summary(gate.to_dict(), options.allow_unsafe_export)
        if gate.status != "passed" and not options.allow_unsafe_export:
            raise UnsafePackageExportError(len(gate.findings))

        validation = validate_package(package_dir)
        included = [item for item in files if item.included]
        skipped = [item for item in files if not item.included]

        manifest_path = package_dir / "package-export-manifest.json"
        readme_path = package_dir / "package-readme.md"
        redaction_report = package_dir / "redaction-report.md"

        result = PackageExportResult(
            schema="doctor-link-package-export-manifest-v1",
            package_dir=str(package_dir),
            output_zip=str(output_zip),
            exported_at=utc_now_iso(),
            validation=validation,
            included_files=included,
            skipped_files=skipped,
            manifest_path=str(manifest_path),
            package_readme_path=str(readme_path),
            privacy_gate=gate_summary,
            redaction_report_present=redaction_report.is_file(),
            redaction_report_path=str(redaction_report) if redaction_report.is_file() else None,
        )

        portable_payload = result.to_manifest_dict()
        atomic_write_json(manifest_path, portable_payload)
        atomic_write_text(readme_path, _render_package_readme(portable_payload))

        final_files = _collect_files(package_dir, options)
        _ensure_disk_capacity(output_zip.parent, final_files)
        _write_zip_atomically(package_dir, output_zip, final_files)

    return result


def migrate_legacy_export_manifest(package_dir: Path) -> PackageManifestMigrationResult:
    """Migrate an export-shaped legacy manifest.json without touching formal manifests."""
    package_dir = package_dir.resolve()
    source = package_dir / "manifest.json"
    target = package_dir / "package-export-manifest.json"
    readme = package_dir / "package-readme.md"

    with package_transaction(package_dir):
        if not source.exists():
            if target.exists():
                return PackageManifestMigrationResult(
                    schema="doctor-link-package-export-migration-v1",
                    status="already_migrated",
                    package_dir=str(package_dir),
                    source_path=None,
                    target_path=str(target),
                    backup_path=None,
                    readme_backup_path=None,
                )
            raise FileNotFoundError(f"Legacy export manifest not found: {source}")

        payload = json.loads(source.read_text(encoding="utf-8"))
        if not _looks_like_legacy_export_manifest(payload):
            raise ValueError("manifest.json is not a legacy package export manifest; it was left untouched.")

        migrated = _migrate_manifest_payload(payload)
        if target.exists():
            existing = json.loads(target.read_text(encoding="utf-8"))
            if existing.get("schema") != "doctor-link-package-export-manifest-v1":
                raise FileExistsError(f"Refusing to replace unrelated target manifest: {target}")
        else:
            atomic_write_json(target, migrated)

        readme_backup: Path | None = None
        if readme.exists():
            readme_backup = _next_backup_path(package_dir / "package-readme.legacy-export.md")
            os.replace(readme, readme_backup)
        atomic_write_text(readme, _render_package_readme(migrated))

        backup = _next_backup_path(package_dir / "manifest.legacy-export.json")
        os.replace(source, backup)

    return PackageManifestMigrationResult(
        schema="doctor-link-package-export-migration-v1",
        status="migrated",
        package_dir=str(package_dir),
        source_path=str(source),
        target_path=str(target),
        backup_path=str(backup),
        readme_backup_path=str(readme_backup) if readme_backup else None,
    )


def _collect_files(package_dir: Path, options: PackageExportOptions) -> list[PackageManifestFile]:
    files: list[PackageManifestFile] = []
    for path in sorted(item for item in package_dir.rglob("*") if item.is_file()):
        relative = _relative_path(package_dir, path)
        size = path.stat().st_size
        reason = _skip_reason(relative, size, options)
        files.append(
            PackageManifestFile(
                path=str(relative),
                size_bytes=size,
                included=reason is None,
                reason=reason,
            )
        )
    return files


def _skip_reason(relative: Path, size: int, options: PackageExportOptions) -> str | None:
    if relative == Path(LOCK_NAME):
        return "excluded internal transaction lock"
    if relative.name.startswith(("manifest.legacy-export", "package-readme.legacy-export")):
        return "excluded legacy migration backup"
    if not options.include_web_assets and _is_under(relative, Path(".doctorlink-web")):
        return "excluded web assets"
    if options.exclude_attachments and _is_under(relative, EXCLUDABLE_DIRS["attachments"]):
        return "excluded attachments"
    if options.exclude_logs and _is_under(relative, EXCLUDABLE_DIRS["logs"]):
        return "excluded logs"
    if options.exclude_screenshots and _is_under(relative, EXCLUDABLE_DIRS["screenshots"]):
        return "excluded screenshots"
    if options.max_file_size is not None and size > options.max_file_size:
        return f"file exceeds max size {options.max_file_size} bytes"
    return None


def _render_package_readme(payload: dict[str, Any]) -> str:
    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    privacy_gate = payload.get("privacy_gate") if isinstance(payload.get("privacy_gate"), dict) else {}
    included_files = payload.get("included_files") if isinstance(payload.get("included_files"), list) else []
    skipped_files = payload.get("skipped_files") if isinstance(payload.get("skipped_files"), list) else []
    lines = [
        "# Doctor link Diagnostic Package Export",
        "",
        f"- Exported at: `{payload.get('exported_at')}`",
        f"- Source package: `{payload.get('package_dir')}`",
        f"- Output zip: `{payload.get('output_zip')}`",
        f"- Package valid: `{validation.get('is_valid')}`",
        f"- Privacy gate: `{privacy_gate.get('status', 'not_run')}`",
        f"- Privacy override used: `{privacy_gate.get('override_used', False)}`",
        f"- Included files: `{len(included_files)}`",
        f"- Skipped files: `{len(skipped_files)}`",
        f"- Redaction report present: `{payload.get('redaction_report_present', False)}`",
        "",
        "## Missing required files",
    ]
    missing = validation.get("missing_required_files")
    lines.extend(_list([str(item) for item in missing] if isinstance(missing, list) else []))
    lines.extend(["", "## Warnings"])
    warnings = validation.get("warnings")
    lines.extend(_list([str(item) for item in warnings] if isinstance(warnings, list) else []))
    lines.extend(["", "## Redaction"])
    if payload.get("redaction_report_present"):
        lines.append(f"- Redaction report: `{payload.get('redaction_report_path')}`")
    else:
        lines.append("- No redaction report found. Review package contents before sharing externally.")
    lines.extend(["", "## Skipped files"])
    rendered_skipped = [
        f"- `{item.get('path')}`: {item.get('reason')}"
        for item in skipped_files
        if isinstance(item, dict)
    ]
    lines.extend(rendered_skipped or ["- None"])
    lines.extend(
        [
            "",
            "## Notes",
            "This zip is a Doctor link diagnostic handoff package. It preserves the diagnostic package directory structure for AI tools, developers, and reviewers.",
            "",
        ]
    )
    return "\n".join(lines)


def _relative_path(root: Path, path: Path) -> Path:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Path is outside package directory: {path}") from exc
    if ".." in relative.parts:
        raise ValueError(f"Unsafe relative path: {relative}")
    return relative


def _safe_join(root: Path, relative: Path) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Refusing to access path outside package directory: {relative}") from exc
    return candidate


def _is_under(path: Path, parent: Path) -> bool:
    return path == parent or path.parts[: len(parent.parts)] == parent.parts


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]


def _privacy_gate_summary(payload: dict[str, Any], allow_unsafe_export: bool) -> dict[str, Any]:
    report = payload.get("report") if isinstance(payload.get("report"), dict) else {}
    privacy = report.get("privacy") if isinstance(report.get("privacy"), dict) else {}
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    status = str(payload.get("status") or "blocked")
    return {
        "status": status,
        "scanned_files": int(privacy.get("scanned_files") or 0),
        "findings_count": len(findings),
        "override_used": status != "passed" and allow_unsafe_export,
    }


def _write_zip_atomically(package_dir: Path, output_zip: Path, files: list[PackageManifestFile]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_zip.name}.", suffix=".tmp", dir=output_zip.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_item in files:
                if not file_item.included:
                    continue
                source = _safe_join(package_dir, Path(file_item.path))
                archive.write(source, arcname=str(Path(package_dir.name) / file_item.path))
        with temporary_path.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary_path, output_zip)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def _ensure_disk_capacity(output_dir: Path, files: list[PackageManifestFile]) -> None:
    included = [item for item in files if item.included]
    estimated_bytes = sum(item.size_bytes for item in included) + max(1_048_576, len(included) * 512)
    free_bytes = shutil.disk_usage(output_dir).free
    if free_bytes < estimated_bytes:
        raise InsufficientDiskSpaceError(
            f"Insufficient disk space for atomic export: need at least {estimated_bytes} bytes, "
            f"but only {free_bytes} bytes are free."
        )


def _looks_like_legacy_export_manifest(payload: Any) -> bool:
    return isinstance(payload, dict) and "output_zip" in payload and "included_files" in payload


def _migrate_manifest_payload(payload: dict[str, Any]) -> dict[str, Any]:
    migrated = dict(payload)
    migrated["schema"] = "doctor-link-package-export-manifest-v1"
    migrated["package_dir"] = "."
    migrated["output_zip"] = _portable_name(str(payload.get("output_zip") or "diagnostic-package.zip"))
    validation = dict(payload.get("validation")) if isinstance(payload.get("validation"), dict) else {}
    validation["package_dir"] = "."
    migrated["validation"] = validation
    migrated["manifest_path"] = "package-export-manifest.json"
    migrated["package_readme_path"] = "package-readme.md"
    if migrated.get("redaction_report_path"):
        migrated["redaction_report_path"] = _portable_name(str(migrated["redaction_report_path"]))
    migrated.setdefault(
        "privacy_gate",
        {"status": "not_run", "scanned_files": 0, "findings_count": 0, "override_used": False},
    )
    for key in ("included_files", "skipped_files"):
        items = migrated.get(key)
        if not isinstance(items, list):
            migrated[key] = []
            continue
        normalized: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            copied = dict(item)
            copied["path"] = _safe_manifest_relative_path(str(item.get("path") or ""))
            normalized.append(copied)
        migrated[key] = normalized
    return migrated


def _safe_manifest_relative_path(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not value or ".." in path.parts:
        raise ValueError(f"Unsafe file path in legacy export manifest: {value}")
    return str(path)


def _portable_name(value: str) -> str:
    if "\\" in value:
        return PureWindowsPath(value).name
    return PurePosixPath(value).name


def _next_backup_path(preferred: Path) -> Path:
    if not preferred.exists():
        return preferred
    counter = 1
    while True:
        candidate = preferred.with_name(f"{preferred.stem}.{counter}{preferred.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
