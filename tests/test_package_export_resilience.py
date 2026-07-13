from __future__ import annotations

import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.package_exporter import (
    InsufficientDiskSpaceError,
    PackageExportOptions,
    UnsafePackageExportError,
    export_package,
)
from doctor_link.entrypoint import main


def _package(tmp_path: Path, project: str = "Export resilience") -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project=project, category="export", summary="resilience validation"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_export_blocks_privacy_findings_by_default_and_records_explicit_override(tmp_path: Path) -> None:
    package = _package(tmp_path)
    secret = package / "evidence" / "logs" / "secret.txt"
    secret.write_text("token=abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
    output = tmp_path / "unsafe.zip"

    with pytest.raises(UnsafePackageExportError, match="Privacy export gate blocked"):
        export_package(package, output)

    assert not output.exists()
    assert not (package / "package-export-manifest.json").exists()

    result = export_package(
        package,
        output,
        PackageExportOptions(allow_unsafe_export=True),
    )
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert output.exists()
    assert manifest["privacy_gate"] == {
        "status": "blocked",
        "scanned_files": manifest["privacy_gate"]["scanned_files"],
        "findings_count": 1,
        "override_used": True,
    }


def test_privacy_gate_scans_only_files_selected_for_export(tmp_path: Path) -> None:
    package = _package(tmp_path)
    secret = package / "evidence" / "logs" / "excluded-secret.txt"
    secret.write_text("token=abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")

    result = export_package(
        package,
        tmp_path / "without-logs.zip",
        PackageExportOptions(exclude_logs=True),
    )

    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["privacy_gate"]["status"] == "passed"
    assert "evidence/logs/excluded-secret.txt" in {
        item["path"] for item in manifest["skipped_files"]
    }


def test_doctor_package_cli_returns_structured_success_and_blocked_failure(tmp_path: Path) -> None:
    package = _package(tmp_path)
    safe_output = tmp_path / "safe-cli.zip"
    runner = CliRunner()

    safe = runner.invoke(
        main,
        ["doctor-package", str(package), "--out", str(safe_output), "--json"],
    )
    assert safe.exit_code == 0, safe.output
    assert json.loads(safe.output)["privacy_gate"]["status"] == "passed"

    (package / "evidence" / "logs" / "secret.txt").write_text(
        "secret=abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8"
    )
    blocked = runner.invoke(
        main,
        ["doctor-package", str(package), "--out", str(tmp_path / "blocked.zip"), "--json"],
    )
    assert blocked.exit_code != 0
    assert "Privacy export gate blocked" in blocked.output


def test_export_manifest_and_readme_never_store_absolute_local_paths(tmp_path: Path) -> None:
    package = _package(tmp_path)
    output = tmp_path / "portable.zip"

    result = export_package(package, output)

    manifest_text = Path(result.manifest_path).read_text(encoding="utf-8")
    readme_text = Path(result.package_readme_path).read_text(encoding="utf-8")
    assert str(tmp_path) not in manifest_text
    assert str(tmp_path) not in readme_text
    with zipfile.ZipFile(output) as archive:
        archived_manifest = archive.read(
            f"{package.name}/package-export-manifest.json"
        ).decode("utf-8")
    assert str(tmp_path) not in archived_manifest


def test_schema_migrate_converts_legacy_export_and_preserves_backups(tmp_path: Path) -> None:
    package = _package(tmp_path)
    exported = export_package(package, tmp_path / "legacy.zip")
    target = Path(exported.manifest_path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload.pop("schema")
    payload.pop("privacy_gate")
    payload["package_dir"] = str(package)
    payload["output_zip"] = str(tmp_path / "legacy.zip")
    payload["validation"]["package_dir"] = str(package)
    payload["manifest_path"] = str(package / "manifest.json")
    payload["package_readme_path"] = str(package / "package-readme.md")
    target.unlink()
    (package / "manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (package / "package-readme.md").write_text(
        f"Legacy source: {package}\n", encoding="utf-8"
    )

    invocation = CliRunner().invoke(main, ["schema", "migrate", str(package), "--json"])

    assert invocation.exit_code == 0, invocation.output
    result = json.loads(invocation.output)
    assert result["status"] == "migrated"
    assert not (package / "manifest.json").exists()
    assert Path(result["backup_path"]).name == "manifest.legacy-export.json"
    assert Path(result["readme_backup_path"]).name == "package-readme.legacy-export.md"
    migrated_text = (package / "package-export-manifest.json").read_text(encoding="utf-8")
    readme_text = (package / "package-readme.md").read_text(encoding="utf-8")
    assert str(tmp_path) not in migrated_text
    assert str(tmp_path) not in readme_text
    assert json.loads(migrated_text)["privacy_gate"]["status"] == "not_run"

    migrated_export = tmp_path / "migrated-export.zip"
    export_package(package, migrated_export)
    with zipfile.ZipFile(migrated_export) as archive:
        archived_names = archive.namelist()
        archived_text = "\n".join(
            archive.read(name).decode("utf-8", errors="ignore")
            for name in archived_names
        )
    assert not any("legacy-export" in name for name in archived_names)
    assert str(tmp_path) not in archived_text

    repeated = CliRunner().invoke(main, ["schema", "migrate", str(package), "--json"])
    assert repeated.exit_code == 0, repeated.output
    assert json.loads(repeated.output)["status"] == "already_migrated"

    readable = CliRunner().invoke(main, ["schema", "migrate", str(package)])
    assert readable.exit_code == 0, readable.output
    assert "Schema migration status: already_migrated" in readable.output


def test_schema_migrate_refuses_formal_manifest(tmp_path: Path) -> None:
    package = _package(tmp_path)
    formal = {"package_id": "formal", "schema_version": "1", "files": []}
    path = package / "manifest.json"
    path.write_text(json.dumps(formal), encoding="utf-8")

    invocation = CliRunner().invoke(main, ["schema", "migrate", str(package), "--json"])

    assert invocation.exit_code != 0
    assert "not a legacy package export manifest" in invocation.output
    assert json.loads(path.read_text(encoding="utf-8")) == formal


def test_large_file_count_export_preserves_every_evidence_file(tmp_path: Path) -> None:
    package = _package(tmp_path)
    attachments = package / "evidence" / "attachments" / "bulk"
    attachments.mkdir()
    expected = 1_200
    for index in range(expected):
        (attachments / f"item-{index:04d}.txt").write_text("payload\n", encoding="utf-8")

    output = tmp_path / "large.zip"
    export_package(package, output)

    with zipfile.ZipFile(output) as archive:
        bulk_files = [
            name
            for name in archive.namelist()
            if f"{package.name}/evidence/attachments/bulk/item-" in name
        ]
    assert len(bulk_files) == expected


def test_interrupted_export_preserves_previous_archive_and_can_be_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = _package(tmp_path)
    output = tmp_path / "atomic.zip"
    output.write_bytes(b"previous-complete-archive")
    original_write = zipfile.ZipFile.write
    calls = 0

    def interrupt(self: zipfile.ZipFile, *args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt("simulated interruption")
        original_write(self, *args, **kwargs)

    monkeypatch.setattr(zipfile.ZipFile, "write", interrupt)
    with pytest.raises(KeyboardInterrupt, match="simulated interruption"):
        export_package(package, output)

    assert output.read_bytes() == b"previous-complete-archive"
    assert not list(tmp_path.glob(f".{output.name}.*.tmp"))

    monkeypatch.undo()
    export_package(package, output)
    assert zipfile.is_zipfile(output)


def test_insufficient_disk_space_fails_before_replacing_existing_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = _package(tmp_path)
    output = tmp_path / "capacity.zip"
    output.write_bytes(b"previous-complete-archive")
    monkeypatch.setattr(
        "doctor_link.core.package_exporter.shutil.disk_usage",
        lambda _path: SimpleNamespace(total=10, used=10, free=0),
    )

    with pytest.raises(InsufficientDiskSpaceError, match="Insufficient disk space"):
        export_package(package, output)

    assert output.read_bytes() == b"previous-complete-archive"
    assert not list(tmp_path.glob(f".{output.name}.*.tmp"))


def test_export_refuses_to_place_archive_inside_package(tmp_path: Path) -> None:
    package = _package(tmp_path)

    with pytest.raises(ValueError, match="must be outside"):
        export_package(package, package / "recursive.zip")
