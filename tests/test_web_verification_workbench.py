from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view


def _package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link verification", category="web", summary="Verification workbench sample"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_verification_workbench_renders_status_signals_and_coverage(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "not_verified",
                "missing_evidence": ["ev-1"],
                "tests_to_rerun": ["rerun playback"],
                "next_commands": ["doctor-link record package"],
                "report_comparison_status": "not_verified",
                "vly_core_proof_status": "NO-GO",
                "assertion_test_coverage": [
                    {
                        "assertion_id": "assertion-1",
                        "statement": "User confirmed playback issue",
                        "status": "missing_coverage",
                        "covered_by_test_records": [],
                    },
                    {
                        "assertion_id": "assertion-2",
                        "statement": "Subtitle issue checked",
                        "status": "covered",
                        "covered_by_test_records": ["test-1"],
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    html = render_package_detail_html(read_package_view(package_dir))

    assert "Verification Workbench" in html
    assert "Report comparison" in html
    assert "not_verified" in html
    assert "Vly Core Proof" in html
    assert "NO-GO" in html
    assert "Assertion Test Coverage" in html
    assert "1/2 covered" in html
    assert "assertion-1" in html
    assert "missing_coverage" in html
    assert "assertion-2" in html
    assert "test-1" in html
    assert "The UI must not claim a fix is complete when evidence is missing." in html


def test_verification_workbench_derives_unknown_assertion_coverage(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    (package_dir / "user-assertions.json").write_text(
        json.dumps(
            [
                {
                    "assertion_id": "assertion-a",
                    "user_statement": "This user assertion needs a test",
                }
            ]
        ),
        encoding="utf-8",
    )
    (package_dir / "verification-result.json").write_text(
        json.dumps(
            {
                "status": "missing_evidence",
                "report_comparison_status": None,
                "vly_core_proof_status": None,
            }
        ),
        encoding="utf-8",
    )

    html = render_package_detail_html(read_package_view(package_dir))

    assert "Assertion Test Coverage" in html
    assert "assertion-a" in html
    assert "unknown" in html
    assert "0/1 covered" in html
    assert "report comparison: unknown" in html
    assert "vly core proof: unknown" in html


def test_verification_workbench_uses_doctor_report_embedded_result(tmp_path: Path) -> None:
    package_dir = _package(tmp_path)
    report = json.loads((package_dir / "doctor-report.json").read_text(encoding="utf-8"))
    report["verification_result"] = {
        "report_comparison_status": "candidate_verified",
        "vly_core_proof_status": "GO",
        "assertion_test_coverage": [
            {
                "assertion_id": "embedded-assertion",
                "statement": "Embedded coverage",
                "status": "covered",
                "covered_by_test_records": ["embedded-test"],
            }
        ],
    }
    (package_dir / "doctor-report.json").write_text(json.dumps(report), encoding="utf-8")
    (package_dir / "verification-result.json").write_text(json.dumps({"status": "candidate_verified"}), encoding="utf-8")

    html = render_package_detail_html(read_package_view(package_dir))

    assert "candidate_verified" in html
    assert "GO" in html
    assert "embedded-assertion" in html
    assert "embedded-test" in html
