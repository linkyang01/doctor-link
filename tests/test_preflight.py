from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.preflight import run_preflight
from doctor_link.entrypoint import main


def _write_valid_project(root: Path) -> None:
    config = root / ".doctorlink"
    config.mkdir()
    (config / "doctorlink.yml").write_text("project:\n  name: demo\n", encoding="utf-8")
    (config / "collect.yml").write_text(
        "collect:\n  commands:\n    - python --version\n",
        encoding="utf-8",
    )
    (config / "package.yml").write_text("package:\n  output_dir: DoctorReports\n", encoding="utf-8")
    (config / "verification.yml").write_text(
        "verification:\n  required_signals:\n    - test_records\n",
        encoding="utf-8",
    )
    (config / "diagnosis.yml").write_text(
        "project_type: python\ndefault_commands:\n  - python --version\nverification_rules:\n  - python --version\n",
        encoding="utf-8",
    )
    (config / "reproduce.yml").write_text("reproductions: []\n", encoding="utf-8")
    (config / "test-matrix.yml").write_text("jobs: []\n", encoding="utf-8")


def test_preflight_passes_or_warns_without_running_commands(tmp_path: Path) -> None:
    _write_valid_project(tmp_path)

    report = run_preflight(tmp_path)

    assert report.status in {"passed", "warning"}
    assert report.blocking_count == 0
    commands = next(check for check in report.checks if check.check_id == "configured-commands")
    assert commands.status == "passed"
    assert "Reviewed 1 configured command" in commands.message


def test_preflight_blocks_unsafe_repository_command(tmp_path: Path) -> None:
    _write_valid_project(tmp_path)
    marker = tmp_path / "must-not-exist"
    (tmp_path / ".doctorlink" / "reproduce.yml").write_text(
        f"reproductions:\n  - id: unsafe\n    title: unsafe\n    kind: command\n    command: python --version; touch {marker}\n",
        encoding="utf-8",
    )

    report = run_preflight(tmp_path)

    assert report.status == "blocked"
    assert not marker.exists()
    assert any(check.check_id == "configured-commands" and check.status == "blocked" for check in report.checks)


def test_preflight_cli_json_is_machine_readable(tmp_path: Path) -> None:
    _write_valid_project(tmp_path)

    result = CliRunner().invoke(main, ["preflight", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["blocking_count"] == 0
    assert payload["checks"]


def test_preflight_cli_blocks_invalid_config(tmp_path: Path) -> None:
    _write_valid_project(tmp_path)
    (tmp_path / ".doctorlink" / "collect.yml").write_text("collect: [unterminated", encoding="utf-8")

    result = CliRunner().invoke(main, ["preflight", str(tmp_path), "--json"])

    assert result.exit_code != 0
    assert '"status": "blocked"' in result.output
