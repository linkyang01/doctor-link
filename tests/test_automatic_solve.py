from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from click.testing import CliRunner
import pytest

from doctor_link.core.command_runner import CommandResult
from doctor_link.core.solve import (
    CodexRepairExecutor,
    RepairExecution,
    detect_project_type,
    discover_workspace_packages,
    discover_solve_commands,
    resolve_solve_target,
    resume_solve_session,
    solve_project,
)
from doctor_link.entrypoint import main


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
            event_count=3,
            file_change_events=1,
            raw_stdout=json.dumps({"type": "thread.started", "thread_id": f"thread-{self.calls}"}) + "\n",
        )


class FailingRepairExecutor:
    name = "failing"

    def run(self, prompt: str, project_root: Path, timeout_seconds: int) -> RepairExecution:
        raise RuntimeError("provider crashed")


class SimulatedInterruption(BaseException):
    pass


class InterruptingRepairExecutor:
    name = "interrupting"

    def run(self, prompt: str, project_root: Path, timeout_seconds: int) -> RepairExecution:
        raise SimulatedInterruption("process stopped")


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _python_project(tmp_path: Path, *, broken: bool = True) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        "[project]\nname = 'solve-fixture'\nversion = '0.0.1'\n",
        encoding="utf-8",
    )
    value = "a - b" if broken else "a + b"
    (root / "calculator.py").write_text(
        f"def add(a: int, b: int) -> int:\n    return {value}\n",
        encoding="utf-8",
    )
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.name", "Doctor link Test")
    _run_git(root, "config", "user.email", "doctor-link@example.invalid")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "fixture")
    return root


def _javascript_project(tmp_path: Path, *, broken: bool = True, scripts: bool = True) -> Path:
    root = tmp_path / "project"
    tests = root / "tests"
    tests.mkdir(parents=True)
    package: dict[str, object] = {"name": "solve-js-fixture", "version": "0.0.1", "private": True}
    if scripts:
        package["scripts"] = {"test": "node --test"}
    (root / "package.json").write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    expression = "a - b" if broken else "a + b"
    (root / "calculator.js").write_text(f"exports.add = (a, b) => {expression};\n", encoding="utf-8")
    (tests / "calculator.test.js").write_text(
        "const test = require('node:test');\n"
        "const assert = require('node:assert/strict');\n"
        "const { add } = require('../calculator');\n\n"
        "test('add returns a sum', () => {\n"
        "  assert.equal(add(2, 3), 5);\n"
        "});\n",
        encoding="utf-8",
    )
    (root / ".gitignore").write_text("node_modules/\ncoverage/\n", encoding="utf-8")
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.name", "Doctor link Test")
    _run_git(root, "config", "user.email", "doctor-link@example.invalid")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "fixture")
    return root


def _javascript_workspace(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "workspace"
    package_root = root / "packages" / "calculator"
    tests = package_root / "tests"
    tests.mkdir(parents=True)
    (root / "package.json").write_text(
        json.dumps({"name": "workspace", "private": True, "workspaces": ["packages/*"]}),
        encoding="utf-8",
    )
    (package_root / "package.json").write_text(
        json.dumps({"name": "calculator", "private": True, "scripts": {"test": "node --test"}}),
        encoding="utf-8",
    )
    (package_root / "calculator.js").write_text("exports.add = (a, b) => a - b;\n", encoding="utf-8")
    (tests / "calculator.test.js").write_text(
        "const test = require('node:test');\n"
        "const assert = require('node:assert/strict');\n"
        "const { add } = require('../calculator');\n"
        "test('adds', () => assert.equal(add(2, 3), 5));\n",
        encoding="utf-8",
    )
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.name", "Doctor link Test")
    _run_git(root, "config", "user.email", "doctor-link@example.invalid")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "fixture")
    return root, package_root


def _check_command() -> str:
    return 'python -c "from calculator import add; assert add(2, 3) == 5"'


def _fix(root: Path) -> None:
    (root / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )


