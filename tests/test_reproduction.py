from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.reproduction import load_reproduction_catalog, run_reproduction
from doctor_link.p4_cli import main


def _write_reproduce(root: Path) -> None:
    config = root / ".doctorlink"
    config.mkdir(parents=True, exist_ok=True)
    (config / "reproduce.yml").write_text(
        """
reproductions:
  - id: repro-pass
    title: passing command
    kind: command
    command: python -c "print('ok')"
    expected: ok
  - id: repro-manual
    title: manual case
    kind: manual
    description: check manually
""",
        encoding="utf-8",
    )


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Repro", category="p4", summary="reproduction test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_load_reproduction_catalog(tmp_path: Path) -> None:
    _write_reproduce(tmp_path)

    catalog = load_reproduction_catalog(tmp_path)

    assert len(catalog.entries) == 2
    assert catalog.entries[0].reproduction_id == "repro-pass"
    assert catalog.entries[0].kind == "command"
    assert catalog.entries[1].kind == "manual"


def test_run_reproduction_writes_evidence(tmp_path: Path) -> None:
    _write_reproduce(tmp_path)
    package_dir = _package(tmp_path)

    result = run_reproduction(tmp_path, "repro-pass", package_dir=package_dir)

    assert result.status == "passed"
    assert result.evidence_id == "reproduction-repro-pass"
    assert (package_dir / "evidence" / "reproductions" / "repro-pass.json").exists()
    assert "reproduction-repro-pass" in (package_dir / "evidence-list.md").read_text(encoding="utf-8")
    assert "Run reproduction repro-pass" in (package_dir / "timeline.md").read_text(encoding="utf-8")


def test_reproduce_list_cli_outputs_json(tmp_path: Path) -> None:
    _write_reproduce(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["reproduce", "list", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["entries"][0]["reproduction_id"] == "repro-pass"


def test_reproduce_run_cli_writes_package_evidence(tmp_path: Path) -> None:
    _write_reproduce(tmp_path)
    package_dir = _package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["reproduce", "run", "repro-pass", str(tmp_path), "--package-dir", str(package_dir), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "passed"
    assert payload["evidence_id"] == "reproduction-repro-pass"
