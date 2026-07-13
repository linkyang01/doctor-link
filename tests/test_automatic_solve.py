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
