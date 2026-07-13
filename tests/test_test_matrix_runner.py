from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.test_matrix_runner import load_test_matrix, run_test_matrix
from doctor_link.p4_cli import main


def _write_matrix(root: Path) -> None:
    config = root / ".doctorlink"
    config.mkdir(parents=True, exist_ok=True)
    (config / "test-matrix.yml").write_text(
        """
name: P4 fixture matrix
jobs:
  - id: job-pass
    title: passing job
    command: python -c "print('ok')"
    required: true
    related_verification_steps:
      - pytest
cases:
  - id: legacy-case
    type: informational
""",
        encoding="utf-8",
    )


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Matrix", category="p4", summary="test matrix"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_load_test_matrix_jobs(tmp_path: Path) -> None:
    _write_matrix(tmp_path)

    catalog = load_test_matrix(tmp_path)

    assert len(catalog.jobs) == 1
    assert catalog.jobs[0].job_id == "job-pass"
    assert catalog.jobs[0].command.startswith("python")
    assert catalog.jobs[0].related_verification_steps == ["pytest"]


def test_run_test_matrix_writes_evidence(tmp_path: Path) -> None:
    _write_matrix(tmp_path)
    package_dir = _package(tmp_path)

    results = run_test_matrix(tmp_path, package_dir=package_dir, job_id="job-pass")

    assert len(results) == 1
    assert results[0].status == "passed"
    assert results[0].evidence_id == "test-matrix-job-pass"
    assert (package_dir / "evidence" / "test-results" / "job-pass.json").exists()
    assert "test-matrix-job-pass" in (package_dir / "evidence-list.md").read_text(encoding="utf-8")
    assert "Run test matrix job-pass" in (package_dir / "timeline.md").read_text(encoding="utf-8")


def test_test_matrix_cli_list_json(tmp_path: Path) -> None:
    _write_matrix(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["test", "list", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["jobs"][0]["job_id"] == "job-pass"


def test_test_matrix_cli_run_json(tmp_path: Path) -> None:
    _write_matrix(tmp_path)
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["test", "run", str(tmp_path), "--job", "job-pass", "--package-dir", str(package_dir), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload[0]["status"] == "passed"
    assert payload[0]["evidence_id"] == "test-matrix-job-pass"


def test_test_matrix_rejects_shell_redirection(tmp_path: Path) -> None:
    marker = tmp_path / "should-not-exist.txt"
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "test-matrix.yml").write_text(
        f"""jobs:
  - id: unsafe
    title: unsafe test
    command: python -c \"print('unsafe')\" > {marker}
""",
        encoding="utf-8",
    )

    results = run_test_matrix(tmp_path, job_id="unsafe")

    assert results[0].status == "failed"
    assert "Unsupported shell operator" in results[0].stderr
    assert not marker.exists()
