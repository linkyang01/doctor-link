from __future__ import annotations

import json
import subprocess
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.reproduction_suggester import suggest_reproductions
from doctor_link.entrypoint import main


def _python_fixture(tmp_path: Path, *, broken: bool = True) -> Path:
    root = tmp_path / "checkout-service"
    tests = root / "tests"
    tests.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='checkout-service'\nversion='0.0.1'\n", encoding="utf-8")
    (root / "checkout.py").write_text(
        "def charge(total: int) -> int:\n    return total * 2\n" if broken else "def charge(total: int) -> int:\n    return total\n",
        encoding="utf-8",
    )
    (tests / "test_checkout.py").write_text(
        "from checkout import charge\n\ndef test_checkout_charges_once():\n    assert charge(10) == 10\n",
        encoding="utf-8",
    )
    (tests / "test_profile.py").write_text("def test_profile():\n    assert True\n", encoding="utf-8")
    return root


def test_problem_terms_rank_and_validate_focused_python_test(tmp_path: Path) -> None:
    root = _python_fixture(tmp_path)

    result = suggest_reproductions(root, "Checkout duplicates a payment charge", validate=True)

    assert result.status == "reproduced"
    assert result.selected_command == "PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_checkout.py -q"
    assert result.suggestions[0]["scope"] == "tests/test_checkout.py"
    assert "checkout" in result.suggestions[0]["matched_terms"]


def test_passing_candidates_report_not_reproduced(tmp_path: Path) -> None:
    root = _python_fixture(tmp_path, broken=False)

    result = suggest_reproductions(root, "Checkout duplicates a payment charge", validate=True)

    assert result.status == "not_reproduced"
    assert result.selected_command is None


def test_suggestion_cli_returns_selected_command_as_json(tmp_path: Path) -> None:
    root = _python_fixture(tmp_path)

    result = CliRunner().invoke(
        main,
        ["reproduce", "suggest", str(root), "--problem", "Checkout duplicates charge", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "reproduced"
    assert payload["selected_command"].endswith("test_checkout.py -q")


def test_unsupported_project_is_blocked(tmp_path: Path) -> None:
    result = suggest_reproductions(tmp_path, "something is wrong", validate=True)

    assert result.status == "blocked"
    assert "supported" in result.warnings[0]


def test_src_layout_without_metadata_is_supported(tmp_path: Path) -> None:
    source = tmp_path / "src"
    tests = tmp_path / "tests"
    source.mkdir()
    tests.mkdir()
    (source / "checkout.py").write_text("value = 1\n", encoding="utf-8")
    (tests / "test_checkout.py").write_text("def test_checkout():\n    assert False\n", encoding="utf-8")

    result = suggest_reproductions(tmp_path, "Checkout fails", validate=False)

    assert result.project_type == "python"
    assert result.status == "proposed"


def test_unrelated_problem_uses_declared_suite_instead_of_claiming_file_match(tmp_path: Path) -> None:
    root = _python_fixture(tmp_path)

    result = suggest_reproductions(root, "The exported report has the wrong color", validate=False)

    assert len(result.suggestions) == 1
    assert result.suggestions[0]["suggestion_id"] == "project-test-suite"


def test_candidate_that_changes_git_worktree_is_not_trusted(tmp_path: Path) -> None:
    root = _python_fixture(tmp_path)
    (root / "tests" / "test_checkout.py").write_text(
        "from pathlib import Path\n"
        "from checkout import charge\n\n"
        "def test_checkout_mutates():\n"
        "    Path('generated.txt').write_text('changed')\n"
        "    assert charge(10) == 10\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Suggestion Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "suggestion@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)

    result = suggest_reproductions(root, "Checkout duplicates charge", validate=True)

    assert result.status == "blocked"
    assert result.suggestions[0]["status"] == "modified_worktree"
    assert result.selected_command is None


def test_configured_reproduction_is_used_without_test_files(tmp_path: Path) -> None:
    source = tmp_path / "src"
    config = tmp_path / ".doctorlink"
    source.mkdir()
    config.mkdir()
    (source / "checkout.py").write_text("def charge(value): return value * 2\n", encoding="utf-8")
    (config / "reproduce.yml").write_text(
        "reproductions:\n"
        "  - id: checkout\n"
        "    title: Checkout charges once\n"
        "    kind: command\n"
        "    command: PYTHONPATH=src python -c \"from checkout import charge; assert charge(10) == 10\"\n",
        encoding="utf-8",
    )

    result = suggest_reproductions(tmp_path, "Checkout duplicates charge", validate=True)

    assert result.status == "reproduced"
    assert result.selected_command is not None
    assert result.selected_command.startswith("PYTHONDONTWRITEBYTECODE=1 ")
    assert result.suggestions[0]["suggestion_id"] == "catalog-checkout"
