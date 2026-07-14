from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def _pyproject() -> dict:
    return tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_has_packaging_metadata() -> None:
    project = _pyproject()["project"]

    assert project["name"] == "doctor-link"
    assert project["version"] == "0.4.0"
    assert project["license"] == "MIT"
    assert "Development Status :: 4 - Beta" in project["classifiers"]
    assert "Programming Language :: Python :: 3.10" in project["classifiers"]
    assert "Programming Language :: Python :: 3.12" in project["classifiers"]
    assert "Programming Language :: Python :: 3.13" in project["classifiers"]
    assert "Programming Language :: Python :: 3.14" in project["classifiers"]
    assert project["urls"]["Repository"] == "https://github.com/linkyang01/doctor-link"


def test_console_script_uses_explicit_entrypoint() -> None:
    scripts = _pyproject()["project"]["scripts"]

    assert scripts["doctor-link"] == "doctor_link.entrypoint:main"


def test_package_data_and_license_files_exist() -> None:
    payload = _pyproject()

    assert Path("LICENSE").exists()
    assert Path("doctor_link/py.typed").exists()
    assert payload["tool"]["setuptools"]["package-data"]["doctor_link"] == ["py.typed"]


def test_dev_quality_and_security_tools_are_declared() -> None:
    payload = _pyproject()
    dev = " ".join(payload["project"]["optional-dependencies"]["dev"]).lower()

    assert "pytest-cov" in dev
    assert "ruff" in dev
    assert "bandit" in dev
    assert "pip-audit" in dev
    assert "twine" in dev
    assert payload["tool"]["coverage"]["report"]["fail_under"] >= 85


def test_source_distribution_manifest_covers_delivery_assets() -> None:
    manifest = Path("MANIFEST.in").read_text(encoding="utf-8")

    assert "include SECURITY.md" in manifest
    assert "recursive-include schemas *.json" in manifest
    assert "recursive-include scripts" in manifest
    assert "recursive-include docs" in manifest
    assert "prune examples/basic-project/.doctor-link" in manifest
    assert "global-exclude *.py[cod]" in manifest
    assert Path("scripts/validate_distribution_contents.py").exists()


def test_installation_docs_cover_build_and_boundaries() -> None:
    docs = Path("docs/installation.md").read_text(encoding="utf-8").lower()

    assert "python -m pip install -e ." in docs
    assert "python -m build" in docs
    assert "do not publish to pypi without explicit authorization" in docs
