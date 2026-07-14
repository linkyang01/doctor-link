from __future__ import annotations

import json
import subprocess
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.guided_assistant import render_guided_result, run_guided_session
from doctor_link.entrypoint import main


def _fixture(tmp_path: Path, *, broken: bool = True) -> Path:
    root = tmp_path / "project"
    tests = root / "tests"
    tests.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='guided'\nversion='0.0.1'\n", encoding="utf-8")
    value = "total * 2" if broken else "total"
    (root / "checkout.py").write_text(f"def charge(total: int) -> int:\n    return {value}\n", encoding="utf-8")
    (tests / "test_checkout.py").write_text(
        "from checkout import charge\n\ndef test_charge_once():\n    assert charge(10) == 10\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Guided Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "guided@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
    return root


def test_guided_session_reproduces_and_prepares_solve_preview(tmp_path: Path) -> None:
    root = _fixture(tmp_path)

    result = run_guided_session(root, problem="Checkout duplicates charge", output_root=tmp_path / "out")

    assert result.status == "approval_required"
    assert result.reproduction["status"] == "reproduced"
    assert result.solve is not None
    assert result.solve["explicit_user_approval"] is False
    assert Path(result.result_page).is_file()
    assert Path(result.output_dir, "guided-session.json").is_file()


def test_guided_session_does_not_repair_when_problem_is_not_reproduced(tmp_path: Path) -> None:
    root = _fixture(tmp_path, broken=False)

    result = run_guided_session(root, problem="Checkout duplicates charge", output_root=tmp_path / "out")

    assert result.status == "not_reproduced"
    assert result.solve is None


def test_assist_cli_requires_no_test_command_knowledge(tmp_path: Path) -> None:
    root = _fixture(tmp_path)

    result = CliRunner().invoke(
        main,
        ["assist", str(root), "--problem", "Checkout duplicates charge", "--out", str(tmp_path / "out"), "--no-open", "--json"],
    )

    assert result.exit_code == 2, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "approval_required"
    assert payload["reproduction"]["selected_command"].endswith("test_checkout.py -q")


def test_guided_result_escapes_user_problem(tmp_path: Path) -> None:
    root = _fixture(tmp_path, broken=False)
    result = run_guided_session(root, problem="<script>alert(1)</script>", output_root=tmp_path / "out")

    rendered = render_guided_result(result)

    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_assist_works_on_dirty_worktree_without_repair(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "local-notes.txt").write_text("dirty\n", encoding="utf-8")

    result = run_guided_session(root, problem="Checkout duplicates charge", output_root=tmp_path / "out")

    assert result.status == "approval_required"
    assert result.reproduction["status"] == "reproduced"
    assert result.solve is not None
    assert result.solve["status"] == "approval_required"
    assert "dirty_worktree" not in (result.solve.get("blockers") or [])


def test_guided_result_includes_exit_code_and_evidence_snippet(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    result = run_guided_session(root, problem="Checkout duplicates charge", output_root=tmp_path / "out")

    rendered = render_guided_result(result)

    assert "Evidence snippet" in rendered
    assert "Selected reproduction" in rendered
    assert "Exit" in rendered
