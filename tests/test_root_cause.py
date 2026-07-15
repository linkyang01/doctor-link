from __future__ import annotations

import json
import subprocess
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.root_cause import analyze_root_cause
from doctor_link.core.hypothesis_verifier import verify_top_hypothesis
from doctor_link.core.repair_guidance import build_repair_guidance
from doctor_link.core.solve import SolveCommandResult, build_repair_prompt, solve_project
from doctor_link.entrypoint import main


def _python_project(tmp_path: Path) -> Path:
    root = tmp_path / "service"
    tests = root / "tests"
    src = root / "src"
    tests.mkdir(parents=True)
    src.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='service'\nversion='0.0.1'\n", encoding="utf-8")
    (src / "billing.py").write_text(
        "class ChargeEngine:\n"
        "    def charge_once(self, total: int) -> int:\n"
        "        return total * 2\n",
        encoding="utf-8",
    )
    (tests / "test_billing.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))\n"
        "from billing import ChargeEngine\n\n"
        "def test_charge_once_a():\n"
        "    assert ChargeEngine().charge_once(10) == 10\n\n"
        "def test_charge_once_b():\n"
        "    assert ChargeEngine().charge_once(5) == 5\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Explain Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "explain@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
    return root


def test_analyze_root_cause_clusters_shared_symbol_and_maps_source(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    failure_a = (
        '______________ test_charge_once_a ______________\n'
        'tests/test_billing.py:8: in test_charge_once_a\n'
        '    assert ChargeEngine().charge_once(10) == 10\n'
        'E   assert 20 == 10\n'
        'File "src/billing.py", line 3, in charge_once\n'
        '    return total * 2\n'
    )
    failure_b = (
        '______________ test_charge_once_b ______________\n'
        'tests/test_billing.py:12: in test_charge_once_b\n'
        '    assert ChargeEngine().charge_once(5) == 5\n'
        'E   assert 10 == 5\n'
        'File "src/billing.py", line 3, in charge_once\n'
        '    return total * 2\n'
    )

    analysis = analyze_root_cause(
        root,
        problem="Checkout charges twice",
        checks=[
            {"status": "failed", "return_code": 1, "stdout": failure_a, "stderr": ""},
            {"status": "failed", "return_code": 1, "stdout": failure_b, "stderr": ""},
        ],
    )

    assert analysis.status in {"explained", "partial"}
    assert analysis.failure_count == 2
    symbols = {hint["symbol"] for hint in analysis.hints}
    assert "ChargeEngine" in symbols or "charge_once" in symbols or "billing" in symbols
    paths = {path for hint in analysis.hints for path in hint["candidate_paths"]}
    assert any(path.endswith("billing.py") for path in paths)
    assert analysis.failures[0]["expected"] == "10"
    assert analysis.failures[0]["actual"] == "20"
    billing_hint = next(hint for hint in analysis.hints if "src/billing.py" in hint["candidate_paths"])
    assert billing_hint["locations"][0]["line"] == 3
    assert billing_hint["locations"][0]["function"] == "charge_once"
    assert billing_hint["locations"][0]["source"] == "return total * 2"
    assert billing_hint["score"] > 0
    assert billing_hint["evidence"]
    chain = analysis.call_chains[0]
    assert chain["complete"] is True
    assert [node["role"] for node in chain["nodes"]] == ["test", "production"]
    assert chain["nodes"][0]["function"] == "test_charge_once_a"
    assert chain["nodes"][1]["function"] == "charge_once"
    assert "advisory" in " ".join(analysis.warnings).casefold() or analysis.advisory is True


def test_solve_prompt_includes_advisory_root_cause_section(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    result = solve_project(
        root,
        problem="Checkout charges twice",
        test_command="PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q",
        output_root=tmp_path / "out",
        allow_repair=False,
    )
    assert result.status == "approval_required"
    assert result.root_cause
    assert result.root_cause.get("status") in {"explained", "partial", "insufficient_evidence"}
    prompt = build_repair_prompt(
        result,
        [
            SolveCommandResult(
                command_id=item["command_id"],
                kind=item["kind"],
                command=item["command"],
                status=item["status"],
                return_code=item["return_code"],
                stdout=item.get("stdout", ""),
                stderr=item.get("stderr", ""),
            )
            for item in result.baseline
        ],
        round_number=1,
    )
    if result.root_cause.get("hints"):
        assert "Suspected root cause" in prompt
        assert "advisory" in prompt.casefold()
    if result.root_cause.get("failures"):
        assert "Structured failure facts" in prompt
    if any(chain.get("nodes") for chain in result.root_cause.get("call_chains") or []):
        assert "Project-owned call paths" in prompt
    assert "grounded root cause" in prompt


def test_explain_cli_json_returns_hints(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            "explain",
            str(root),
            "--problem",
            "Checkout charges twice",
            "--test-command",
            "PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q",
            "--out",
            str(tmp_path / "explain-out"),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] in {"explained", "partial", "insufficient_evidence"}
    assert Path(payload["output_dir"], "explain-session.json").is_file()
    assert Path(payload["output_dir"], "root-cause.md").is_file()


def test_explain_cli_human_output_and_no_failure_exit(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    (root / "src" / "billing.py").write_text(
        "class ChargeEngine:\n"
        "    def charge_once(self, total: int) -> int:\n"
        "        return total\n",
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        main,
        [
            "explain",
            str(root),
            "--problem",
            "Checkout charges twice",
            "--test-command",
            "PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q",
        ],
    )
    assert result.exit_code == 3, result.output
    assert "Explain status: no_failures" in result.output


def test_explain_cli_reports_check_worktree_mutation(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    # The file is already untracked before the check; content hashing must still
    # detect that the command changed it even though porcelain status stays `??`.
    (root / "generated.txt").write_text("before", encoding="utf-8")
    command = (
        "python -c \"from pathlib import Path; "
        "Path('generated.txt').write_text('changed'); raise SystemExit(1)\""
    )

    result = CliRunner().invoke(
        main,
        ["explain", str(root), "--problem", "check mutates project", "--test-command", command, "--json"],
    )

    assert result.exit_code == 5, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "modified_worktree"
    assert payload["worktree_changed"] is True
    assert (root / "generated.txt").read_text(encoding="utf-8") == "changed"


def test_explain_cli_can_confirm_reversible_hypothesis(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    source = root / "src" / "billing.py"
    source.write_text(source.read_text(encoding="utf-8").replace("total * 2", "total"), encoding="utf-8")
    subprocess.run(["git", "add", "src/billing.py"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "correct implementation"], cwd=root, check=True, capture_output=True)
    source.write_text(source.read_text(encoding="utf-8").replace("return total", "return total * 2"), encoding="utf-8")
    before = source.read_bytes()

    result = CliRunner().invoke(
        main,
        [
            "explain", str(root), "--problem", "checkout charges twice",
            "--test-command", "python -m pytest -p no:cacheprovider -q",
            "--verify-hypothesis", "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    verification = payload["hypothesis_verification"]
    assert verification["status"] == "confirmed"
    assert verification["restored"] is True
    assert verification["worktree_unchanged"] is True
    assert payload["repair_guidance"]["status"] == "actionable"
    assert payload["repair_guidance"]["verification"]["focused_commands"]
    assert payload["analysis"]["call_chains"]
    assert source.read_bytes() == before


def test_explain_cli_rejects_missing_commands_and_unsupported_projects(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "notes.txt").write_text("no project markers\n", encoding="utf-8")
    unsupported = CliRunner().invoke(main, ["explain", str(empty), "--problem", "broken"])
    assert unsupported.exit_code != 0

    root = _python_project(tmp_path / "svc")
    # Remove default discovery by wiping tests and not providing a command.
    for path in (root / "tests").rglob("*.py"):
        path.unlink()
    missing = CliRunner().invoke(
        main,
        ["explain", str(root), "--problem", "broken", "--test-command", "python -c 'print(1)' | true"],
    )
    assert missing.exit_code != 0


def test_prompt_section_and_javascript_frame_mapping(tmp_path: Path) -> None:
    root = tmp_path / "js-app"
    src = root / "src"
    src.mkdir(parents=True)
    (root / "package.json").write_text('{"name":"js-app","version":"1.0.0"}\n', encoding="utf-8")
    (src / "math.js").write_text("function add(a, b) { return a - b; }\nmodule.exports = { add };\n", encoding="utf-8")
    analysis = analyze_root_cause(
        root,
        problem="addition subtracts",
        outputs=[
            (
                "Error: expected 3 got 1\n    at Object.add (src/math.js:1:28)\n",
                "",
            ),
            (
                "Error: expected 5 got 1\n    at Object.add (src/math.js:1:28)\nassert add(2, 3) == 5\n",
                "",
            ),
        ],
    )
    assert analysis.failure_count == 2
    assert analysis.failures[0]["expected"] == "3"
    assert analysis.failures[0]["actual"] == "1"
    math_frame = next(frame for frame in analysis.frames if frame["path"] == "src/math.js")
    assert math_frame["line"] == 1
    assert math_frame["function"] == "Object.add"
    assert math_frame["project_code"] is True
    section = analysis.prompt_section()
    if analysis.hints:
        assert "Suspected root cause" in section
        assert "advisory" in section.casefold()
    # Empty analysis path
    empty = analyze_root_cause(root, problem="nothing", checks=[{"status": "passed", "return_code": 0, "stdout": "", "stderr": ""}])
    assert empty.status == "no_failures"
    assert empty.prompt_section() == ""


def test_root_cause_prioritizes_changed_production_file(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    source = root / "src" / "billing.py"
    source.write_text(source.read_text(encoding="utf-8").replace("total * 2", "total * 3"), encoding="utf-8")

    analysis = analyze_root_cause(
        root,
        problem="checkout charge is wrong",
        outputs=[("Difference between expected and actual values", "")],
    )

    assert analysis.hints
    assert analysis.hints[0]["candidate_paths"] == ["src/billing.py"]
    assert "may still be unrelated" in analysis.hints[0]["rationale"]
    assert analysis.hints[0]["locations"][0]["line"] == 3
    assert analysis.hints[0]["locations"][0]["function"] == "charge_once"


def test_extracts_jest_expected_and_received_values(tmp_path: Path) -> None:
    root = tmp_path / "jest-app"
    (root / "src").mkdir(parents=True)
    (root / "src" / "price.js").write_text("export function price() { return 12; }\n", encoding="utf-8")
    output = """Error: expect(received).toBe(expected)\n\nExpected: 10\nReceived: 12\n\n    at price (src/price.js:1:34)\n"""

    analysis = analyze_root_cause(root, problem="wrong price", outputs=[(output, "")])

    assert analysis.failures[0]["expected"] == "10"
    assert analysis.failures[0]["actual"] == "12"
    frame = next(frame for frame in analysis.frames if frame["path"] == "src/price.js")
    assert frame["function"] == "price"
    assert frame["line"] == 1


def test_hypothesis_verification_confirms_and_restores_changed_file(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    source = root / "src" / "billing.py"
    source.write_text(source.read_text(encoding="utf-8").replace("total * 2", "total"), encoding="utf-8")
    subprocess.run(["git", "add", "src/billing.py"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "correct implementation"], cwd=root, check=True, capture_output=True)
    correct = source.read_bytes()
    source.write_text(source.read_text(encoding="utf-8").replace("return total", "return total * 2"), encoding="utf-8")
    faulty = source.read_bytes()
    command = "PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q"

    analysis = analyze_root_cause(
        root,
        problem="checkout charges twice",
        outputs=[('File "src/billing.py", line 3, in charge_once\nE   assert 20 == 10\n', "")],
    )
    result = verify_top_hypothesis(
        root,
        hints=analysis.hints,
        commands=[{"command_id": "test", "command": command}],
        baseline=[{"command_id": "test", "return_code": 1, "timed_out": False}],
        timeout_seconds=30,
    )

    assert result.status == "confirmed"
    assert result.experiment_passed == 1
    assert result.restored is True
    assert result.worktree_unchanged is True
    assert source.read_bytes() == faulty
    assert source.read_bytes() != correct


def test_hypothesis_verification_rejects_candidate_that_does_not_fix_failure(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    source = root / "src" / "billing.py"
    source.write_text(source.read_text(encoding="utf-8").replace("total * 2", "total * 3"), encoding="utf-8")
    analysis = analyze_root_cause(root, problem="wrong charge", outputs=[("E   assert 30 == 10", "")])

    result = verify_top_hypothesis(
        root,
        hints=analysis.hints,
        commands=[{"command_id": "test", "command": "python -m pytest -p no:cacheprovider -q"}],
        baseline=[{"command_id": "test", "return_code": 1, "timed_out": False}],
        timeout_seconds=30,
    )

    assert result.status == "rejected"
    assert result.restored is True
    assert source.read_text(encoding="utf-8").endswith("return total * 3\n")


def test_hypothesis_verification_reports_command_worktree_pollution(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    source = root / "src" / "billing.py"
    source.write_text(source.read_text(encoding="utf-8").replace("total * 2", "total * 3"), encoding="utf-8")
    analysis = analyze_root_cause(root, problem="wrong charge", outputs=[("E   assert 30 == 10", "")])
    command = "python -c \"from pathlib import Path; Path('experiment-output.txt').write_text('changed')\""

    result = verify_top_hypothesis(
        root,
        hints=analysis.hints,
        commands=[{"command_id": "test", "command": command}],
        baseline=[{"command_id": "test", "return_code": 1, "timed_out": False}],
        timeout_seconds=30,
    )

    assert result.status == "unsafe_to_test"
    assert result.restored is True
    assert result.worktree_unchanged is False
    assert (root / "experiment-output.txt").is_file()


def test_repair_guidance_separates_facts_inferences_and_verified_evidence(tmp_path: Path) -> None:
    root = _python_project(tmp_path)
    source = root / "src" / "billing.py"
    source.write_text(source.read_text(encoding="utf-8").replace("total * 2", "total * 3"), encoding="utf-8")
    analysis = analyze_root_cause(
        root,
        problem="wrong charge",
        outputs=[('tests/test_billing.py:8: in test_charge_once_a\nFile "src/billing.py", line 3, in charge_once\nE   assert 30 == 10', "")],
    )
    command = {"command_id": "test", "command": "python -m pytest tests/test_billing.py -q"}

    guidance = build_repair_guidance(
        root,
        analysis=analysis.to_dict(),
        hypothesis_verification={"status": "confirmed"},
        commands=[command],
        baseline=[{"command_id": "test", "return_code": 1}],
    )

    assert guidance["status"] == "actionable"
    assert guidance["candidate"] == {
        "path": "src/billing.py",
        "line": 3,
        "function": "charge_once",
        "source": "return total * 3",
    }
    assert guidance["diagnosis"]["observed_facts"]
    assert guidance["diagnosis"]["inferences"]
    assert guidance["diagnosis"]["verified_evidence"]
    assert guidance["verification"]["focused_commands"] == [command["command"]]
    assert "total * 3" in guidance["recommended_change"]["current_diff_excerpt"]
