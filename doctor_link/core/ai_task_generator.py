from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import DiagnosticEvent, ScanResult, TestPlan


HUMAN_CONFIRMED_WARNING = (
    "The human user has confirmed this as the problem. "
    "Do not dismiss it as normal behavior without evidence."
)


def generate_ai_task(scan_result: ScanResult, test_plan: TestPlan, output: Path) -> Path:
    """Generate an AI-ready debugging task draft from scan data."""
    output.mkdir(parents=True, exist_ok=True)
    path = output / "ai-task.md"

    lines = [
        "# AI Debugging Task",
        "",
        "You are helping diagnose a software project using a Doctor link report.",
        "",
        "## Context",
        "",
        f"- Test library: `{scan_result.root}`",
        f"- Files scanned: `{len(scan_result.files)}`",
        "",
        "## Current findings",
        "",
    ]

    if test_plan.missing_categories:
        lines.append("The test library is incomplete. Missing categories:")
        for item in test_plan.missing_categories:
            lines.append(f"- {item}")
    else:
        lines.append("The test library covers the initial static categories.")

    lines.extend(
        [
            "",
            "## Requested work",
            "",
            "1. Review the diagnostic report and JSON data.",
            "2. Identify what information is missing for reliable diagnosis.",
            "3. Propose the next test steps.",
            "4. Do not guess root causes without evidence.",
            "5. If code changes are needed, make the smallest possible change and add verification steps.",
            "",
            "## Investigation boundary",
            "",
            "- Stay within the diagnostic package and test plan unless evidence points elsewhere.",
            "- Do not rewrite unrelated modules without evidence.",
            "",
            "## Verification checklist",
            "",
            "- Confirm the issue is reproducible.",
            "- Confirm the failing category is covered by a test sample.",
            "- Confirm the fix changes the failing result.",
            "- Update Doctor link reports after the fix.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def generate_ai_task_from_event(event: DiagnosticEvent, output: Path) -> Path:
    """Generate an AI-ready task from a full diagnostic event."""
    output.mkdir(parents=True, exist_ok=True)
    path = output / "ai-task.md"

    lines = [
        "# AI Debugging Task",
        "",
        "## Problem summary",
        "",
        event.ai_task.summary or event.summary or "No summary provided.",
        "",
        "## Diagnostic context",
        "",
        f"- Event ID: `{event.event_id}`",
        f"- Project: `{event.project}`",
        f"- Category: `{event.category}`",
        f"- Severity: `{event.severity}`",
        f"- Status: `{event.status}`",
        "",
    ]

    if event.user_assertions:
        lines.extend(["## Human-confirmed issue", "", HUMAN_CONFIRMED_WARNING, ""])
        for assertion in event.user_assertions:
            lines.extend(
                [
                    f"- Statement: {assertion.user_statement}",
                    f"  - Expected: {assertion.expected_behavior or 'N/A'}",
                    f"  - Actual: {assertion.actual_behavior or 'N/A'}",
                    f"  - Why wrong: {assertion.why_user_thinks_it_is_wrong or 'N/A'}",
                    f"  - Next AI instruction: {assertion.next_ai_instruction or 'Use this assertion as the primary diagnosis target.'}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Evidence",
            "",
            *_list([f"{item.evidence_id}: {item.title} ({item.kind})" for item in event.evidence]),
            "",
            "## Reproduction steps",
            "",
            *_numbered(event.reproduce_steps),
            "",
            "## Timeline",
            "",
            *_list([f"Step {step.order}: {step.action} -> {step.status}" for step in event.timeline]),
            "",
            "## Requested work",
            "",
            *_list(event.ai_task.requested_work),
            "",
            "## Investigation boundary",
            "",
            *_list(event.ai_task.investigation_boundary),
            "",
            "## Do not change without evidence",
            "",
            *_list(event.ai_task.do_not_change),
            "",
            "## Verification checklist",
            "",
            *_checkboxes(event.ai_task.verification_steps or event.verification_checklist.items),
            "",
            "## Machine-readable event summary",
            "",
            "```json",
            json.dumps(
                {
                    "event_id": event.event_id,
                    "project": event.project,
                    "category": event.category,
                    "severity": event.severity,
                    "user_assertion_count": len(event.user_assertions),
                    "evidence_count": len(event.evidence),
                },
                ensure_ascii=False,
                indent=2,
            ),
            "```",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]


def _numbered(items: list[str]) -> list[str]:
    return [f"{index}. {item}" for index, item in enumerate(items, start=1)] if items else ["1. No reproduction step recorded."]


def _checkboxes(items: list[str]) -> list[str]:
    return [f"- [ ] {item}" for item in items] if items else ["- [ ] No verification step generated."]
