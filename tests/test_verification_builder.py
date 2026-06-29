from __future__ import annotations

from doctor_link.core.models import AITask, DiagnosticEvent, EvidenceItem, UserAssertion
from doctor_link.core.verification_builder import build_verification_checklist, render_verification_checklist


def test_build_verification_checklist_includes_assertions() -> None:
    event = DiagnosticEvent(
        user_assertions=[UserAssertion(user_statement="Checkout fails on submit")],
        ai_task=AITask(verification_steps=["Run checkout integration test"]),
    )
    checklist = build_verification_checklist(event)
    assert any("Checkout fails on submit" in item for item in checklist.items)
    assert "Run checkout integration test" in checklist.items


def test_build_verification_checklist_adds_evidence_followups() -> None:
    event = DiagnosticEvent(evidence=[EvidenceItem(title="log", content="error")])
    checklist = build_verification_checklist(event)
    assert any("Regenerate the Doctor link diagnostic package" in item for item in checklist.items)


def test_render_verification_checklist_markdown() -> None:
    checklist = build_verification_checklist(DiagnosticEvent())
    rendered = render_verification_checklist(checklist)
    assert "# Fix Verification Checklist" in rendered
    assert "- [ ]" in rendered