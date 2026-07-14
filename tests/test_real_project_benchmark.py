from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from doctor_link.core.reproduction_suggester import suggest_reproductions


def _load_runner():
    path = Path("examples/real-project-benchmark/run.py")
    spec = importlib.util.spec_from_file_location("doctor_link_real_project_benchmark", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_real_project_corpus_has_24_cross_language_domain_scenarios(tmp_path: Path) -> None:
    runner = _load_runner()

    scenarios = runner.materialize_corpus(tmp_path / "projects")

    assert len(scenarios) == 24
    assert sum(item["id"].startswith("python-") for item in scenarios) == 12
    assert sum(item["id"].startswith("javascript-") for item in scenarios) == 12
    assert len({item["problem"] for item in scenarios}) == 12


def test_every_corpus_scenario_is_automatically_reproduced(tmp_path: Path) -> None:
    runner = _load_runner()
    scenarios = runner.materialize_corpus(tmp_path / "projects")

    results = [
        suggest_reproductions(Path(str(item["project_root"])), str(item["problem"]), validate=True)
        for item in scenarios
    ]

    assert all(result.status == "reproduced" for result in results)
    assert all(result.selected_command for result in results)
