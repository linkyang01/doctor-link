from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_runner():
    path = Path("examples/failure-mode-validation/run.py")
    spec = importlib.util.spec_from_file_location("doctor_link_failure_mode_validation", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_failure_mode_harness_covers_required_scenarios(tmp_path: Path) -> None:
    runner = _load_runner()
    results = runner.run_scenarios(tmp_path / "workspace", tmp_path / "sessions")
    by_id = {item.scenario_id: item for item in results}

    required = {
        "multi_file_verified_repair",
        "wrong_ai_fix_returns_failed",
        "multi_file_hash_protection",
        "allow_verification_changes_review_required",
        "off_by_one_assist_reproduction",
        "public_nodejs_corpus_pins",
    }
    assert required.issubset(by_id)
    assert all(item.passed for item in results), [(item.scenario_id, item.actual_status) for item in results if not item.passed]


def test_failure_mode_cli_writes_receipts(tmp_path: Path) -> None:
    runner = _load_runner()
    out = tmp_path / "out"
    # Invoke main via argv simulation
    old = sys.argv
    try:
        sys.argv = ["run.py", "--out", str(out)]
        runner.main()
    finally:
        sys.argv = old

    payload = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert payload["schema"] == "doctor-link-failure-mode-validation-v1"
    assert payload["passed_count"] == payload["scenario_count"]
    assert (out / "results.md").is_file()