def _fix_javascript(root: Path) -> None:
    (root / "calculator.js").write_text("exports.add = (a, b) => a + b;\n", encoding="utf-8")


def _tamper_javascript_contract(root: Path) -> None:
    (root / "tests" / "calculator.test.js").write_text(
        "const test = require('node:test');\n"
        "const assert = require('node:assert/strict');\n"
        "const { add } = require('../calculator');\n\n"
        "test('add returns subtraction', () => {\n"
        "  assert.equal(add(2, 3), -1);\n"
        "});\n",
        encoding="utf-8",
    )


def _no_fix(root: Path) -> None:
    assert root.is_dir()


def _add_pytest_contract(root: Path) -> None:
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_calculator.py").write_text(
        "from calculator import add\n\n\ndef test_add() -> None:\n    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "add acceptance test")


def _tamper_pytest_contract(root: Path) -> None:
    (root / "tests" / "test_calculator.py").write_text(
        "from calculator import add\n\n\ndef test_add() -> None:\n    assert add(2, 3) == -1\n",
        encoding="utf-8",
    )


def test_detects_python_project_and_explicit_commands(tmp_path: Path) -> None:
    root = _python_project(tmp_path)

    commands = discover_solve_commands(root, reproduce_command=_check_command(), test_command="python -m compileall -q .")

    assert detect_project_type(root) == "python"
    assert [item.command_id for item in commands] == ["explicit-reproduction", "explicit-test"]


def test_detects_python_src_layout_without_project_metadata(tmp_path: Path) -> None:
    root = tmp_path / "src-layout"
    source = root / "src"
    source.mkdir(parents=True)
    (source / "service.py").write_text("value = 1\n", encoding="utf-8")

    assert detect_project_type(root) == "python"


def test_discovers_pytest_when_no_matrix_exists(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    (root / "tests").mkdir()

    commands = discover_solve_commands(root)

    assert any(item.command == "python -m pytest" for item in commands)


def test_detects_javascript_and_typescript_projects(tmp_path: Path) -> None:
    javascript_root = _javascript_project(tmp_path)

    assert detect_project_type(javascript_root) == "javascript"
    assert [item.command for item in discover_solve_commands(javascript_root)] == ["npm test"]

    typescript_root = tmp_path / "typescript-src"
    source = typescript_root / "src"
    source.mkdir(parents=True)
    (source / "service.ts").write_text("export const value: number = 1;\n", encoding="utf-8")

    assert detect_project_type(typescript_root) == "javascript"


def test_javascript_command_discovery_uses_declared_or_locked_package_manager(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    package["packageManager"] = "pnpm@11.7.0"
    (root / "package.json").write_text(json.dumps(package), encoding="utf-8")

    assert [item.command for item in discover_solve_commands(root)] == ["pnpm test"]

    package.pop("packageManager")
    (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (root / "yarn.lock").write_text("# fixture\n", encoding="utf-8")

    assert [item.command for item in discover_solve_commands(root)] == ["yarn test"]


def test_javascript_without_test_script_falls_back_to_node_test(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path, scripts=False)

    assert [item.command for item in discover_solve_commands(root)] == ["node --test"]


def test_workspace_package_discovery_and_target_resolution(tmp_path: Path) -> None:
    root, package_root = _javascript_workspace(tmp_path)

    assert discover_workspace_packages(root) == ["packages/calculator"]
    target, package_path, error = resolve_solve_target(root, "packages/calculator")
    assert (target, package_path, error) == (package_root, "packages/calculator", None)

    _, _, absolute_error = resolve_solve_target(root, package_root)
    _, _, escape_error = resolve_solve_target(root, "../outside")
    assert "relative" in str(absolute_error)
    assert "inside" in str(escape_error)


def test_workspace_root_requires_explicit_package_when_root_has_no_test(tmp_path: Path) -> None:
    root, _ = _javascript_workspace(tmp_path)

    result = solve_project(root, problem="calculator subtracts")

    assert result.status == "blocked"
    assert "workspace_package_required" in result.blockers
    assert "packages/calculator" in result.warnings[0]


def test_workspace_package_repair_runs_inside_selected_package(tmp_path: Path) -> None:
    root, package_root = _javascript_workspace(tmp_path)

    result = solve_project(
        root,
        package="packages/calculator",
        problem="calculator subtracts",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix_javascript]),
    )

    assert result.status == "verified"
    assert result.workspace_root == str(root)
    assert result.project_root == str(package_root)
    assert result.package_path == "packages/calculator"


def test_interrupted_session_can_resume_with_fresh_approval(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    output = tmp_path / "out"

    with pytest.raises(SimulatedInterruption):
        solve_project(
            root,
            problem="add returns subtraction",
            test_command=_check_command(),
            output_root=output,
            allow_repair=True,
            repair_executor=InterruptingRepairExecutor(),
        )

    session_dir = next(output.iterdir())
    stored = json.loads((session_dir / "solve-session.json").read_text(encoding="utf-8"))
    assert stored["status"] == "repairing"
    assert stored["rounds"] == []

    approval = resume_solve_session(session_dir)
    assert approval.status == "approval_required"

    resumed = resume_solve_session(
        session_dir,
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix]),
    )
    assert resumed.status == "verified"
    assert len(resumed.rounds) == 1


