from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.user_assertion_manager import add_user_assertion


def _package(tmp_path: Path) -> Path:
    scan = scan_library(tmp_path)
    plan = generate_test_plan(scan)
    event = event_from_scan(scan, plan, project="demo")
    package = build_diagnostic_package(event, tmp_path / "DoctorReports")
    return package.root_dir


def test_add_user_assertion_updates_package_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")
    package_dir = _package(tmp_path)

    assertion = add_user_assertion(
        package_dir,
        user_statement="App crashes on startup",
        expected_behavior="Starts normally",
        actual_behavior="Traceback on import",
        why_user_thinks_it_is_wrong="Regression after config change",
        next_ai_instruction="Inspect config loader first",
    )

    assertions = json.loads((package_dir / "user-assertions.json").read_text(encoding="utf-8"))
    assert len(assertions) == 1
    assert assertions[0]["user_statement"] == "App crashes on startup"
    assert assertion.assertion_id

    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert report["problem_map"]["human_confirmed_problem"] == "App crashes on startup"
    assert "App crashes on startup" in (package_dir / "summary.md").read_text(encoding="utf-8")
    assert "Human-confirmed issue" in (package_dir / "problem-map.md").read_text(encoding="utf-8")
    assert "Human-confirmed issue override" in (package_dir / "ai-task.md").read_text(encoding="utf-8")


def test_add_user_assertion_requires_existing_package(tmp_path: Path) -> None:
    missing = tmp_path / "missing-package"
    try:
        add_user_assertion(missing, user_statement="broken")
    except FileNotFoundError as exc:
        assert "Diagnostic package not found" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")