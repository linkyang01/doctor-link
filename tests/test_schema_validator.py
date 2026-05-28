from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.schema_validator import validate_diagnostic_package
from doctor_link.p4_cli import main


def test_schema_validator_accepts_generated_package(tmp_path: Path) -> None:
    package = build_diagnostic_package(DiagnosticEvent(project="Schema Demo", summary="schema validation"), tmp_path)
    assert package.root_dir is not None

    result = validate_diagnostic_package(package.root_dir)

    assert result.valid
    assert "doctor-report.json" in result.checked_files
    assert "ai-context.json" in result.checked_files
    assert "user-assertions.json" in result.checked_files


def test_schema_validator_rejects_missing_required_file(tmp_path: Path) -> None:
    package = build_diagnostic_package(DiagnosticEvent(project="Schema Demo"), tmp_path)
    assert package.root_dir is not None
    (package.root_dir / "doctor-report.json").unlink()

    result = validate_diagnostic_package(package.root_dir)

    assert not result.valid
    assert any(item.path == "doctor-report.json" and item.level == "error" for item in result.findings)


def test_schema_validate_cli_writes_result_files(tmp_path: Path) -> None:
    package = build_diagnostic_package(DiagnosticEvent(project="Schema Demo"), tmp_path)
    assert package.root_dir is not None
    runner = CliRunner()

    result = runner.invoke(main, ["schema", "validate", str(package.root_dir), "--write", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["valid"] is True
    assert (package.root_dir / "schema-validation-result.json").exists()
    assert (package.root_dir / "schema-validation-result.md").exists()