def test_resume_blocks_when_original_repair_branch_is_not_checked_out(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    output = tmp_path / "out"
    with pytest.raises(SimulatedInterruption):
        solve_project(
            root,
            problem="add returns subtraction",
            test_command=_check_command(),
            output_root=output,
            allow_repair=True,
            repair_executor=InterruptingRepairExecutor(),
        )
    session_dir = next(output.iterdir())
    _run_git(root, "switch", "main")

    resumed = resume_solve_session(session_dir, allow_repair=True, repair_executor=ScriptedRepairExecutor([_fix]))

    assert resumed.status == "blocked"
    assert "resume_branch_mismatch" in resumed.blockers


def test_resume_blocks_when_protected_input_changed_during_interruption(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)
    output = tmp_path / "out"
    with pytest.raises(SimulatedInterruption):
        solve_project(
            root,
            problem="addition subtracts",
            output_root=output,
            allow_repair=True,
            repair_executor=InterruptingRepairExecutor(),
        )
    session_dir = next(output.iterdir())
    _tamper_javascript_contract(root)

    resumed = resume_solve_session(
        session_dir,
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix_javascript]),
    )

    assert resumed.status == "blocked"
    assert "verification_inputs_modified" in resumed.blockers


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is required for the Node.js solve integration")
def test_javascript_repair_uses_npm_and_independently_verifies(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)

    result = solve_project(
        root,
        problem="add returns subtraction",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix_javascript]),
    )

    assert result.status == "verified"
    assert result.project_type == "javascript"
    assert result.commands[0]["command"] == "npm test"
    assert result.rounds[0]["verification"][0]["status"] == "passed"
    assert "package.json" in result.protected_verification_inputs
    assert "tests/calculator.test.js" in result.protected_verification_inputs


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is required for the Node.js solve integration")
def test_javascript_multi_round_repair_preserves_contract_and_then_verifies(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)
    (root / "calculator.js").write_text(
        "exports.add = (a, b) => a - b;\nexports.multiply = (a, b) => a + b;\n",
        encoding="utf-8",
    )
    (root / "tests" / "calculator.test.js").write_text(
        "const test = require('node:test');\n"
        "const assert = require('node:assert/strict');\n"
        "const { add, multiply } = require('../calculator');\n\n"
        "test('add returns a sum', () => assert.equal(add(2, 3), 5));\n"
        "test('multiply returns a product', () => assert.equal(multiply(3, 4), 12));\n",
        encoding="utf-8",
    )
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "add second broken behavior")

    def fix_add_only(project: Path) -> None:
        (project / "calculator.js").write_text(
            "exports.add = (a, b) => a + b;\nexports.multiply = (a, b) => a + b;\n",
            encoding="utf-8",
        )

    def fix_both_behaviors(project: Path) -> None:
        (project / "calculator.js").write_text(
            "exports.add = (a, b) => a + b;\nexports.multiply = (a, b) => a * b;\n",
            encoding="utf-8",
        )

    executor = ScriptedRepairExecutor([fix_add_only, fix_both_behaviors])
    result = solve_project(
        root,
        problem="addition subtracts and multiplication adds",
        output_root=tmp_path / "out",
        allow_repair=True,
        max_rounds=3,
        repair_executor=executor,
    )

    assert result.status == "verified"
    assert executor.calls == 2
    assert [item["verified"] for item in result.rounds] == [False, True]
    assert result.verification_input_changes == []
    assert "tests/calculator.test.js" in result.protected_verification_inputs


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is required for the Node.js solve integration")
def test_javascript_test_tampering_is_blocked_before_npm_verification(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)

    result = solve_project(
        root,
        problem="add returns subtraction",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_tamper_javascript_contract]),
    )

    assert result.status == "blocked"
    assert result.rounds[0]["verification"] == []
    assert result.verification_input_changes[0]["path"] == "tests/calculator.test.js"


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is required for the Node.js solve integration")
def test_javascript_package_script_tampering_is_blocked(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)

    def weaken_package_script(project: Path) -> None:
        _fix_javascript(project)
        package = json.loads((project / "package.json").read_text(encoding="utf-8"))
        package["scripts"]["test"] = "node -e \"process.exit(0)\""
        (project / "package.json").write_text(json.dumps(package), encoding="utf-8")

    result = solve_project(
        root,
        problem="add returns subtraction",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([weaken_package_script]),
    )

    assert result.status == "blocked"
    assert result.rounds[0]["verification"] == []
    assert result.verification_input_changes[0]["path"] == "package.json"


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is required for the Node.js solve integration")
def test_javascript_runner_config_and_lockfile_tampering_is_blocked(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)
    (root / "package-lock.json").write_text('{"lockfileVersion": 3}\n', encoding="utf-8")
    (root / "vitest.config.ts").write_text(
        "export default { test: { environment: 'node' } };\n",
        encoding="utf-8",
    )
    ignored_test = root / "node_modules" / "fixture.test.js"
    ignored_test.parent.mkdir()
    ignored_test.write_text("throw new Error('must not be scanned');\n", encoding="utf-8")
    _run_git(root, "add", "package-lock.json", "vitest.config.ts")
    _run_git(root, "commit", "-m", "add JavaScript verification configuration")

    def weaken_runner_contract(project: Path) -> None:
        _fix_javascript(project)
        (project / "package-lock.json").write_text('{"lockfileVersion": 2}\n', encoding="utf-8")
        (project / "vitest.config.ts").write_text(
            "export default { test: { passWithNoTests: true } };\n",
            encoding="utf-8",
        )

    result = solve_project(
        root,
        problem="add returns subtraction",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([weaken_runner_contract]),
    )

    changed = {item["path"] for item in result.verification_input_changes}
    assert result.status == "blocked"
    assert result.rounds[0]["verification"] == []
    assert {"package-lock.json", "vitest.config.ts"}.issubset(result.protected_verification_inputs)
    assert "node_modules/fixture.test.js" not in result.protected_verification_inputs
    assert changed == {"package-lock.json", "vitest.config.ts"}


