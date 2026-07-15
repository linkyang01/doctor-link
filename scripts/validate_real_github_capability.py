#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "doctor-link-real-github-capability-v1"


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios")
    if payload.get("schema") != SCHEMA or not isinstance(scenarios, list):
        raise ValueError("Unsupported real-GitHub capability manifest")
    return scenarios


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 240) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)


def _git(root: Path, *args: str) -> str:
    completed = _run(["git", *args], cwd=root, timeout=30)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Git command failed")
    return completed.stdout.strip()


def validate_scenario(scenario: dict[str, Any], workspace: Path, doctor_link: str) -> dict[str, Any]:
    root = workspace / str(scenario["directory"])
    expected_commit = str(scenario["commit"])
    if _git(root, "rev-parse", "HEAD") != expected_commit:
        raise RuntimeError(f"{scenario['name']}: repository is not at {expected_commit}")
    initial_status = _git(root, "status", "--porcelain")
    baseline = _run([str(item) for item in scenario["baseline_command"]], cwd=root)
    if baseline.returncode != 0:
        raise RuntimeError(f"{scenario['name']}: native baseline failed before mutation: {baseline.stderr[-800:]}")

    mutation = scenario["mutation"]
    target = root / str(mutation["path"])
    original = target.read_text(encoding="utf-8")
    before = str(mutation["before"])
    after = str(mutation["after"])
    if original.count(before) != 1:
        raise RuntimeError(f"{scenario['name']}: mutation anchor was not unique")

    env = dict(os.environ)
    prefix = scenario.get("doctor_path_prefix")
    if prefix:
        env["PATH"] = str(root / str(prefix)) + os.pathsep + env.get("PATH", "")
    try:
        target.write_text(original.replace(before, after, 1), encoding="utf-8")
        reproduce = _run(
            [
                doctor_link,
                "reproduce",
                "suggest",
                str(root),
                "--problem",
                str(scenario["problem"]),
                "--validate",
                "--timeout",
                "180",
                "--max-candidates",
                "3",
                "--json",
            ],
            cwd=root,
            env=env,
        )
        reproduction = json.loads(reproduce.stdout)
        selected = reproduction.get("selected_command")
        if reproduction.get("status") != "reproduced" or not selected:
            raise RuntimeError(f"{scenario['name']}: Doctor link did not reproduce the injected fault")

        explain = _run(
            [
                doctor_link,
                "explain",
                str(root),
                "--problem",
                str(scenario["problem"]),
                "--test-command",
                str(selected),
                "--command-timeout",
                "180",
                "--verify-hypothesis",
                "--json",
            ],
            cwd=root,
            env=env,
        )
        explanation = json.loads(explain.stdout)
        hints = list((explanation.get("analysis") or {}).get("hints") or [])
        expected_hint = str(scenario["expected_hint"])
        hint_rank = next(
            (index for index, hint in enumerate(hints, start=1) if expected_hint in (hint.get("candidate_paths") or [])),
            None,
        )
        expected_hint_item = next(
            (hint for hint in hints if expected_hint in (hint.get("candidate_paths") or [])),
            {},
        )
        locations = list(expected_hint_item.get("locations") or [])
        expected_line = int(scenario["expected_line"])
        expected_function = str(scenario["expected_function"])
        location_match = any(
            item.get("path") == expected_hint
            and item.get("line") == expected_line
            and item.get("function") == expected_function
            for item in locations
        )
        failures = list((explanation.get("analysis") or {}).get("failures") or [])
        structured_failure = any(
            item.get("expected") is not None or item.get("actual") is not None or item.get("frames")
            for item in failures
        )
        hypothesis = dict(explanation.get("hypothesis_verification") or {})
        passed = (
            explain.returncode == 0
            and explanation.get("worktree_changed") is False
            and hint_rank == 1
            and location_match
            and structured_failure
            and hypothesis.get("status") == "confirmed"
            and hypothesis.get("restored") is True
            and hypothesis.get("worktree_unchanged") is True
        )
        return {
            "name": scenario["name"],
            "repository": scenario["repository"],
            "commit": expected_commit,
            "language": scenario["language"],
            "baseline_return_code": baseline.returncode,
            "reproduction_status": reproduction.get("status"),
            "selected_command": selected,
            "explain_status": explanation.get("status"),
            "expected_hint": expected_hint,
            "expected_hint_rank": hint_rank,
            "expected_line": expected_line,
            "expected_function": expected_function,
            "location_match": location_match,
            "structured_failure": structured_failure,
            "hypothesis_status": hypothesis.get("status"),
            "hypothesis_restored": hypothesis.get("restored"),
            "worktree_changed_by_checks": explanation.get("worktree_changed"),
            "passed": passed,
        }
    finally:
        target.write_text(original, encoding="utf-8")
        final_status = _git(root, "status", "--porcelain")
        if final_status != initial_status:
            raise RuntimeError(f"{scenario['name']}: harness did not restore the initial Git status")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Doctor link on prepared, pinned real GitHub projects.")
    parser.add_argument("--manifest", type=Path, default=Path("examples/real-github-capability-validation/scenarios.json"))
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--doctor-link", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    results = [validate_scenario(item, args.workspace.resolve(), args.doctor_link) for item in load_scenarios(args.manifest)]
    payload = {
        "schema": "doctor-link-real-github-capability-result-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(results),
        "passed_count": sum(bool(item["passed"]) for item in results),
        "results": results,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Real GitHub capability validation", "", f"Passed: {payload['passed_count']}/{payload['scenario_count']}", ""]
    lines.extend(
        f"- {'PASS' if item['passed'] else 'FAIL'} `{item['name']}`: reproduction={item['reproduction_status']}, "
        f"hint=`{item['expected_hint']}:{item['expected_line']}` function=`{item['expected_function']}` "
        f"rank={item['expected_hint_rank']}, location_match={item['location_match']}, "
        f"structured_failure={item['structured_failure']}, hypothesis={item['hypothesis_status']}, "
        f"restored={item['hypothesis_restored']}, checks_changed_tree={item['worktree_changed_by_checks']}"
        for item in results
    )
    (args.out / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Real GitHub capability validation: {payload['passed_count']}/{payload['scenario_count']}")
    if payload["passed_count"] != payload["scenario_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
