from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.adapter_runtime import (
    discover_adapters,
    load_adapter_manifest,
    run_adapter,
    validate_adapter_file,
)
from doctor_link.entrypoint import main


def _adapter_manifest_text(adapter_id: str = "demo-adapter", extra_capabilities: list[str] | None = None) -> str:
    capabilities = ["evidence_collector", "verification", "handoff"] + (extra_capabilities or [])
    lines = [
        "schema: doctor-link-adapter-v1",
        f"id: {adapter_id}",
        "name: Demo Adapter",
        "version: 0.1.0",
        "description: Demo local adapter",
        "capabilities:",
    ]
    lines.extend(f"  - {capability}" for capability in capabilities)
    lines.extend(
        [
            "commands:",
            "  evidence_collector:",
            "    - python",
            "    - -c",
            "    - print('evidence-ok')",
            "  verification:",
            "    - python",
            "    - -c",
            "    - print('verify-ok')",
            "  handoff:",
            "    - python",
            "    - -c",
            "    - print('handoff-ok')",
        ]
    )
    return "\n".join(lines)


def _write_adapter(project_root: Path, adapter_id: str = "demo-adapter", extra_capabilities: list[str] | None = None) -> Path:
    adapter_dir = project_root / ".doctorlink" / "adapters" / adapter_id
    adapter_dir.mkdir(parents=True)
    manifest = adapter_dir / "adapter.yml"
    manifest.write_text(_adapter_manifest_text(adapter_id, extra_capabilities), encoding="utf-8")
    return manifest


def test_load_and_validate_adapter_manifest(tmp_path: Path) -> None:
    manifest_path = _write_adapter(tmp_path)

    manifest = load_adapter_manifest(manifest_path)
    result = validate_adapter_file(manifest_path)

    assert manifest.adapter_id == "demo-adapter"
    assert manifest.name == "Demo Adapter"
    assert result.valid is True
    assert result.status == "passed"


def test_validate_adapter_manifest_blocks_unknown_capability(tmp_path: Path) -> None:
    manifest_path = _write_adapter(tmp_path, extra_capabilities=["unknown_capability"])

    result = validate_adapter_file(manifest_path)

    assert result.valid is False
    assert result.status == "blocked"
    assert any(item["code"] == "capability-unsupported" for item in result.findings)


def test_discover_adapters(tmp_path: Path) -> None:
    _write_adapter(tmp_path)

    catalog = discover_adapters(tmp_path)

    assert len(catalog.adapters) == 1
    assert catalog.adapters[0].adapter_id == "demo-adapter"
    assert catalog.findings == []


def test_run_adapter_defaults_to_dry_run_audit_record(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    output_dir = tmp_path / "DoctorReports" / "adapters"

    result = run_adapter(tmp_path, "demo-adapter", "verification", output_dir=output_dir)

    assert result.status == "dry-run"
    assert result.return_code is None
    assert result.stdout == ""
    assert result.dry_run is True
    assert result.explicit_user_approval is False
    assert (output_dir / "demo-adapter-verification-run.json").exists()
    audit_file = output_dir / "adapter-audit.jsonl"
    assert audit_file.exists()
    audit = json.loads(audit_file.read_text(encoding="utf-8").splitlines()[0])
    assert audit["adapter_id"] == "demo-adapter"
    assert audit["capability"] == "verification"
    assert audit["local_execution_boundary"] is True
    assert audit["dry_run"] is True
    assert audit["explicit_user_approval"] is False


def test_run_adapter_with_explicit_approval_executes_command(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    output_dir = tmp_path / "DoctorReports" / "adapters"

    result = run_adapter(tmp_path, "demo-adapter", "verification", output_dir=output_dir, allow_run=True)

    assert result.status == "passed"
    assert result.return_code == 0
    assert "verify-ok" in result.stdout
    assert result.dry_run is False
    assert result.explicit_user_approval is True
    audit = json.loads((output_dir / "adapter-audit.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert audit["dry_run"] is False
    assert audit["explicit_user_approval"] is True


def test_adapter_list_cli_json(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["adapter", "list", str(tmp_path), "--json"])

    assert result.exit_code == 0
    assert '"adapter_id": "demo-adapter"' in result.output


def test_adapter_validate_cli_json(tmp_path: Path) -> None:
    manifest_path = _write_adapter(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["adapter", "validate", str(manifest_path), "--json"])

    assert result.exit_code == 0
    assert '"status": "passed"' in result.output


def test_adapter_run_cli_json_defaults_to_dry_run(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["adapter", "run", "demo-adapter", "verification", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0
    assert '"status": "dry-run"' in result.output
    assert '"return_code": null' in result.output
    assert '"stdout": ""' in result.output
    assert '"dry_run": true' in result.output
    assert '"explicit_user_approval": false' in result.output


def test_adapter_run_cli_json_allow_run_executes(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["adapter", "run", "demo-adapter", "verification", str(tmp_path), "--allow-run", "--json"],
    )

    assert result.exit_code == 0
    assert '"status": "passed"' in result.output
    assert '"dry_run": false' in result.output
    assert '"explicit_user_approval": true' in result.output
    assert "verify-ok" in result.output
