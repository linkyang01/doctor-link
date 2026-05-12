from __future__ import annotations

from doctor_link.core.models import DiagnosticEvent, ProblemMap


def build_problem_map(event: DiagnosticEvent) -> ProblemMap:
    """Build a problem map from the current diagnostic event.

    This function is intentionally conservative. It does not invent root causes.
    It organizes available evidence, timeline failures, and human assertions.
    """
    failure_steps = [step for step in event.timeline if step.is_failure_point or step.status == "failed"]
    assertions = event.user_assertions

    human_problem = assertions[-1].user_statement if assertions else event.problem_map.human_confirmed_problem
    failure_stage = event.problem_map.failure_stage
    if failure_steps:
        failure_stage = failure_steps[-1].action
    elif assertions:
        failure_stage = "human_confirmed_issue"

    next_actions = list(event.problem_map.next_actions)
    if assertions:
        next_actions.insert(0, "Use the human-confirmed issue as the primary diagnosis target.")
        if assertions[-1].next_ai_instruction:
            next_actions.insert(1, assertions[-1].next_ai_instruction)

    evidence_ids = set(event.problem_map.evidence_ids)
    for step in failure_steps:
        evidence_ids.update(step.evidence_ids)
    for assertion in assertions:
        evidence_ids.update(assertion.related_evidence_ids)

    return ProblemMap(
        user_symptom=event.problem_map.user_symptom or event.summary,
        failure_stage=failure_stage,
        possible_root_causes=event.problem_map.possible_root_causes,
        ruled_out_causes=event.problem_map.ruled_out_causes,
        related_modules=event.problem_map.related_modules,
        next_actions=next_actions,
        human_confirmed_problem=human_problem,
        evidence_ids=sorted(evidence_ids),
    )


def render_problem_map(problem_map: ProblemMap) -> str:
    """Render a human-readable problem map."""
    return "\n".join(
        [
            "# Problem Map",
            "",
            "## User symptom",
            problem_map.user_symptom or "Not provided.",
            "",
            "## Failure stage",
            f"`{problem_map.failure_stage}`",
            "",
            "## Human-confirmed problem",
            problem_map.human_confirmed_problem or "No human-confirmed issue has been recorded.",
            "",
            "## Possible root causes",
            *_list(problem_map.possible_root_causes),
            "",
            "## Ruled out causes",
            *_list(problem_map.ruled_out_causes),
            "",
            "## Related modules",
            *_list(problem_map.related_modules),
            "",
            "## Evidence IDs",
            *_list(problem_map.evidence_ids),
            "",
            "## Next actions",
            *_list(problem_map.next_actions),
            "",
        ]
    )


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]