def test_missing_verification_tool_blocks_before_repair(tmp_path: Path) -> None:
    root = _javascript_project(tmp_path)
    executor = ScriptedRepairExecutor([_fix_javascript])

    result = solve_project(
        root,
        problem="add returns subtraction",
        test_command="doctor-link-command-that-does-not-exist --test",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=executor,
    )

    assert result.status == "blocked"
    assert "verification_tool_missing" in result.blockers
    assert executor.calls == 0
    assert result.repair_branch is None


def test_baseline_timeout_blocks_before_repair(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    executor = ScriptedRepairExecutor([_fix])

    result = solve_project(
        root,
        problem="verification never finishes",
        test_command='python -c "import time; time.sleep(2)"',
        output_root=tmp_path / "out",
        allow_repair=True,
        command_timeout_seconds=1,
        repair_executor=executor,
    )

    assert result.status == "blocked"
    assert "baseline_check_timed_out" in result.blockers
    assert result.baseline[0]["timed_out"] is True
    assert executor.calls == 0
    assert result.repair_branch is None


def test_dry_run_reproduces_problem_and_requires_approval(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    output = tmp_path / "solve-output"

    result = solve_project(root, problem="addition subtracts", test_command=_check_command(), output_root=output)

    assert result.status == "approval_required"
    assert result.explicit_user_approval is False
    assert result.repair_branch is None
    assert result.baseline[0]["status"] == "failed"
    session = Path(result.output_dir or "")
    assert (session / "repair-prompt-preview.md").exists()
    assert json.loads((session / "solve-session.json").read_text(encoding="utf-8"))["status"] == "approval_required"
    assert _run_git(root, "branch", "--show-current") == "main"


def test_passing_baseline_is_not_reproduced_and_does_not_repair(tmp_path: Path) -> None:
    root = _python_project(tmp_path, broken=False)
    executor = ScriptedRepairExecutor([_fix])

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=executor,
    )

    assert result.status == "not_reproduced"
    assert executor.calls == 0
    assert result.repair_branch is None


def test_dirty_worktree_blocks_before_commands_or_repair(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    (root / "calculator.py").write_text("dirty = True\n", encoding="utf-8")

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix]),
    )

    assert result.status == "blocked"
    assert "dirty_worktree" in result.blockers
    assert result.baseline == []


