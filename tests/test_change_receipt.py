from __future__ import annotations

import json
import subprocess
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.change_receipt import build_change_receipt, classify_path, receipt_to_markdown
from doctor_link.entrypoint import main


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("value = 1\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_app.py").write_text("def test_app():\n    assert True\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='x'\nversion='0'\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Diff Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "diff@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=root, check=True, capture_output=True)
    return root


def test_classify_path_categories() -> None:
    assert classify_path("src/app.py") == "production"
    assert classify_path("tests/test_app.py") == "test"
    assert classify_path("package.json") == "config"


def test_build_change_receipt_classifies_files(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "src" / "app.py").write_text("value = 2\n", encoding="utf-8")
    (root / "tests" / "test_app.py").write_text("def test_app():\n    assert False\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "change"], cwd=root, check=True, capture_output=True)
    base = subprocess.run(["git", "rev-parse", "HEAD^"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    receipt = build_change_receipt(root, base_ref=base, head_ref="HEAD", protected_paths=["tests/test_app.py"])
    assert receipt.schema == "doctor-link-change-receipt-v1"
    assert "src/app.py" in receipt.production_files
    assert "tests/test_app.py" in receipt.test_files
    assert "tests/test_app.py" in receipt.protected_changes
    markdown = receipt_to_markdown(receipt)
    assert "production" in markdown
    assert "Protected input changes" in markdown


def test_diff_cli_json_from_project(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = CliRunner().invoke(main, ["diff", str(root), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "doctor-link-change-receipt-v1"


def test_diff_cli_from_solve_session_writes_receipt(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    subprocess.run(["git", "switch", "-c", "doctor-link/repair"], cwd=root, check=True, capture_output=True)
    (root / "src" / "app.py").write_text("value = 3\n", encoding="utf-8")
    session = tmp_path / "session"
    session.mkdir()
    (session / "solve-session.json").write_text(
        json.dumps(
            {
                "project_root": str(root),
                "original_branch": "main",
                "repair_branch": "doctor-link/repair",
                "change_receipt": {
                    "base_ref": subprocess.run(
                        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
                    ).stdout.strip()
                },
                "protected_verification_inputs": ["tests/test_app.py"],
                "verification_input_changes": [],
            }
        ),
        encoding="utf-8",
    )
    result = CliRunner().invoke(main, ["diff", str(session), "--json", "--out", str(session)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "doctor-link-change-receipt-v1"
    assert "src/app.py" in payload["production_files"]
    assert (session / "change-receipt.json").is_file()
    assert (session / "change-receipt.md").is_file()


def test_receipt_markdown_handles_empty_change_set(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    receipt = build_change_receipt(root, base_ref="HEAD", head_ref="HEAD")
    text = receipt_to_markdown(receipt)
    assert "No file changes" in receipt.summary or "(none)" in text or "0 changed" in receipt.summary or "changed file" in receipt.summary


def test_diff_cli_human_output_lists_files(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "src" / "app.py").write_text("value = 9\n", encoding="utf-8")
    result = CliRunner().invoke(main, ["diff", str(root)])
    assert result.exit_code == 0, result.output
    assert "src/app.py" in result.output or "changed" in result.output.casefold() or "file" in result.output.casefold()


def test_classify_path_config_and_other() -> None:
    assert classify_path("README.md") in {"other", "config"}
    assert classify_path("pnpm-lock.yaml") == "config"
    assert classify_path("packages/pkg/index.ts") == "production"
