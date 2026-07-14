from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_validator():
    path = Path("scripts/validate_public_projects.py")
    spec = importlib.util.spec_from_file_location("doctor_link_public_project_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_project_manifest_is_pinned_and_cross_language() -> None:
    validator = _load_validator()
    payload = validator.load_manifest(Path("examples/public-project-validation/projects.json"))
    projects = payload["projects"]

    assert len(projects) == 6
    assert {item["language"] for item in projects} == {"python", "javascript"}
    assert len({item["url"] for item in projects}) == 6
    assert all(len(item["commit"]) == 40 for item in projects)
    assert all(item["url"].startswith("https://github.com/") for item in projects)