def test_dirty_worktree_allows_preview_without_repair_authorization(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    (root / "notes.txt").write_text("local scratch\n", encoding="utf-8")

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=False,
    )

    assert result.status == "approval_required"
    assert "dirty_worktree" not in result.blockers
    assert result.baseline
    assert result.output_dir is not None


def test_verification_change_approval_requires_repair_approval(tmp_path: Path) -> None:
    root = _python_project(tmp_path)

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        allow_verification_changes=True,
    )

    assert result.status == "blocked"
    assert "verification_change_approval_requires_repair" in result.blockers


def test_unsafe_shell_operator_is_blocked_without_execution(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    marker = root / "must-not-exist"

    result = solve_project(
        root,
        problem="unsafe command",
        test_command=f"python -c \"raise SystemExit(1)\"; touch {marker}",
        output_root=tmp_path / "out",
    )

    assert result.status == "blocked"
    assert any("Unsupported shell operator" in item for item in result.blockers)
    assert not marker.exists()


def test_check_that_modifies_worktree_blocks_even_without_repair_approval(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    command = (
        'python -c "from pathlib import Path; '
        "Path('calculator.py').write_text('changed = True\\n'); raise SystemExit(1)\""
    )

    result = solve_project(
        root,
        problem="mutating check",
        test_command=command,
        output_root=tmp_path / "out",
    )

    assert result.status == "blocked"
    assert "checks_modified_worktree" in result.blockers
    assert result.repair_branch is None


def test_explicit_repair_creates_branch_and_independently_verifies(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    executor = ScriptedRepairExecutor([_fix])

    result = solve_project(
        root,
        problem="add returns subtraction",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=True,
        max_rounds=3,
        repair_executor=executor,
    )

    assert result.status == "verified"
    assert result.success is True
    assert executor.calls == 1
    assert result.repair_branch is not None
    assert _run_git(root, "branch", "--show-current") == result.repair_branch
    assert result.rounds[0]["verified"] is True
    session = Path(result.output_dir or "")
    assert (session / "round-1" / "codex-events.jsonl").exists()
    assert (session / "round-1" / "verification.json").exists()


def test_failed_first_round_retries_and_then_verifies(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    executor = ScriptedRepairExecutor([_no_fix, _fix])

    result = solve_project(
        root,
        problem="add returns subtraction",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=True,
        max_rounds=3,
        repair_executor=executor,
    )

    assert result.status == "verified"
    assert executor.calls == 2
    assert [item["verified"] for item in result.rounds] == [False, True]


def test_test_tampering_blocks_even_when_modified_tests_pass(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    _add_pytest_contract(root)

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command="python -m pytest -q",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_tamper_pytest_contract]),
    )

    assert result.status == "blocked"
    assert result.success is False
    assert "verification_inputs_modified" in result.blockers
    assert result.rounds[0]["verification"] == []
    assert result.rounds[0]["verified"] is False
    assert result.verification_input_changes[0]["path"] == "tests/test_calculator.py"
    assert result.verification_input_changes[0]["change_type"] == "modified"
    session = Path(result.output_dir or "")
    changes = json.loads((session / "round-1" / "verification-input-changes.json").read_text(encoding="utf-8"))
    assert changes[0]["path"] == "tests/test_calculator.py"


def test_explicit_test_change_authorization_requires_review_instead_of_verified(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    _add_pytest_contract(root)

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command="python -m pytest -q",
        output_root=tmp_path / "out",
        allow_repair=True,
        allow_verification_changes=True,
        repair_executor=ScriptedRepairExecutor([_tamper_pytest_contract]),
    )

    assert result.status == "review_required"
    assert result.success is False
    assert result.blockers == []
    assert result.rounds[0]["verification"][0]["status"] == "passed"
    assert result.verification_input_changes[0]["path"] == "tests/test_calculator.py"


def test_directly_referenced_verification_script_is_protected(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    verification_script = root / "verify_contract.py"
    verification_script.write_text(
        "from calculator import add\nassert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "add verification script")

    def tamper_script(project: Path) -> None:
        (project / "verify_contract.py").write_text("raise SystemExit(0)\n", encoding="utf-8")

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command="python verify_contract.py",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([tamper_script]),
    )

    assert result.status == "blocked"
    assert result.verification_input_changes[0]["path"] == "verify_contract.py"


def test_test_configuration_change_blocks_a_passing_production_fix(tmp_path: Path) -> None:
    root = _python_project(tmp_path)

    def change_config_and_fix(project: Path) -> None:
        _fix(project)
        (project / "pyproject.toml").write_text(
            "[project]\nname = 'solve-fixture'\nversion = '0.0.1'\n\n[tool.pytest.ini_options]\naddopts = '-q'\n",
            encoding="utf-8",
        )

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([change_config_and_fix]),
    )

    assert result.status == "blocked"
    assert result.rounds[0]["verification"] == []
    assert result.verification_input_changes[0]["path"] == "pyproject.toml"


def test_post_repair_check_cannot_mutate_protected_golden_file(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    tests = root / "tests"
    tests.mkdir()
    (tests / "golden.txt").write_text("original\n", encoding="utf-8")
    (root / "verify_contract.py").write_text(
        "from pathlib import Path\n"
        "from calculator import add\n"
        "value = add(2, 3)\n"
        "if value == 5:\n"
        "    Path('tests/golden.txt').write_text('changed\\n', encoding='utf-8')\n"
        "assert value == 5\n",
        encoding="utf-8",
    )
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "add mutating verification fixture")

    result = solve_project(
        root,
        problem="addition is wrong",
        test_command="python verify_contract.py",
        output_root=tmp_path / "out",
        allow_repair=True,
        repair_executor=ScriptedRepairExecutor([_fix]),
    )

    assert result.status == "blocked"
    assert result.rounds[0]["verification"][0]["status"] == "passed"
    assert result.verification_input_changes[0]["path"] == "tests/golden.txt"
    assert result.verification_input_changes[0]["detected_at"] == "after_verification"


def test_exhausted_rounds_returns_failed_with_evidence(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    executor = ScriptedRepairExecutor([_no_fix])

    result = solve_project(
        root,
        problem="add returns subtraction",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=True,
        max_rounds=2,
        repair_executor=executor,
    )

    assert result.status == "failed"
    assert executor.calls == 2
    assert len(result.rounds) == 2
    assert all(item["verified"] is False for item in result.rounds)


def test_repair_executor_exception_is_captured_and_bounded_to_three_rounds(tmp_path: Path) -> None:
    root = _python_project(tmp_path)

    result = solve_project(
        root,
        problem="add returns subtraction",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        allow_repair=True,
        max_rounds=99,
        repair_executor=FailingRepairExecutor(),
    )

    assert result.status == "failed"
    assert len(result.rounds) == 3
    assert all(item["repair"]["error"] == "RuntimeError: provider crashed" for item in result.rounds)


def test_codex_executor_uses_workspace_write_json_and_parses_events(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run_command(command, timeout_seconds, cwd):
        captured["command"] = command
        captured["cwd"] = cwd
        return CommandResult(
            command=list(command),
            returncode=0,
            stdout="\n".join(
                [
                    json.dumps({"type": "thread.started", "thread_id": "thread-123"}),
                    json.dumps({"type": "item.completed", "item": {"type": "file_change"}}),
                    json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "fixed"}}),
                ]
            ),
            stderr="",
            started_at="start",
            completed_at="end",
        )

    monkeypatch.setattr("doctor_link.core.solve.run_command", fake_run_command)
    executor = CodexRepairExecutor(binary="codex-test")

    result = executor.run("repair this", tmp_path, 60)

    command = captured["command"]
    assert isinstance(command, list)
    assert command[:4] == ["codex-test", "exec", "--sandbox", "workspace-write"]
    assert "--json" in command
    assert "--dangerously-bypass-approvals-and-sandbox" not in command
    assert result.thread_id == "thread-123"
    assert result.final_message == "fixed"
    assert result.file_change_events == 1


def test_solve_cli_json_uses_distinct_approval_exit_code(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "solve",
            str(root),
            "--problem",
            "addition subtracts",
            "--test-command",
            _check_command(),
            "--out",
            str(tmp_path / "out"),
            "--json",
        ],
    )

    assert result.exit_code == 2, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "approval_required"
    assert payload["success"] is False


