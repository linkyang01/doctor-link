from __future__ import annotations

import json
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso

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

    exclude_attachments: bool = False
    exclude_logs: bool = False
    exclude_screenshots: bool = False
    max_file_size: int | None = None


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
    package_dir: str
    output_zip: str
    exported_at: str
    validation: PackageValidationResult
    included_files: list[PackageManifestFile]
    skipped_files: list[PackageManifestFile]
    manifest_path: str
    package_readme_path: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["validation"] = self.validation.to_dict()
        payload["included_files"] = [item.to_dict() for item in self.included_files]
        payload["skipped_files"] = [item.to_dict() for item in self.skipped_files]
        return payload


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
    validation = validate_package(package_dir)

    output_zip = output_zip or package_dir.with_suffix(".zip")
    output_zip = output_zip.resolve()
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    files = _collect_files(package_dir, options)
    included = [item for item in files if item.included]
    skipped = [item for item in files if not item.included]

    manifest_path = package_dir / "manifest.json"
    readme_path = package_dir / "package-readme.md"

    result = PackageExportResult(
        package_dir=str(package_dir),
        output_zip=str(output_zip),
        exported_at=utc_now_iso(),
        validation=validation,
        included_files=included,
        skipped_files=skipped,
        manifest_path=str(manifest_path),
        package_readme_path=str(readme_path),
    )

    manifest_path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    readme_path.write_text(_render_package_readme(result), encoding="utf-8")

    final_files = _collect_files(package_dir, options)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_item in final_files:
            if not file_item.included:
                continue
            source = _safe_join(package_dir, Path(file_item.path))
            archive.write(source, arcname=str(Path(package_dir.name) / file_item.path))

    return result


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
    if options.exclude_attachments and _is_under(relative, EXCLUDABLE_DIRS["attachments"]):
        return "excluded attachments"
    if options.exclude_logs and _is_under(relative, EXCLUDABLE_DIRS["logs"]):
        return "excluded logs"
    if options.exclude_screenshots and _is_under(relative, EXCLUDABLE_DIRS["screenshots"]):
        return "excluded screenshots"
    if options.max_file_size is not None and size > options.max_file_size:
        return f"file exceeds max size {options.max_file_size} bytes"
    return None


def _render_package_readme(result: PackageExportResult) -> str:
    lines = [
        "# Doctor link Diagnostic Package Export",
        "",
        f"- Exported at: `{result.exported_at}`",
        f"- Source package: `{result.package_dir}`",
        f"- Output zip: `{result.output_zip}`",
        f"- Package valid: `{result.validation.is_valid}`",
        f"- Included files: `{len(result.included_files)}`",
        f"- Skipped files: `{len(result.skipped_files)}`",
        "",
        "## Missing required files",
    ]
    lines.extend(_list(result.validation.missing_required_files))
    lines.extend(["", "## Warnings"])
    lines.extend(_list(result.validation.warnings))
    lines.extend(["", "## Skipped files"])
    lines.extend([f"- `{item.path}`: {item.reason}" for item in result.skipped_files] or ["- None"])
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
