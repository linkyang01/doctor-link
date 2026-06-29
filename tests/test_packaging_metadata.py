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
    assert project["version"] == "0.1.2"
    assert project["license"]["text"] == "MIT"
    assert "Development Status :: 4 - Beta" in project["classifiers"]
    assert "Programming Language :: Python :: 3.10" in project["classifiers"]
    assert "Programming Language :: Python :: 3.12" in project["classifiers"]
    assert project["urls"]["Repository"] == "https://github.com/linkyang01/doctor-link"


def test_console_script_uses_explicit_entrypoint() -> None:
    scripts = _pyproject()["project"]["scripts"]

    assert scripts["doctor-link"] == "doctor_link.entrypoint:main"


def test_package_data_and_license_files_exist() -> None:
    payload = _pyproject()

    assert Path("LICENSE").exists()
    assert Path("doctor_link/py.typed").exists()
    assert payload["tool"]["setuptools"]["package-data"]["doctor_link"] == ["py.typed"]


def test_installation_docs_cover_build_and_boundaries() -> None:
    docs = Path("docs/installation.md").read_text(encoding="utf-8").lower()

    assert "python -m pip install -e ." in docs
    assert "python -m build" in docs
    assert "do not publish to pypi without explicit authorization" in docs