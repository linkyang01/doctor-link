from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.cli import main
from doctor_link.core.diagnosis_strategy import load_diagnosis_strategy, validate_diagnosis_strategy


def _write_strategy(root: Path, content: str) -> Path:
    strategy_dir = root / ".doctorlink"
    strategy_dir.mkdir(parents=True, exist_ok=True)
    path = strategy_dir / "diagnosis.yml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_valid_diagnosis_strategy(tmp_path: Path) -> None:
    _write_strategy(
        tmp_path,
        """
project_type: python
default_commands:
  - pytest
evidence_rules:
  - logs/*.log
verification_rules:
  - pytest
excluded_paths:
  - .venv/
""",
    )

    result = load_diagnosis_strategy(tmp_path)

    assert result.is_valid
    assert result.strategy is not None
    assert result.strategy.project_type == "python"
    assert result.strategy.default_commands == ["pytest"]
    assert result.strategy.evidence_rules == ["logs/*.log"]
    assert result.strategy.verification_rules == ["pytest"]
    assert result.strategy.excluded_paths == [".venv/"]


def test_missing_strategy_uses_defaults_with_warning(tmp_path: Path) -> None:
    result = load_diagnosis_strategy(tmp_path)

    assert result.is_valid
    assert result.strategy is not None
    assert result.strategy.project_type == "generic"
    assert result.warnings


def test_invalid_strategy_type_fails(tmp_path: Path) -> None:
    _write_strategy(tmp_path, "- not\n- mapping\n")

    result = load_diagnosis_strategy(tmp_path)

    assert not result.is_valid
    assert any("mapping" in item for item in result.errors)


def test_strategy_validation_warns_for_missing_commands() -> None:
    result = validate_diagnosis_strategy({"project_type": "python"})

    assert result.is_valid
    assert "No default_commands configured" in result.warnings
    assert "No verification_rules configured" in result.warnings


def test_strategy_validate_cli_outputs_json(tmp_path: Path) -> None:
    _write_strategy(
        tmp_path,
        """
project_type: python
default_commands:
  - pytest
verification_rules:
  - pytest
""",
    )
    runner = CliRunner()

    result = runner.invoke(main, ["strategy", "validate", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["is_valid"] is True
    assert payload["strategy"]["project_type"] == "python"


def test_strategy_validate_cli_fails_on_invalid_yaml(tmp_path: Path) -> None:
    _write_strategy(tmp_path, "project_type: [unterminated")
    runner = CliRunner()

    result = runner.invoke(main, ["strategy", "validate", str(tmp_path)])

    assert result.exit_code != 0
    assert "validation failed" in result.output.lower()