def test_solve_cli_rejects_unknown_tool_with_string_validation(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            "solve",
            str(root),
            "--problem",
            "addition is wrong",
            "--test-command",
            _check_command(),
            "--tool",
            "not-a-tool",
            "--json",
        ],
    )
    assert result.exit_code != 0
    assert "Unsupported repair tool" in result.output


def test_compact_protected_paths_use_globs_for_test_trees() -> None:
    from doctor_link.core.solve import _compact_protected_paths

    paths = [f"tests/test_{index}.py" for index in range(8)] + ["pyproject.toml", "package.json"]
    compact = _compact_protected_paths(paths)
    assert "tests/**" in compact
    assert "pyproject.toml" in compact
    assert len(compact) < len(paths)


def test_suggest_only_produces_change_receipt_without_verified(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        output_root=tmp_path / "out",
        suggest_only=True,
        repair_executor=ScriptedRepairExecutor([_fix]),
    )
    assert result.status == "suggestion_ready"
    assert result.success is False
    assert result.repair_branch is not None
    assert result.change_receipt
    assert result.change_receipt.get("schema") == "doctor-link-change-receipt-v1"
    session = Path(result.output_dir or "")
    assert (session / "change-receipt.json").is_file()
    assert (session / "change-receipt.md").is_file()
    assert any("calculator.py" in path for path in result.change_receipt.get("production_files", []) + [item.get("path") for item in result.change_receipt.get("files", [])])


def test_suggest_only_conflicts_with_allow_repair(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    result = solve_project(
        root,
        problem="addition is wrong",
        test_command=_check_command(),
        allow_repair=True,
        suggest_only=True,
        repair_executor=ScriptedRepairExecutor([_fix]),
    )
    assert result.status == "blocked"
    assert "conflicting_repair_modes" in result.blockers
