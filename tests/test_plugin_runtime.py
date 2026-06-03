from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.plugin_runtime import (
    discover_plugins,
    load_plugin_manifest,
    run_plugin,
    validate_plugin_file,
)
from doctor_link.entrypoint import main


def _plugin_manifest_text(
    plugin_id: str = "demo-plugin",
    extra_extension_points: list[str] | None = None,
    extra_permissions: list[str] | None = None,
    permissions: list[str] | None = None,
) -> str:
    extension_points = ["collector", "renderer", "handoff", "verification"] + (extra_extension_points or [])
    permission_values = permissions if permissions is not None else ["read_project", "write_reports", "run_local_command"]
    permission_values = permission_values + (extra_permissions or [])
    lines = [
        "schema: doctor-link-plugin-v1",
        f"id: {plugin_id}",
        "name: Demo Plugin",
        "version: 0.1.0",
        "description: Demo local plugin",
        "extension_points:",
    ]
    lines.extend(f"  - {extension_point}" for extension_point in extension_points)
    lines.append("permissions:")
    lines.extend(f"  - {permission}" for permission in permission_values)
    lines.extend(
        [
            "commands:",
            "  collector:",
            "    - python",
            "    - -c",
            "    - print('collector-ok')",
            "  renderer:",
            "    - python",
            "    - -c",
            "    - print('renderer-ok')",
            "  handoff:",
            "    - python",
            "    - -c",
            "    - print('handoff-ok')",
            "  verification:",
            "    - python",
            "    - -c",
            "    - print('verification-ok')",
        ]
    )
    return "\n".join(lines)


def _write_plugin(
    project_root: Path,
    plugin_id: str = "demo-plugin",
    extra_extension_points: list[str] | None = None,
    extra_permissions: list[str] | None = None,
    permissions: list[str] | None = None,
) -> Path:
    plugin_dir = project_root / ".doctorlink" / "plugins" / plugin_id
    plugin_dir.mkdir(parents=True)
    manifest = plugin_dir / "plugin.yml"
    manifest.write_text(
        _plugin_manifest_text(plugin_id, extra_extension_points, extra_permissions, permissions),
        encoding="utf-8",
    )
    return manifest


def test_load_and_validate_plugin_manifest(tmp_path: Path) -> None:
    manifest_path = _write_plugin(tmp_path)

    manifest = load_plugin_manifest(manifest_path)
    result = validate_plugin_file(manifest_path)

    assert manifest.plugin_id == "demo-plugin"
    assert manifest.name == "Demo Plugin"
    assert result.valid is True
    assert result.status == "passed"


def test_validate_plugin_manifest_blocks_unknown_extension_point(tmp_path: Path) -> None:
    manifest_path = _write_plugin(tmp_path, extra_extension_points=["unknown_extension"])

    result = validate_plugin_file(manifest_path)

    assert result.valid is False
    assert result.status == "blocked"
    assert any(item["code"] == "extension-point-unsupported" for item in result.findings)


def test_validate_plugin_manifest_blocks_unknown_permission(tmp_path: Path) -> None:
    manifest_path = _write_plugin(tmp_path, extra_permissions=["unknown_permission"])

    result = validate_plugin_file(manifest_path)

    assert result.valid is False
    assert result.status == "blocked"
    assert any(item["code"] == "permission-unsupported" for item in result.findings)


def test_discover_plugins(tmp_path: Path) -> None:
    _write_plugin(tmp_path)

    catalog = discover_plugins(tmp_path)

    assert len(catalog.plugins) == 1
    assert catalog.plugins[0].plugin_id == "demo-plugin"
    assert catalog.findings == []


def test_run_plugin_defaults_to_dry_run_audit_record(tmp_path: Path) -> None:
    _write_plugin(tmp_path)
    output_dir = tmp_path / "DoctorReports" / "plugins"

    result = run_plugin(tmp_path, "demo-plugin", "verification", output_dir=output_dir)

    assert result.status == "dry-run"
    assert result.return_code is None
    assert result.stdout == ""
    assert result.dry_run is True
    assert result.explicit_user_approval is False
    assert (output_dir / "demo-plugin-verification-run.json").exists()
    audit_file = output_dir / "plugin-audit.jsonl"
    assert audit_file.exists()
    audit = json.loads(audit_file.read_text(encoding="utf-8").splitlines()[0])
    assert audit["plugin_id"] == "demo-plugin"
    assert audit["extension_point"] == "verification"
    assert audit["local_execution_boundary"] is True
    assert audit["sandbox_boundary"] == "local-process-boundary"
    assert audit["dry_run"] is True
    assert audit["explicit_user_approval"] is False


def test_run_plugin_with_explicit_approval_executes_command(tmp_path: Path) -> None:
    _write_plugin(tmp_path)
    output_dir = tmp_path / "DoctorReports" / "plugins"

    result = run_plugin(tmp_path, "demo-plugin", "verification", output_dir=output_dir, allow_run=True)

    assert result.status == "passed"
    assert result.return_code == 0
    assert "verification-ok" in result.stdout
    assert result.dry_run is False
    assert result.explicit_user_approval is True
    audit = json.loads((output_dir / "plugin-audit.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert audit["dry_run"] is False
    assert audit["explicit_user_approval"] is True


def test_run_plugin_requires_run_permission(tmp_path: Path) -> None:
    _write_plugin(tmp_path, permissions=["read_project", "write_reports"])

    try:
        run_plugin(tmp_path, "demo-plugin", "verification")
    except ValueError as exc:
        assert "run_local_command" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected missing permission failure")


def test_plugin_list_cli_json(tmp_path: Path) -> None:
    _write_plugin(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["plugin", "list", str(tmp_path), "--json"])

    assert result.exit_code == 0
    assert '"plugin_id": "demo-plugin"' in result.output


def test_plugin_validate_cli_json(tmp_path: Path) -> None:
    manifest_path = _write_plugin(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["plugin", "validate", str(manifest_path), "--json"])

    assert result.exit_code == 0
    assert '"status": "passed"' in result.output


def test_plugin_run_cli_json_defaults_to_dry_run(tmp_path: Path) -> None:
    _write_plugin(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["plugin", "run", "demo-plugin", "verification", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0
    assert '"status": "dry-run"' in result.output
    assert '"dry_run": true' in result.output
    assert '"explicit_user_approval": false' in result.output
    assert "verification-ok" not in result.output


def test_plugin_run_cli_json_allow_run_executes(tmp_path: Path) -> None:
    _write_plugin(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["plugin", "run", "demo-plugin", "verification", str(tmp_path), "--allow-run", "--json"],
    )

    assert result.exit_code == 0
    assert '"status": "passed"' in result.output
    assert '"dry_run": false' in result.output
    assert '"explicit_user_approval": true' in result.output
    assert "verification-ok" in result.output
