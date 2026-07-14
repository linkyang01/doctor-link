#!/usr/bin/env python3
"""Disposable failure-mode validation harness for Doctor link solve/assist contracts.

Runs offline fixture scenarios (no network, no Codex CLI). Complements the pinned
public-project preflight harness and the 24-scenario real-project corpus.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from doctor_link.core.reproduction_suggester import suggest_reproductions  # noqa: E402
from doctor_link.core.solve import RepairExecution, solve_project  # noqa: E402


@dataclass
class ScenarioResult:
    scenario_id: str
    title: str
    expected_status: str
    actual_status: str
    passed: bool
    details: dict


class ScriptedRepairExecutor:
    name = "scripted"

    def __init__(self, actions: list[Callable[[Path], None]]) -> None:
        self.actions = actions
        self.calls = 0

    def run(self, prompt: str, project_root: Path, timeout_seconds: int) -> RepairExecution:
        action = self.actions[min(self.calls, len(self.actions) - 1)]
        self.calls += 1
        action(project_root)
        return RepairExecution(
            status="completed",
            return_code=0,
            thread_id=f"thread-{self.calls}",
            final_message=f"scripted round {self.calls}",
            event_count=1,
            file_change_events=1,
        )


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _init_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Failure Mode Harness")
    _git(root, "config", "user.email", "failure-mode@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")


def _multi_file_project(workspace: Path, *, broken: bool = True) -> Path:
    root = workspace / "multi-file"
    tests = root / "tests"
    src = root / "src"
    tests.mkdir(parents=True)
    src.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='multi-file'\nversion='0.0.1'\n", encoding="utf-8")
    charge = "total * 2" if broken else "total"
    stock = "count - 1" if broken else "count"
    (src / "billing.py").write_text(
        f"class ChargeEngine:\n    def charge_once(self, total: int) -> int:\n        return {charge}\n",
        encoding="utf-8",
    )
    (src / "inventory.py").write_text(
        f"class StockLedger:\n    def remaining(self, count: int) -> int:\n        return {stock}\n",
        encoding="utf-8",
    )
    (tests / "test_services.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))\n"
        "from billing import ChargeEngine\n"
        "from inventory import StockLedger\n\n"
        "def test_charge_once():\n"
        "    assert ChargeEngine().charge_once(10) == 10\n\n"
        "def test_stock_remaining():\n"
        "    assert StockLedger().remaining(5) == 5\n",
        encoding="utf-8",
    )
    _init_repo(root)
    return root


def _off_by_one_project(workspace: Path) -> Path:
    root = workspace / "off-by-one"
    tests = root / "tests"
    tests.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='off-by-one'\nversion='0.0.1'\n", encoding="utf-8")
    (root / "pager.py").write_text(
        "def page_count(items: int, size: int) -> int:\n"
        "    if size <= 0:\n"
        "        raise ValueError('size')\n"
        "    return (items // size)  # off-by-one: should ceil\n",
        encoding="utf-8",
    )
    (tests / "test_pager.py").write_text(
        "from pager import page_count\n\n"
        "def test_page_count_rounds_up():\n"
        "    assert page_count(10, 3) == 4\n",
        encoding="utf-8",
    )
    _init_repo(root)
    return root


def _pytest_command() -> str:
    return "PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q"


def _fix_multi(root: Path) -> None:
    (root / "src" / "billing.py").write_text(
        "class ChargeEngine:\n    def charge_once(self, total: int) -> int:\n        return total\n",
        encoding="utf-8",
    )
    (root / "src" / "inventory.py").write_text(
        "class StockLedger:\n    def remaining(self, count: int) -> int:\n        return count\n",
        encoding="utf-8",
    )


def _partial_multi_fix(root: Path) -> None:
    # Fixes billing only; inventory remains broken.
    (root / "src" / "billing.py").write_text(
        "class ChargeEngine:\n    def charge_once(self, total: int) -> int:\n        return total\n",
        encoding="utf-8",
    )


def _tamper_tests(root: Path) -> None:
    (root / "tests" / "test_services.py").write_text(
        "def test_charge_once():\n    assert True\n\ndef test_stock_remaining():\n    assert True\n",
        encoding="utf-8",
    )


def run_scenarios(workspace: Path, output: Path) -> list[ScenarioResult]:
    output.mkdir(parents=True, exist_ok=True)
    results: list[ScenarioResult] = []

    multi = _multi_file_project(workspace)
    multi_ok = solve_project(
        multi,
        problem="Billing charges twice and inventory decrements stock",
        test_command=_pytest_command(),
        output_root=output / "multi-file-verified",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix_multi]),
    )
    results.append(
        ScenarioResult(
            scenario_id="multi_file_verified_repair",
            title="Multi-file production repair preserves tests and verifies",
            expected_status="verified",
            actual_status=multi_ok.status,
            passed=multi_ok.status == "verified",
            details={
                "changed_production_files": ["src/billing.py", "src/inventory.py"],
                "protected_inputs_include_tests": any(
                    path.startswith("tests/") for path in multi_ok.protected_verification_inputs
                ),
                "rounds": len(multi_ok.rounds),
            },
        )
    )

    multi_wrong = _multi_file_project(workspace / "wrong")
    multi_fail = solve_project(
        multi_wrong,
        problem="Billing charges twice and inventory decrements stock",
        test_command=_pytest_command(),
        output_root=output / "multi-file-wrong-fix",
        allow_repair=True,
        max_rounds=2,
        repair_executor=ScriptedRepairExecutor([_partial_multi_fix]),
    )
    results.append(
        ScenarioResult(
            scenario_id="wrong_ai_fix_returns_failed",
            title="Partial/wrong AI repair exhausts rounds and returns failed",
            expected_status="failed",
            actual_status=multi_fail.status,
            passed=multi_fail.status == "failed",
            details={"rounds": len(multi_fail.rounds), "executor_style": "partial_multi_file_fix"},
        )
    )

    multi_tamper = _multi_file_project(workspace / "tamper")
    multi_blocked = solve_project(
        multi_tamper,
        problem="Billing charges twice and inventory decrements stock",
        test_command=_pytest_command(),
        output_root=output / "multi-file-tamper",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_tamper_tests]),
    )
    results.append(
        ScenarioResult(
            scenario_id="multi_file_hash_protection",
            title="Test-contract tampering across multi-file project is blocked",
            expected_status="blocked",
            actual_status=multi_blocked.status,
            passed=multi_blocked.status == "blocked"
            and "verification_inputs_modified" in multi_blocked.blockers,
            details={
                "blockers": multi_blocked.blockers,
                "verification_input_changes": multi_blocked.verification_input_changes,
            },
        )
    )

    multi_review = _multi_file_project(workspace / "review")
    review = solve_project(
        multi_review,
        problem="Billing charges twice and inventory decrements stock",
        test_command=_pytest_command(),
        output_root=output / "multi-file-review",
        allow_repair=True,
        allow_verification_changes=True,
        repair_executor=ScriptedRepairExecutor([_tamper_tests]),
    )
    results.append(
        ScenarioResult(
            scenario_id="allow_verification_changes_review_required",
            title="Explicit verification-input changes require human review",
            expected_status="review_required",
            actual_status=review.status,
            passed=review.status == "review_required",
            details={"success": review.success, "changes": review.verification_input_changes},
        )
    )

    off = _off_by_one_project(workspace)
    assist = suggest_reproductions(
        off,
        "Page count is off by one for leftover items",
        validate=True,
    )
    results.append(
        ScenarioResult(
            scenario_id="off_by_one_assist_reproduction",
            title="Assist/suggest reproduces a non-trivial off-by-one logic bug",
            expected_status="reproduced",
            actual_status=assist.status,
            passed=assist.status == "reproduced" and bool(assist.selected_command),
            details={
                "selected_command": assist.selected_command,
                "suggestion_count": len(assist.suggestions),
            },
        )
    )

    public_manifest = ROOT / "examples" / "public-project-validation" / "projects.json"
    payload = json.loads(public_manifest.read_text(encoding="utf-8"))
    projects = payload.get("projects") or []
    languages = {item.get("language") for item in projects if isinstance(item, dict)}
    js_projects = [item.get("name") for item in projects if item.get("language") == "javascript"]
    results.append(
        ScenarioResult(
            scenario_id="public_nodejs_corpus_pins",
            title="Public validation set includes pinned Node.js projects for external demos",
            expected_status="present",
            actual_status="present" if "javascript" in languages and len(js_projects) >= 1 else "missing",
            passed="javascript" in languages and len(js_projects) >= 1 and all(
                isinstance(item.get("commit"), str) and len(item.get("commit", "")) == 40 for item in projects
            ),
            details={"javascript_projects": js_projects, "project_count": len(projects)},
        )
    )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Doctor link failure-mode validation scenarios.")
    parser.add_argument("--out", type=Path, required=True, help="Output directory for receipts.")
    args = parser.parse_args()
    workspace = args.out / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    results = run_scenarios(workspace, args.out / "sessions")
    payload = {
        "schema": "doctor-link-failure-mode-validation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(results),
        "passed_count": sum(item.passed for item in results),
        "results": [asdict(item) for item in results],
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Failure-mode validation",
        "",
        f"Passed: {payload['passed_count']}/{payload['scenario_count']}",
        "",
    ]
    for item in results:
        mark = "PASS" if item.passed else "FAIL"
        lines.append(f"- {mark} `{item.scenario_id}` expected={item.expected_status} actual={item.actual_status}")
    (args.out / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Failure-mode validation: {payload['passed_count']}/{payload['scenario_count']}")
    if payload["passed_count"] != payload["scenario_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
