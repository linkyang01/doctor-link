from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from doctor_link.adapters.registry import detect_adapter
from doctor_link.p4_cli import main


EXAMPLE_PATHS = [
    "examples/python-api-bug/.doctorlink/diagnosis.yml",
    "examples/media-playback-library/.doctorlink/diagnosis.yml",
]


def test_phase_b_example_configs_exist() -> None:
    for relative in EXAMPLE_PATHS:
        assert Path(relative).exists(), relative


def test_python_api_bug_full_diagnose(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "diagnose-now",
            "examples/python-api-bug",
            "--full",
            "--reports",
            str(tmp_path / "DoctorReports"),
            "--summary",
            "GET /users returns 500",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "python-api-bug" in result.output or "Diagnostic workflow complete." in result.output


def test_media_library_vly_proof_go(tmp_path: Path) -> None:
    runner = CliRunner()
    reports = tmp_path / "DoctorReports"
    report = runner.invoke(main, ["report", "examples/media-playback-library", "--out", str(reports)])
    assert report.exit_code == 0, report.output
    package_line = next(line for line in report.output.splitlines() if line.startswith("Generated diagnostic package:"))
    package_dir = Path(package_line.split(":", 1)[1].strip())

    proof = runner.invoke(main, ["vly-proof", "examples/media-playback-library", "--package-dir", str(package_dir), "--json"])
    assert proof.exit_code == 0, proof.output
    assert detect_adapter(Path("examples/media-playback-library")) is not None