from __future__ import annotations

import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.conformance import run_conformance_suite
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.p4_cli import main


def test_conformance_suite_scores_expected_cases(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    valid_package = _generated_package(fixtures / "valid", "valid-case")
    backward_package = _generated_package(fixtures / "backward-compatible", "legacy-case")
    _remove_schema_version(backward_package / "doctor-report.json")
    _remove_schema_version(backward_package / "ai-context.json")
    migration_package = _generated_package(fixtures / "migration", "migration-case")
    invalid_package = _generated_package(fixtures / "invalid", "invalid-case")
    (invalid_package / "doctor-report.json").unlink()

    report = run_conformance_suite(fixtures)

    assert report.status == "passed"
    assert report.total_cases == 4
    assert report.passed_cases == 4
    assert report.compatibility_score == 100.0


def test_conformance_cli_writes_report(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    _generated_package(fixtures / "valid", "valid-case")
    output = tmp_path / "conformance-report"
    runner = CliRunner()

    result = runner.invoke(main, ["conformance", "run", str(fixtures), "--out", str(output), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "passed"
    assert (output / "conformance-report.json").exists()
    assert (output / "conformance-report.md").exists()


def _generated_package(group_dir: Path, name: str) -> Path:
    group_dir.mkdir(parents=True, exist_ok=True)
    package = build_diagnostic_package(DiagnosticEvent(project=name, summary="conformance"), group_dir)
    assert package.root_dir is not None
    target = group_dir / name
    shutil.move(str(package.root_dir), target)
    return target


def _remove_schema_version(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("schema_version", None)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
