from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.verification_runner import run_verification


def _build_package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="verification", summary="Verification test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def _read_report(package_dir: Path) -> dict:
    return json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))


def _write_report(package_dir: Path, payload: dict) -> None:
    (package_dir / "doctor-report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_verify_reports_missing_evidence_when_no_tests_or_comparison(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)

    result = run_verification(package_dir)

    assert result.status == "missing_evidence"
    assert "test_records" in result.missing_evidence
    assert "report_comparison" in result.missing_evidence
    assert (package_dir / "verification-plan.md").exists()
    assert (package_dir / "verification-result.json").exists()
    assert "doctor-link record" in "\n".join(result.next_commands)


def test_verify_reports_not_verified_when_comparison_not_verified(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    payload = _read_report(package_dir)
    payload["evidence"] = [{"evidence_id": "evd_1"}]
    payload["test_records"] = [{"name": "rerun"}]
    payload["report_comparison"] = {"status": "not_verified"}
    _write_report(package_dir, payload)

    result = run_verification(package_dir)

    assert result.status == "not_verified"
    assert "Report comparison says the fix is not verified." in result.notes


def test_verify_reports_candidate_verified_when_inputs_are_complete(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    payload = _read_report(package_dir)
    payload["evidence"] = [{"evidence_id": "evd_1"}]
    payload["test_records"] = [{"name": "rerun"}]
    payload["report_comparison"] = {"status": "candidate_verified"}
    payload["vly_core_proof"] = {"go_no_go": "GO"}
    _write_report(package_dir, payload)

    result = run_verification(package_dir)

    assert result.status == "candidate_verified"
    assert result.report_comparison_status == "candidate_verified"
    assert result.vly_core_proof_status == "GO"
    assert result.missing_evidence == []


def test_verify_write_back_updates_package_context(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    payload = _read_report(package_dir)
    payload["evidence"] = [{"evidence_id": "evd_1"}]
    payload["test_records"] = [{"name": "rerun"}]
    payload["report_comparison"] = {"status": "candidate_verified"}
    _write_report(package_dir, payload)

    result = run_verification(package_dir, write_back=True)

    updated = _read_report(package_dir)
    assert updated["verification_result"]["status"] == result.status
    assert "Verification runner result" in (package_dir / "summary.md").read_text(encoding="utf-8")
    assert "Verification runner result" in (package_dir / "ai-task.md").read_text(encoding="utf-8")


def test_verify_reads_user_assertions_from_file(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    (package_dir / "user-assertions.json").write_text(
        json.dumps([{"user_statement": "Audio is missing"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    result = run_verification(package_dir)

    assert result.user_assertion_count == 1
    assert any("Audio is missing" in item for item in result.tests_to_rerun)
