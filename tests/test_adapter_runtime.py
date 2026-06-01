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
from doctor_link.p4_cli import main


def _write_adapter(project_root: Path, adapter_id: str = "demo-adapter") -> Path:
    adapter_dir = project_root / ".doctorlink" / "adapters" / adapter_id
    adapter_dir.mkdir(parents=True)
    manifest = adapter_dir / "adapter.yml"
    manifest.write_text(
        "\n".join(
            [
                "schema: doctor-link-adapter-v1",
                f"id: {adapter_id}",
                "name: Demo Adapter",
                "version: 0.1.0",
                "description: Demo local adapter",
                "capabilities:",
                "  - evidence_collector",
                "  - verification",
                "  - handoff",
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
        ),
        encoding="utf-8",
    )
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
    manifest_path = _write_adapter(tmp_path)
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(text + "\n  - unknown_capability\n", encoding="utf-8")

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


def test_run_adapter_writes_audit_record(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    output_dir = tmp_path / "DoctorReports" / "adapters"

    result = run_adapter(tmp_path, "demo-adapter", "verification", output_dir=output_dir)

    assert result.status == "passed"
    assert result.return_code == 0
    assert "verify-ok" in result.stdout
    assert (output_dir / "demo-adapter-verification-run.json").exists()
    audit_file = output_dir / "adapter-audit.jsonl"
    assert audit_file.exists()
    audit = json.loads(audit_file.read_text(encoding="utf-8").splitlines()[0])
    assert audit["adapter_id"] == "demo-adapter"
    assert audit["capability"] == "verification"
    assert audit["local_execution_boundary"] is True


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


def test_adapter_run_cli_json(tmp_path: Path) -> None:
    _write_adapter(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["adapter", "run", "demo-adapter", "verification", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0
    assert '"status": "passed"' in result.output
    assert "verify-ok" in result.output
