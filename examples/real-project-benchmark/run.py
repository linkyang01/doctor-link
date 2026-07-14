#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    domain: str
    problem: str
    input_value: object
    expected: object
    python_broken: str
    javascript_broken: str


DOMAINS = [
    Scenario("checkout", "payments", "Checkout duplicates a payment charge", 10, 10, "value * 2", "value * 2"),
    Scenario("authorization", "security", "Authorization allows a viewer to perform an admin action", "viewer", False, "True", "true"),
    Scenario("cache", "infrastructure", "Cache returns a stale previous value", 4, 4, "value - 1", "value - 1"),
    Scenario("unicode", "data", "Unicode text loses the final character", "米穗🌾", "米穗🌾", "value[:-1]", "value.slice(0, -2)"),
    Scenario("concurrency", "reliability", "Concurrent update loses one committed write", 2, 2, "value - 1", "value - 1"),
    Scenario("config", "configuration", "Config false is interpreted as enabled", "false", False, "bool(value)", "Boolean(value)"),
    Scenario("retry", "network", "Retry accounting adds an extra attempt", 3, 3, "value + 1", "value + 1"),
    Scenario("pagination", "api", "Pagination skips the first item of the next page", 20, 20, "value + 1", "value + 1"),
    Scenario("timezone", "time", "Timezone conversion subtracts the offset twice", 8, 8, "value - 8", "value - 8"),
    Scenario("transaction", "database", "Transaction rollback loses the original balance", 100, 100, "0", "0"),
    Scenario("path-security", "security", "Path traversal is accepted outside the workspace", "../secret", False, "True", "true"),
    Scenario("rate-limit", "api", "Rate limit rejects the request at the allowed boundary", 5, True, "value < 5", "value < 5"),
]


def materialize_corpus(workspace: Path) -> list[dict[str, object]]:
    workspace.mkdir(parents=True, exist_ok=True)
    manifest_scenarios: list[dict[str, object]] = []
    for language in ("python", "javascript"):
        for scenario in DOMAINS:
            scenario_id = f"{language}-{scenario.scenario_id}"
            root = workspace / scenario_id
            root.mkdir(parents=True)
            if language == "python":
                _write_python(root, scenario)
            else:
                _write_javascript(root, scenario)
            _initialize_git(root)
            manifest_scenarios.append(
                {
                    "id": scenario_id,
                    "project_root": str(root),
                    "problem": scenario.problem,
                    "auto_reproduce": True,
                    "expected_status": "approval_required",
                }
            )
    return manifest_scenarios


def _write_python(root: Path, scenario: Scenario) -> None:
    tests = root / "tests"
    tests.mkdir()
    (root / "pyproject.toml").write_text(
        f"[project]\nname='doctor-link-{scenario.scenario_id}'\nversion='0.0.1'\n",
        encoding="utf-8",
    )
    (root / "service.py").write_text(
        f"def handle(value):\n    return {scenario.python_broken}\n",
        encoding="utf-8",
    )
    (tests / f"test_{scenario.scenario_id.replace('-', '_')}.py").write_text(
        "from service import handle\n\n"
        f"def test_{scenario.scenario_id.replace('-', '_')}():\n"
        f"    assert handle({scenario.input_value!r}) == {scenario.expected!r}\n",
        encoding="utf-8",
    )
    (root / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n", encoding="utf-8")


def _write_javascript(root: Path, scenario: Scenario) -> None:
    tests = root / "test"
    tests.mkdir()
    (root / "package.json").write_text(
        json.dumps(
            {
                "name": f"doctor-link-{scenario.scenario_id}",
                "private": True,
                "scripts": {"test": "node --test"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "service.js").write_text(
        f"exports.handle = (value) => {scenario.javascript_broken};\n",
        encoding="utf-8",
    )
    (tests / f"{scenario.scenario_id}.test.js").write_text(
        "const test = require('node:test');\n"
        "const assert = require('node:assert/strict');\n"
        "const { handle } = require('../service');\n"
        f"test({json.dumps(scenario.problem)}, () => assert.deepEqual(handle({json.dumps(scenario.input_value, ensure_ascii=False)}), {json.dumps(scenario.expected, ensure_ascii=False)}));\n",
        encoding="utf-8",
    )
    (root / ".gitignore").write_text("node_modules/\n", encoding="utf-8")


def _initialize_git(root: Path) -> None:
    commands = (
        ("git", "init", "-b", "main"),
        ("git", "config", "user.name", "Doctor link Benchmark"),
        ("git", "config", "user.email", "benchmark@example.invalid"),
        ("git", "add", "."),
        ("git", "commit", "-m", "benchmark fixture"),
    )
    for command in commands:
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(f"Could not initialize {root.name}: {completed.stderr}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 24 repeatable real-project-style automatic reproduction scenarios.")
    parser.add_argument("--doctor-link", default=shutil.which("doctor-link"))
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    if not args.doctor_link:
        parser.error("doctor-link was not found; install it or pass --doctor-link")
    workspace = (args.workspace or Path(tempfile.mkdtemp(prefix="doctor-link-real-benchmark-"))).resolve()
    output = (args.out or workspace / "results").resolve()
    scenarios = materialize_corpus(workspace / "projects")
    manifest = workspace / "benchmark.json"
    manifest.write_text(
        json.dumps({"schema": "doctor-link-benchmark-v1", "scenarios": scenarios}, indent=2),
        encoding="utf-8",
    )
    completed = subprocess.run(
        [args.doctor_link, "benchmark", str(manifest), "--out", str(output), "--json"],
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    print(f"24-scenario benchmark passed: {output / 'benchmark-result.md'}")


if __name__ == "__main__":
    main()
