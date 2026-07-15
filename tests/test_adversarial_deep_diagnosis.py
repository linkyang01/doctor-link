from __future__ import annotations

import subprocess
from pathlib import Path

from doctor_link.core.root_cause import analyze_root_cause
from doctor_link.core.solve import RepairExecution, solve_project


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _init(root: Path) -> None:
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Adversarial Test")
    _git(root, "config", "user.email", "adversarial@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")


def test_multifile_chain_keeps_test_service_and_repository_order(tmp_path: Path) -> None:
    root = tmp_path / "service"
    for relative in ("tests/test_checkout.py", "src/checkout.py", "src/repository.py"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n", encoding="utf-8")
    output = (
        "tests/test_checkout.py:14: in test_charge_once\n"
        'File "src/checkout.py", line 41, in charge\n'
        'File "src/repository.py", line 27, in save\n'
        "E   assert 2 == 1\n"
    )

    analysis = analyze_root_cause(root, problem="duplicate charge", outputs=[(output, "")])

    chain = analysis.call_chains[0]
    assert chain["complete"] is True
    assert [(item["role"], item["path"], item["function"]) for item in chain["nodes"]] == [
        ("test", "tests/test_checkout.py", "test_charge_once"),
        ("production", "src/checkout.py", "charge"),
        ("production", "src/repository.py", "save"),
    ]


def test_unrelated_recent_change_is_flagged_as_conflicting_evidence(tmp_path: Path) -> None:
    root = tmp_path / "service"
    (root / "src").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='adversarial'\nversion='0.0.1'\n", encoding="utf-8")
    (root / "src" / "actual.py").write_text("def charge():\n    raise RuntimeError('boom')\n", encoding="utf-8")
    (root / "src" / "unrelated.py").write_text("FLAG = False\n", encoding="utf-8")
    _init(root)
    (root / "src" / "unrelated.py").write_text("FLAG = True\n", encoding="utf-8")
    output = 'File "src/actual.py", line 2, in charge\nRuntimeError: boom\n'

    analysis = analyze_root_cause(root, problem="charge crashes", outputs=[(output, "")])

    assert analysis.hints[0]["candidate_paths"] == ["src/unrelated.py"]
    unrelated = next(item for item in analysis.hints if item["candidate_paths"] == ["src/unrelated.py"])
    assert "failure stack references" not in unrelated["evidence"]
    assert any("conflicting evidence" in warning for warning in analysis.warnings)
    assert any(item["candidate_paths"] == ["src/actual.py"] for item in analysis.hints)


class _FixOnlyFocused:
    name = "scripted"

    def run(self, prompt: str, project_root: Path, timeout_seconds: int) -> RepairExecution:
        (project_root / "calculator.py").write_text(
            "def add(a, b): return a + b\ndef multiply(a, b): return a + b\n",
            encoding="utf-8",
        )
        return RepairExecution(status="completed", return_code=0)


def test_focused_pass_cannot_hide_full_regression_failure(tmp_path: Path) -> None:
    root = tmp_path / "calculator"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='calculator'\nversion='0.0.1'\n", encoding="utf-8")
    (root / "calculator.py").write_text(
        "def add(a, b): return a - b\ndef multiply(a, b): return a + b\n",
        encoding="utf-8",
    )
    _init(root)

    result = solve_project(
        root,
        problem="addition and multiplication are wrong",
        reproduce_command='python -c "from calculator import add; assert add(2, 3) == 5"',
        test_command='python -c "from calculator import add, multiply; assert add(2, 3) == 5; assert multiply(3, 4) == 12"',
        allow_repair=True,
        max_rounds=1,
        output_root=tmp_path / "out",
        repair_executor=_FixOnlyFocused(),
    )

    assert result.status == "failed"
    layers = result.rounds[0]["verification_layers"]
    assert layers[0]["passed"] is True
    assert layers[1]["passed"] is False
    assert layers[1]["skipped"] is False


def test_dependency_error_remains_ungrounded_and_blocks_repair(tmp_path: Path) -> None:
    root = tmp_path / "dependency"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='dependency'\nversion='0.0.1'\n", encoding="utf-8")
    _init(root)

    result = solve_project(
        root,
        problem="dependency cannot import",
        test_command='python -c "import definitely_missing_doctor_link_package"',
        allow_repair=True,
        require_grounded_root_cause=True,
        output_root=tmp_path / "out",
        repair_executor=_FixOnlyFocused(),
    )

    assert result.status == "blocked"
    assert "grounded_root_cause_required" in result.blockers
    assert result.repair_branch is None
