from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from click.testing import CliRunner

from doctor_link.core.ai_handoff import check_handoff_compatibility
from doctor_link.core.diagnosis_workflow import create_after_package, create_before_package
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.package_transaction import LOCK_NAME, package_transaction
from doctor_link.core.report_comparator import write_report_comparison_to_package
from doctor_link.core.safe_command_runner import run_safe_command_sequence
from doctor_link.core.test_recorder import record_test_result
from doctor_link.core.user_assertion_manager import add_user_assertion
from doctor_link.core.verification_runner import run_verification
from doctor_link.p4_cli import main


def _package(tmp_path: Path, project: str = "Complex") -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project=project, category="simulation", summary="complex regression"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_safe_runner_supports_leading_environment_assignments(tmp_path: Path) -> None:
    result = run_safe_command_sequence(
        "MODE=simulation python -c \"import os; print(os.environ['MODE'])\" && python -c \"print('second')\"",
        cwd=tmp_path,
        timeout_seconds=10,
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["simulation", "second"]


def test_failed_reproduction_and_required_test_return_nonzero(tmp_path: Path) -> None:
    config = tmp_path / ".doctorlink"
    config.mkdir()
    (config / "reproduce.yml").write_text(
        'reproductions:\n  - id: fails\n    title: fails\n    kind: command\n    command: python -c "raise SystemExit(4)"\n',
        encoding="utf-8",
    )
    (config / "test-matrix.yml").write_text(
        'jobs:\n  - id: fails\n    title: fails\n    required: true\n    command: python -c "raise SystemExit(5)"\n',
        encoding="utf-8",
    )
    runner = CliRunner()

    reproduction = runner.invoke(main, ["reproduce", "run", "fails", str(tmp_path), "--json"])
    matrix = runner.invoke(main, ["test", "run", str(tmp_path), "--json"])

    assert reproduction.exit_code == 1
    assert json.loads(reproduction.output)["status"] == "failed"
    assert matrix.exit_code == 1
    assert json.loads(matrix.output)[0]["status"] == "failed"


def test_failed_optional_test_job_does_not_fail_the_command(tmp_path: Path) -> None:
    config = tmp_path / ".doctorlink"
    config.mkdir()
    (config / "test-matrix.yml").write_text(
        'jobs:\n  - id: optional\n    title: optional\n    required: false\n    command: python -c "raise SystemExit(7)"\n',
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, ["test", "run", str(tmp_path), "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == [
        {
            "job_id": "optional",
            "status": "failed",
            "required": False,
            "return_code": 7,
            "stdout": "",
            "stderr": "",
            "evidence_id": None,
        }
    ]


def test_concurrent_test_records_are_not_lost(tmp_path: Path) -> None:
    package = _package(tmp_path)

    def write(name: str) -> str:
        return record_test_result(package, name=name, status="passed").test_id

    with ThreadPoolExecutor(max_workers=2) as executor:
        test_ids = list(executor.map(write, ["auth", "billing"]))

    report = json.loads((package / "doctor-report.json").read_text(encoding="utf-8"))
    stored = {item["test_id"] for item in report["test_records"]}
    assert stored.issuperset(test_ids)
    assert len(stored) == 2


def test_package_transaction_recovers_stale_lock_and_times_out_on_live_lock(tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()
    lock = package / LOCK_NAME
    lock.write_text("stale", encoding="utf-8")
    stale_time = time.time() - 60
    os.utime(lock, (stale_time, stale_time))

    with package_transaction(package, timeout_seconds=0):
        assert lock.exists()
    assert not lock.exists()

    lock.write_text("live", encoding="utf-8")
    with pytest.raises(TimeoutError, match="Timed out waiting"):
        with package_transaction(package, timeout_seconds=0):
            pass


def test_after_package_inherits_assertions_and_requires_linked_passing_tests(tmp_path: Path) -> None:
    output = tmp_path / "DoctorReports"
    before = create_before_package("Partial", "before", output)
    assertion = add_user_assertion(before, "Invoice omits tax")
    after = create_after_package("Partial", "after", output, before)

    inherited = json.loads((after / "user-assertions.json").read_text(encoding="utf-8"))
    assert [item["assertion_id"] for item in inherited] == [assertion.assertion_id]

    first = write_report_comparison_to_package(before / "doctor-report.json", after)
    first_payload = json.loads((after / first.path).read_text(encoding="utf-8"))
    assert first_payload["status"] == "not_verified"

    record_test_result(
        after,
        name="invoice tax regression",
        status="passed",
        related_assertion_ids=[assertion.assertion_id],
    )
    second = write_report_comparison_to_package(before / "doctor-report.json", after)
    second_payload = json.loads((after / second.path).read_text(encoding="utf-8"))
    assert second_payload["status"] == "candidate_verified"
    assert (after / "ai-task.md").read_text(encoding="utf-8").count("## Report comparison verification evidence") == 1


def test_failed_test_is_a_verification_and_handoff_blocker(tmp_path: Path) -> None:
    package = _package(tmp_path)
    assertion = add_user_assertion(package, "Billing remains wrong")
    record_test_result(
        package,
        name="billing regression",
        status="failed",
        related_assertion_ids=[assertion.assertion_id],
    )
    report = json.loads((package / "doctor-report.json").read_text(encoding="utf-8"))
    report["report_comparison"] = {"status": "not_verified"}
    (package / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")

    verification = run_verification(package, write_back=True)
    compatibility = check_handoff_compatibility(package, "codex")

    assert verification.status == "not_verified"
    assert verification.blocking_test_records == ["billing regression"]
    assert any("billing regression" in item for item in verification.tests_to_rerun)
    assert compatibility.status == "needs_repair"
    assert compatibility.verification_status == "not_verified"
    assert any("blocking test record" in item for item in compatibility.missing_evidence_warnings)


def test_verification_writeback_replaces_stale_commands_and_blocker_request(tmp_path: Path) -> None:
    package = _package(tmp_path)
    first = run_verification(package, write_back=True)
    assert first.status == "missing_evidence"

    report = json.loads((package / "doctor-report.json").read_text(encoding="utf-8"))
    stale_commands = set(report["verification_result"]["next_commands"])
    assert any("compare" in command for command in stale_commands)
    assert "Resolve verification blockers before marking the fix complete." in report["ai_task"]["requested_work"]

    record_test_result(package, name="fixed regression", status="passed")
    report = json.loads((package / "doctor-report.json").read_text(encoding="utf-8"))
    report["report_comparison"] = {"status": "candidate_verified"}
    (package / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")

    second = run_verification(package, write_back=True)
    updated = json.loads((package / "doctor-report.json").read_text(encoding="utf-8"))

    assert second.status == "candidate_verified"
    obsolete_commands = stale_commands.difference(second.next_commands)
    assert not obsolete_commands.intersection(updated["ai_task"]["verification_steps"])
    assert "Resolve verification blockers before marking the fix complete." not in updated["ai_task"]["requested_work"]


def test_automated_results_link_assertions_by_statement(tmp_path: Path) -> None:
    project = tmp_path / "project"
    config = project / ".doctorlink"
    config.mkdir(parents=True)
    (config / "reproduce.yml").write_text(
        "\n".join(
            [
                "reproductions:",
                "  - id: linked",
                "    title: linked reproduction",
                "    kind: command",
                '    command: MODE=test python -c "print(\'ok\')"',
                "    expected: ok",
                "    related_assertion_statements:",
                '      - "User confirmed issue"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    package = _package(tmp_path, "Linked")
    assertion = add_user_assertion(package, "User confirmed issue")
    result = CliRunner().invoke(
        main,
        ["reproduce", "run", "linked", str(project), "--package-dir", str(package), "--json"],
    )

    assert result.exit_code == 0, result.output
    report = json.loads((package / "doctor-report.json").read_text(encoding="utf-8"))
    automated = next(item for item in report["test_records"] if item["test_id"] == "reproduction-linked")
    assert automated["related_assertion_ids"] == [assertion.assertion_id]
