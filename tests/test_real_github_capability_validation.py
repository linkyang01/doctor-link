from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_validator():
    path = Path("scripts/validate_real_github_capability.py")
    spec = importlib.util.spec_from_file_location("doctor_link_real_github_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_real_github_scenarios_are_pinned_cross_language_and_reversible() -> None:
    validator = _load_validator()
    scenarios = validator.load_scenarios(Path("examples/real-github-capability-validation/scenarios.json"))

    assert len(scenarios) == 3
    assert {item["language"] for item in scenarios} == {"python", "javascript"}
    assert len({item["repository"] for item in scenarios}) == 3
    assert all(len(item["commit"]) == 40 for item in scenarios)
    assert all(item["mutation"]["before"] != item["mutation"]["after"] for item in scenarios)
    assert all(item["expected_hint"] == item["mutation"]["path"] for item in scenarios)
