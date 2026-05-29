from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.schema_validator import validate_diagnostic_package
from doctor_link.p4_cli import main


SCHEMA_FILES = [
    "doctor-report.schema.json",
    "ai-context.schema.json",
    "user-assertions.schema.json",
    "verification-result.schema.json",
    "handoff-manifest.schema.json",
    "ai-repair-result.schema.json",
    "diagnosis-history.schema.json",
    "manifest.schema.json",
]


def test_schema_file_set_exists() -> None:
    schema_dir = Path("schemas/v1")
    for filename in SCHEMA_FILES:
        path = schema_dir / filename
        assert path.exists(), filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert payload["type"] in {"object", "array"}


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
