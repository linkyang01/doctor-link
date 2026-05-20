from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.p4_cli import main


def _write_project_config(root: Path) -> None:
    cfg = root / ".doctorlink"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "diagnosis.yml").write_text(
        """
project_type: python
default_commands:
  - python --version
verification_rules:
  - pytest
excluded_paths:
  - .git/
""",
        encoding="utf-8",
    )
    (cfg / "test-matrix.yml").write_text(
        """
jobs:
  - id: smoke-pass
    title: smoke pass
    command: python -c "print('ok')"
    required: true
""",
        encoding="utf-8",
    )
    (cfg / "reproduce.yml").write_text(
        """
reproductions:
  - id: repro-pass
    title: reproduction pass
    kind: command
    command: python -c "print('repro')"
""",
        encoding="utf-8",
    )


def _package_from_output(output: str, prefix: str) -> Path:
    line = next(item for item in output.splitlines() if item.startswith(prefix))
    return Path(line.split(":", 1)[1].strip())


def test_p4_pipeline_smoke(tmp_path: Path) -> None:
    _write_project_config(tmp_path)
    reports = tmp_path / "DoctorReports"
    runner = CliRunner()

    strategy = runner.invoke(main, ["strategy", "validate", str(tmp_path), "--json"])
    assert strategy.exit_code == 0, strategy.output
    assert json.loads(strategy.output)["is_valid"] is True

    before = runner.invoke(
        main,
        ["diagnose", "before", "--project", "Smoke", "--summary", "before", "--out", str(reports)],
    )
    assert before.exit_code == 0, before.output
    before_package = _package_from_output(before.output, "Created before package:")

    test_run = runner.invoke(
        main,
        ["test", "run", str(tmp_path), "--job", "smoke-pass", "--package-dir", str(before_package), "--json"],
    )
    assert test_run.exit_code == 0, test_run.output
    assert json.loads(test_run.output)[0]["status"] == "passed"

    repro = runner.invoke(
        main,
        ["reproduce", "run", "repro-pass", str(tmp_path), "--package-dir", str(before_package), "--json"],
    )
    assert repro.exit_code == 0, repro.output
    assert json.loads(repro.output)["status"] == "passed"

    after = runner.invoke(
        main,
        [
            "diagnose",
            "after",
            "--project",
            "Smoke",
            "--summary",
            "after",
            "--before-package",
            str(before_package),
            "--out",
            str(reports),
        ],
    )
    assert after.exit_code == 0, after.output
    after_package = _package_from_output(after.output, "Created after package:")

    verify = runner.invoke(main, ["diagnose", "verify", str(after_package), "--json"])
    assert verify.exit_code == 0, verify.output
    verify_payload = json.loads(verify.output)
    assert verify_payload["comparison_status"] == "generated"
    assert verify_payload["success"] is False

    health = runner.invoke(main, ["health", str(reports), "--json"])
    assert health.exit_code == 0, health.output
    health_payload = json.loads(health.output)
    assert health_payload["package_count"] == 2
    assert health_payload["status"] == "needs_attention"
