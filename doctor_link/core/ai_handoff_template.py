from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from doctor_link.core.web_package_reader import DiagnosticPackageView
from doctor_link.core.web_review_summary import verification_status_reasons


@dataclass
class AICodeTaskTemplate:
    title: str
    body: str


def build_ai_code_task_template(view: DiagnosticPackageView) -> AICodeTaskTemplate:
    """Build a copy-ready task template for AI Coding tools.

    The template is generated from the diagnostic package view and does not
    modify the package.
    """
    report = _dict(view.json_data("doctor_report"))
    verification = _dict(view.json_data("verification_result"))
    assertions = _list(view.json_data("user_assertions"))
    task = view.text("ai_task") or "Missing ai-task.md"
    boundary = view.text("investigation_boundary") or "Missing investigation-boundary.md"
    checklist = view.text("verification_checklist") or "Missing fix-verification-checklist.md"
    reasons = verification_status_reasons(view)

    project = _first([
        _nested(report, ["event", "project"]),
        report.get("project"),
        view.title,
    ])
    status = str(verification.get("status") or _nested(report, ["verification_result", "status"]) or "unknown")
    title = f"Doctor link task: {project}"
    assertion_count = len(assertions)

    body = "\n".join(
        [
            "# Doctor link AI Code Task",
            "",
            f"Project: {project}",
            f"Verification status: {status}",
            f"User assertions: {assertion_count}",
            "",
            "## Required rule",
            "Use evidence from the diagnostic package before drawing conclusions. Human-confirmed assertions must be treated as first-class diagnostic signals.",
            "",
            "## Task",
            task,
            "",
            "## Investigation boundary",
            boundary,
            "",
            "## Verification checklist",
            checklist,
            "",
            "## Verification status reasons",
            *[f"- {reason}" for reason in reasons],
            "",
            "## Expected output",
            "- Explain the likely cause using cited package evidence.",
            "- Propose a minimal fix scope.",
            "- State which tests must be rerun.",
            "- Do not mark the issue complete until verification evidence supports it.",
            "",
        ]
    )
    return AICodeTaskTemplate(title=title, body=body)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nested(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first(values: list[Any]) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Unknown project"
