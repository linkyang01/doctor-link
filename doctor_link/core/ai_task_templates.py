from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


HUMAN_ASSERTION_WARNING = (
    "The human user has confirmed one or more issues. "
    "Do not dismiss user-confirmed problems as normal behavior without evidence."
)


@dataclass(frozen=True)
class AITaskTemplate:
    template_id: str
    title: str
    purpose: str
    required_sections: list[str]
    expected_outputs: list[str]
    verification_focus: list[str]
    forbidden_changes: list[str] = field(default_factory=list)


@dataclass
class AITaskTemplateInput:
    project: str
    issue_summary: str
    evidence_ids: list[str] = field(default_factory=list)
    user_assertions: list[str] = field(default_factory=list)
    reproduction_steps: list[str] = field(default_factory=list)
    investigation_boundaries: list[str] = field(default_factory=list)
    forbidden_changes: list[str] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)
    verification_steps: list[str] = field(default_factory=list)


TEMPLATES: dict[str, AITaskTemplate] = {
    "bug_fix": AITaskTemplate(
        template_id="bug_fix",
        title="Bug Fix",
        purpose="Find and fix a confirmed defect using package evidence.",
        required_sections=["Evidence", "User assertions", "Reproduction steps", "Investigation boundary"],
        expected_outputs=["Root cause", "Minimal fix plan", "Files changed", "Tests to rerun"],
        verification_focus=["Confirm the original failure is fixed", "Confirm no new regression is introduced"],
    ),
    "regression_fix": AITaskTemplate(
        template_id="regression_fix",
        title="Regression Fix",
        purpose="Compare before and after behavior and repair a regression.",
        required_sections=["Before/after comparison", "Evidence", "User assertions", "Test records"],
        expected_outputs=["Regression cause", "Changed behavior", "Minimal rollback or fix", "Regression test"],
        verification_focus=["Rerun failed regression evidence", "Compare before and after reports"],
    ),
    "investigation": AITaskTemplate(
        template_id="investigation",
        title="Investigation",
        purpose="Investigate a problem without making unsupported conclusions.",
        required_sections=["Evidence", "Timeline", "User assertions", "Unknowns"],
        expected_outputs=["Most likely causes", "Evidence supporting each cause", "Evidence gaps", "Next diagnostic steps"],
        verification_focus=["Collect missing evidence before claiming a fix"],
    ),
    "refactor_risk_review": AITaskTemplate(
        template_id="refactor_risk_review",
        title="Refactor Risk Review",
        purpose="Review whether a proposed refactor risks violating the diagnostic boundary.",
        required_sections=["Investigation boundary", "Forbidden changes", "Evidence", "Verification checklist"],
        expected_outputs=["Risk level", "Risk rationale", "Unsafe change list", "Safe minimal alternative"],
        verification_focus=["Confirm changed files stay inside the agreed scope"],
        forbidden_changes=["Do not expand the repair scope without evidence."],
    ),
    "verification_only": AITaskTemplate(
        template_id="verification_only",
        title="Verification Only",
        purpose="Verify a claimed fix without treating the claim as proof.",
        required_sections=["Verification checklist", "Test records", "Report comparison", "User assertions"],
        expected_outputs=["Verification result", "Missing evidence", "Tests rerun", "Remaining risks"],
        verification_focus=["Do not mark complete unless verification evidence supports it"],
    ),
}


def get_template(template_id: str) -> AITaskTemplate:
    try:
        return TEMPLATES[template_id]
    except KeyError as exc:
        available = ", ".join(sorted(TEMPLATES))
        raise ValueError(f"Unknown AI task template: {template_id}. Available templates: {available}") from exc


def render_ai_task_from_template(template_id: str, data: AITaskTemplateInput) -> str:
    template = get_template(template_id)
    expected_outputs = data.expected_outputs or template.expected_outputs
    forbidden_changes = [*template.forbidden_changes, *data.forbidden_changes]
    verification_steps = data.verification_steps or template.verification_focus
    lines = [
        f"# AI Task Template: {template.title}",
        "",
        f"Project: {data.project or 'Unknown project'}",
        f"Issue summary: {data.issue_summary or 'No issue summary provided.'}",
        "",
        "## Required human assertion rule",
        HUMAN_ASSERTION_WARNING,
        "",
        "## Purpose",
        template.purpose,
        "",
        "## Required sections to inspect",
        *_bullets(template.required_sections),
        "",
        "## Evidence IDs",
        *_bullets(data.evidence_ids, empty="No evidence IDs provided."),
        "",
        "## User assertions",
        *_bullets(data.user_assertions, empty="No user assertions provided."),
        "",
        "## Reproduction steps",
        *_bullets(data.reproduction_steps, empty="No reproduction steps provided."),
        "",
        "## Investigation boundaries",
        *_bullets(data.investigation_boundaries, empty="No investigation boundaries provided."),
        "",
        "## Forbidden changes",
        *_bullets(forbidden_changes, empty="No forbidden changes provided."),
        "",
        "## Expected outputs",
        *_bullets(expected_outputs),
        "",
        "## Verification steps",
        *_bullets(verification_steps),
        "",
    ]
    return "\n".join(lines)


def list_templates() -> list[dict[str, Any]]:
    return [
        {
            "template_id": template.template_id,
            "title": template.title,
            "purpose": template.purpose,
            "required_sections": list(template.required_sections),
            "expected_outputs": list(template.expected_outputs),
            "verification_focus": list(template.verification_focus),
        }
        for template in TEMPLATES.values()
    ]


def _bullets(values: list[str], empty: str | None = None) -> list[str]:
    if not values:
        return [f"- {empty}"] if empty else ["- None"]
    return [f"- {value}" for value in values]
