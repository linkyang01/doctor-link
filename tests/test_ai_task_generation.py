from __future__ import annotations

from pathlib import Path

from doctor_link.core.ai_handoff_template import build_ai_code_task_template
from doctor_link.core.ai_task_generator import generate_ai_task, generate_ai_task_from_event
from doctor_link.core.models import (
    AITask,
    DiagnosticEvent,
    EvidenceItem,
    ScanResult,
    TestPlan as DoctorTestPlan,
    TimelineStep,
    UserAssertion,
    VerificationChecklist,
)
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.web_package_reader import read_package_view


def test_generate_ai_task_covers_complete_and_incomplete_plans(tmp_path: Path) -> None:
    scan = ScanResult(root=tmp_path)
    incomplete = DoctorTestPlan(
        title="Incomplete",
        missing_categories=["missing logs"],
        recommended_tests=[],
        detected_extensions={},
    )
    complete = DoctorTestPlan(
        title="Complete",
        missing_categories=[],
        recommended_tests=[],
        detected_extensions={},
    )

    incomplete_path = generate_ai_task(scan, incomplete, tmp_path / "incomplete")
    complete_path = generate_ai_task(scan, complete, tmp_path / "complete")

    assert "missing logs" in incomplete_path.read_text(encoding="utf-8")
    assert "covers the initial static categories" in complete_path.read_text(encoding="utf-8")


def test_generate_ai_task_from_rich_event(tmp_path: Path) -> None:
    event = DiagnosticEvent(
        project="demo",
        category="startup",
        summary="startup failed",
        status="investigating",
        evidence=[EvidenceItem(evidence_id="ev-1", title="app log", kind="log")],
        timeline=[TimelineStep(order=1, action="start", status="failed")],
        reproduce_steps=["run the app"],
        user_assertions=[
            UserAssertion(
                assertion_id="assert-1",
                user_statement="startup is broken",
                expected_behavior="starts",
                actual_behavior="crashes",
                why_user_thinks_it_is_wrong="no service is available",
                next_ai_instruction="inspect startup logs",
            )
        ],
        ai_task=AITask(
            summary="diagnose startup",
            requested_work=["find the failing branch"],
            investigation_boundary=["doctor_link/"],
            do_not_change=["unrelated modules"],
            verification_steps=["rerun startup"],
        ),
    )

    path = generate_ai_task_from_event(event, tmp_path)
    text = path.read_text(encoding="utf-8")

    assert "startup is broken" in text
    assert "ev-1" in text
    assert "rerun startup" in text
    assert '"evidence_count": 1' in text


def test_generate_ai_task_from_minimal_event_uses_fallbacks(tmp_path: Path) -> None:
    event = DiagnosticEvent(
        project="minimal",
        verification_checklist=VerificationChecklist(items=[]),
    )

    text = generate_ai_task_from_event(event, tmp_path).read_text(encoding="utf-8")

    assert "No summary provided" in text
    assert "No reproduction step recorded" in text
    assert "No verification step generated" in text


def test_build_ai_code_task_template_from_package(tmp_path: Path) -> None:
    package = build_diagnostic_package(
        DiagnosticEvent(project="template-demo", summary="template test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None

    template = build_ai_code_task_template(read_package_view(package.root_dir))

    assert template.title == "Doctor link task: template-demo"
    assert "Human-confirmed assertions" in template.body
    assert "Do not mark the issue complete" in template.body
