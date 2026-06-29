from __future__ import annotations

from doctor_link.core.models import DiagnosticEvent, ProblemMap, TimelineStep, UserAssertion
from doctor_link.core.problem_map_builder import build_problem_map, render_problem_map


def test_build_problem_map_uses_failed_timeline_step() -> None:
    event = DiagnosticEvent(
        summary="demo",
        timeline=[
            TimelineStep(order=1, action="scan", status="passed"),
            TimelineStep(order=2, action="api_call", status="failed", is_failure_point=True, evidence_ids=["evd_1"]),
        ],
        problem_map=ProblemMap(user_symptom="API error"),
    )
    problem_map = build_problem_map(event)
    assert problem_map.failure_stage == "api_call"
    assert "evd_1" in problem_map.evidence_ids


def test_build_problem_map_prioritizes_user_assertions() -> None:
    assertion = UserAssertion(user_statement="Users endpoint returns 500", next_ai_instruction="Fix config lookup")
    event = DiagnosticEvent(
        summary="demo",
        user_assertions=[assertion],
        problem_map=ProblemMap(next_actions=["old action"]),
    )
    problem_map = build_problem_map(event)
    assert problem_map.human_confirmed_problem == "Users endpoint returns 500"
    assert problem_map.next_actions[0] == "Use the human-confirmed issue as the primary diagnosis target."


def test_render_problem_map_includes_sections() -> None:
    rendered = render_problem_map(ProblemMap(user_symptom="slow startup", failure_stage="boot"))
    assert "# Problem Map" in rendered
    assert "slow startup" in rendered