from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable

from click.testing import CliRunner

from doctor_link.core.command_runner import CommandResult
from doctor_link.core.solve import (
    CodexRepairExecutor,
    RepairExecution,
    detect_project_type,
    discover_solve_commands,
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


def _check_command() -> str:
    return 'python -c "from calculator import add; assert add(2, 3) == 5"'


def _fix(root: Path) -> None:
    (root / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
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
