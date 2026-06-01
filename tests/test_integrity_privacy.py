from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.integrity_privacy import (
    build_integrity_manifest,
    export_safety_gate,
    redaction_gate,
    scan_privacy,
    verify_integrity_manifest,
    write_gate_result,
    write_integrity_manifest,
    write_integrity_verify,
    write_privacy_scan,
)
from doctor_link.p4_cli import main


def test_build_and_verify_integrity_manifest(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    manifest_path = tmp_path / "DoctorReports" / "integrity.json"

    manifest = write_integrity_manifest(tmp_path, manifest_path)
    result = verify_integrity_manifest(tmp_path, manifest_path)

    assert manifest.schema == "doctor-link-integrity-manifest-v1"
    assert manifest.signed is False
    assert len(manifest.files) >= 1
    assert result.status == "passed"
    assert any(item["code"] == "unsigned-package" for item in result.findings)


def test_integrity_verify_detects_hash_mismatch(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("before\n", encoding="utf-8")
    manifest_path = tmp_path / "integrity.json"
    write_integrity_manifest(tmp_path, manifest_path)
    target.write_text("after\n", encoding="utf-8")

    result = verify_integrity_manifest(tmp_path, manifest_path)

    assert result.status == "blocked"
    assert any(item["code"] == "hash-mismatch" for item in result.findings)


def test_integrity_verify_detects_missing_file(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("before\n", encoding="utf-8")
    manifest_path = tmp_path / "integrity.json"
    write_integrity_manifest(tmp_path, manifest_path)
    target.unlink()

    result = verify_integrity_manifest(tmp_path, manifest_path)

    assert result.status == "blocked"
    assert any(item["code"] == "missing-file" for item in result.findings)


def test_integrity_verify_detects_unsafe_path(tmp_path: Path) -> None:
    manifest_path = tmp_path / "integrity.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema": "doctor-link-integrity-manifest-v1",
                "signed": False,
                "files": [{"path": "../secret.txt", "sha256": "x", "size_bytes": 1}],
            }
        ),
        encoding="utf-8",
    )

    result = verify_integrity_manifest(tmp_path, manifest_path)

    assert result.status == "blocked"
    assert any(item["code"] == "unsafe-path" for item in result.findings)


def test_privacy_scan_detects_default_patterns(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Contact test@example.com\n", encoding="utf-8")

    result = scan_privacy(tmp_path)

    assert result.status == "blocked"
    assert result.scanned_files == 1
    assert any(item["pattern"] == "email" for item in result.findings)


def test_privacy_policy_loader_supports_custom_patterns(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("CUSTOM-SECRET-123\n", encoding="utf-8")
    policy = tmp_path / "privacy.yml"
    policy.write_text(
        "\n".join(
            [
                "schema: doctor-link-privacy-policy-v1",
                "patterns:",
                "  custom_secret: CUSTOM-SECRET-[0-9]+",
            ]
        ),
        encoding="utf-8",
    )

    result = scan_privacy(tmp_path, policy)

    assert result.status == "blocked"
    assert any(item["pattern"] == "custom_secret" for item in result.findings)


def test_redaction_and_export_gates_block_findings(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("token=abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")

    redaction = redaction_gate(tmp_path)
    export = export_safety_gate(tmp_path)

    assert redaction.status == "blocked"
    assert export.status == "blocked"


def test_write_gate_and_scan_outputs(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("safe\n", encoding="utf-8")
    scan = write_privacy_scan(scan_privacy(tmp_path), tmp_path / "privacy-scan.json")
    gate = write_gate_result(redaction_gate(tmp_path), tmp_path / "redaction-gate.json")
    manifest = write_integrity_manifest(tmp_path, tmp_path / "integrity.json")
    verify = write_integrity_verify(
        verify_integrity_manifest(tmp_path, tmp_path / "integrity.json"),
        tmp_path / "integrity-verify.json",
    )

    assert scan.status == "passed"
    assert gate.status == "passed"
    assert manifest.files
    assert verify.status == "passed"
    assert (tmp_path / "privacy-scan.json").exists()
    assert (tmp_path / "redaction-gate.json").exists()
    assert (tmp_path / "integrity-verify.json").exists()


def test_build_integrity_manifest_respects_excludes(tmp_path: Path) -> None:
    (tmp_path / "visible.txt").write_text("yes\n", encoding="utf-8")
    ignored = tmp_path / "dist"
    ignored.mkdir()
    (ignored / "hidden.txt").write_text("no\n", encoding="utf-8")

    manifest = build_integrity_manifest(tmp_path)

    paths = {item["path"] for item in manifest.files}
    assert "visible.txt" in paths
    assert "dist/hidden.txt" not in paths


def test_integrity_and_privacy_cli_commands(tmp_path: Path) -> None:
    (tmp_path / "safe.txt").write_text("safe\n", encoding="utf-8")
    runner = CliRunner()
    manifest_path = tmp_path / "DoctorReports" / "integrity.json"

    result_manifest = runner.invoke(
        main,
        ["integrity", "manifest", str(tmp_path), "--out", str(manifest_path), "--json"],
    )
    result_verify = runner.invoke(
        main,
        ["integrity", "verify", str(tmp_path), str(manifest_path), "--json"],
    )
    result_scan = runner.invoke(main, ["privacy", "scan", str(tmp_path), "--json"])
    result_redaction = runner.invoke(main, ["privacy", "redaction-gate", str(tmp_path), "--json"])
    result_export = runner.invoke(main, ["privacy", "export-gate", str(tmp_path), "--json"])

    assert result_manifest.exit_code == 0
    assert result_verify.exit_code == 0
    assert result_scan.exit_code == 0
    assert result_redaction.exit_code == 0
    assert result_export.exit_code == 0
    assert '"status": "passed"' in result_verify.output
