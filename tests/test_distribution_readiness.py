from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

from click.testing import CliRunner

from doctor_link.p4_cli import main
from doctor_link.core.distribution_readiness import write_distribution_readiness_report


def _write_pyproject(project_root: Path) -> None:
    (project_root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "doctor-link-demo"',
                'version = "0.1.0"',
                'description = "Demo package"',
                'readme = "README.md"',
                'requires-python = ">=3.10"',
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "README.md").write_text("# Demo\n", encoding="utf-8")


def _write_wheel(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "doctor_link_demo-0.1.0.dist-info/METADATA",
            "Name: doctor-link-demo\nVersion: 0.1.0\nSummary: Demo package\nRequires-Python: >=3.10\n",
        )
        archive.writestr("doctor_link_demo-0.1.0.dist-info/WHEEL", "Wheel-Version: 1.0\n")
        archive.writestr(
            "doctor_link_demo-0.1.0.dist-info/RECORD",
            "doctor_link_demo-0.1.0.dist-info/METADATA,,\n",
        )


def _write_sdist(path: Path, project_root: Path) -> None:
    pyproject = project_root / "pkg" / "pyproject.toml"
    pkg_info = project_root / "pkg" / "PKG-INFO"
    pyproject.parent.mkdir(parents=True, exist_ok=True)
    pyproject.write_text("[project]\n", encoding="utf-8")
    pkg_info.write_text(
        "Name: doctor-link-demo\nVersion: 0.1.0\nSummary: Demo package\nRequires-Python: >=3.10\n",
        encoding="utf-8",
    )
    with tarfile.open(path, "w:gz") as archive:
        archive.add(pyproject, arcname="doctor-link-demo-0.1.0/pyproject.toml")
        archive.add(pkg_info, arcname="doctor-link-demo-0.1.0/PKG-INFO")


def _write_dist(project_root: Path) -> Path:
    dist = project_root / "dist"
    dist.mkdir()
    _write_wheel(dist / "doctor_link_demo-0.1.0-py3-none-any.whl")
    _write_sdist(dist / "doctor-link-demo-0.1.0.tar.gz", project_root)
    return dist


def test_distribution_readiness_report_passes_with_valid_artifacts(tmp_path: Path) -> None:
    _write_pyproject(tmp_path)
    dist = _write_dist(tmp_path)
    report = write_distribution_readiness_report(tmp_path, dist_dir=dist)

    out = Path(report.output_dir)
    assert report.status == "passed"
    assert report.blocking_count == 0
    assert len(report.artifacts) == 2
    assert (out / "distribution-report.json").exists()
    assert (out / "distribution-report.md").exists()
    assert (out / "distribution-manifest.json").exists()
    assert (out / "checksums.sha256").exists()
    assert (out / "target-environment.json").exists()


def test_distribution_readiness_blocks_missing_artifacts(tmp_path: Path) -> None:
    _write_pyproject(tmp_path)
    report = write_distribution_readiness_report(tmp_path)

    assert report.status == "blocked"
    assert report.blocking_count >= 3
    assert any(item["id"] == "dist-dir-present" for item in report.checklist)


def test_distribution_check_cli_json(tmp_path: Path) -> None:
    _write_pyproject(tmp_path)
    dist = _write_dist(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "distribution",
            "check",
            str(tmp_path),
            "--dist",
            str(dist),
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"status": "passed"' in result.output


def test_distribution_check_cli_blocks_invalid_dist(tmp_path: Path) -> None:
    _write_pyproject(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["distribution", "check", str(tmp_path)])

    assert result.exit_code != 0
    assert "Distribution readiness blocked" in result.output
