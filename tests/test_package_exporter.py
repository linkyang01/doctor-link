from __future__ import annotations

import json
import zipfile
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.package_exporter import PackageExportOptions, export_package, validate_package


def _build_package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="package_export", summary="Package export test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_validate_package_accepts_standard_package(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)

    validation = validate_package(package_dir)

    assert validation.is_valid is True
    assert validation.missing_required_files == []


def test_export_package_writes_manifest_readme_and_zip(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    output_zip = tmp_path / "handoff.zip"

    result = export_package(package_dir, output_zip)

    assert output_zip.exists()
    assert Path(result.manifest_path).exists()
    assert Path(result.package_readme_path).exists()
    assert result.validation.is_valid is True

    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["output_zip"] == str(output_zip.resolve())
    assert manifest["validation"]["is_valid"] is True

    with zipfile.ZipFile(output_zip) as archive:
        names = set(archive.namelist())
    prefix = package_dir.name
    assert f"{prefix}/summary.md" in names
    assert f"{prefix}/doctor-report.json" in names
    assert f"{prefix}/manifest.json" in names
    assert f"{prefix}/package-readme.md" in names


def test_export_package_can_exclude_logs_attachments_and_screenshots(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    (package_dir / "evidence" / "logs" / "app.log").write_text("log", encoding="utf-8")
    (package_dir / "evidence" / "attachments" / "input.txt").write_text("attachment", encoding="utf-8")
    (package_dir / "evidence" / "screenshots" / "screen.txt").write_text("screenshot", encoding="utf-8")
    output_zip = tmp_path / "filtered.zip"

    result = export_package(
        package_dir,
        output_zip,
        PackageExportOptions(exclude_logs=True, exclude_attachments=True, exclude_screenshots=True),
    )

    skipped_paths = {item.path for item in result.skipped_files}
    assert "evidence/logs/app.log" in skipped_paths
    assert "evidence/attachments/input.txt" in skipped_paths
    assert "evidence/screenshots/screen.txt" in skipped_paths

    with zipfile.ZipFile(output_zip) as archive:
        names = set(archive.namelist())
    prefix = package_dir.name
    assert f"{prefix}/evidence/logs/app.log" not in names
    assert f"{prefix}/evidence/attachments/input.txt" not in names
    assert f"{prefix}/evidence/screenshots/screen.txt" not in names


def test_export_package_skips_large_files(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    large_file = package_dir / "evidence" / "attachments" / "large.bin"
    large_file.write_bytes(b"x" * 32)

    result = export_package(package_dir, tmp_path / "limited.zip", PackageExportOptions(max_file_size=10))

    skipped = {item.path: item.reason for item in result.skipped_files}
    assert skipped["evidence/attachments/large.bin"] == "file exceeds max size 10 bytes"


def test_validate_package_reports_missing_required_files(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    (package_dir / "ai-task.md").unlink()

    validation = validate_package(package_dir)

    assert validation.is_valid is False
    assert "ai-task.md" in validation.missing_required_files
