from __future__ import annotations

import pytest

from doctor_link.core.ai_task_templates import (
    HUMAN_ASSERTION_WARNING,
    AITaskTemplateInput,
    get_template,
    list_templates,
    render_ai_task_from_template,
)


def test_list_templates_contains_required_p3_templates() -> None:
    template_ids = {item["template_id"] for item in list_templates()}

    assert {
        "bug_fix",
        "regression_fix",
        "investigation",
        "refactor_risk_review",
        "verification_only",
    }.issubset(template_ids)


def test_render_ai_task_template_preserves_human_assertion_warning() -> None:
    rendered = render_ai_task_from_template(
        "bug_fix",
        AITaskTemplateInput(
            project="Doctor link",
            issue_summary="User-confirmed failure",
            evidence_ids=["ev-1"],
            user_assertions=["assertion-1: user says output is wrong"],
            reproduction_steps=["Run sample command"],
            investigation_boundaries=["Only inspect parser code"],
            forbidden_changes=["Do not rewrite unrelated modules"],
            verification_steps=["Rerun regression test"],
        ),
    )

    assert "# AI Task Template: Bug Fix" in rendered
    assert HUMAN_ASSERTION_WARNING in rendered
    assert "ev-1" in rendered
    assert "assertion-1" in rendered
    assert "Run sample command" in rendered
    assert "Only inspect parser code" in rendered
    assert "Do not rewrite unrelated modules" in rendered
    assert "Rerun regression test" in rendered


def test_each_template_contains_human_assertion_warning() -> None:
    for template in list_templates():
        rendered = render_ai_task_from_template(
            template["template_id"],
            AITaskTemplateInput(project="P3", issue_summary="template check"),
        )
        assert HUMAN_ASSERTION_WARNING in rendered


def test_unknown_template_raises_helpful_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        get_template("missing")

    assert "Unknown AI task template" in str(exc_info.value)
    assert "bug_fix" in str(exc_info.value)
