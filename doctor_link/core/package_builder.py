from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from doctor_link.adapters.registry import resolve_adapter_name
from doctor_link.core.diagnosis_strategy import DiagnosisStrategy
from doctor_link.core.models import (
    AITask,
    DiagnosticEvent,
    DiagnosticPackage,
    EvidenceItem,
    ProblemMap,
    ScanResult,
    TestPlan,
    TimelineStep,
    VerificationChecklist,
    utc_now_iso,
)
from doctor_link.core.problem_map_builder import build_problem_map, render_problem_map
from doctor_link.core.verification_builder import build_verification_checklist, render_verification_checklist


def event_from_scan(
    scan_result: ScanResult,
    test_plan: TestPlan,
    project: str = "Doctor link",
    strategy: DiagnosisStrategy | None = None,
    symptom: str | None = None,
) -> DiagnosticEvent:
    """Create a diagnostic event from a library scan and test plan."""
    evidence = [
        EvidenceItem(
            kind="scan_result",
            title="Library scan summary",
            source="doctor-link scan",
            content=f"Scanned {len(scan_result.files)} file(s) from {scan_result.root}",
        )
    ]

    timeline = [
        TimelineStep(
            order=1,
            action="scan_library",
            target=str(scan_result.root),
            expected_result="Test library can be scanned and categorized.",
            actual_result=f"Detected {len(scan_result.files)} file(s).",
            status="passed",
            evidence_ids=[evidence[0].evidence_id],
        )
    ]

    missing_count = len(test_plan.missing_categories)
    strategy = strategy or DiagnosisStrategy()
    user_symptom = symptom or strategy.symptom or "Initial diagnostic package generated from a scanned test library."
    failure_stage = strategy.failure_stage or ("test_library_completeness" if missing_count else "ready_for_playback_testing")
    investigation_boundary = strategy.investigation_boundary or ["diagnostic package", "test plan", "scan result"]
    do_not_change = strategy.do_not_change or ["Do not modify unrelated application code without evidence."]
    reproduce_steps = strategy.default_commands or [f"Run doctor-link report {scan_result.root}"]

    problem_map = ProblemMap(
        user_symptom=user_symptom,
        failure_stage=failure_stage,
        possible_root_causes=test_plan.missing_categories[:10],
        ruled_out_causes=[],
        related_modules=["test_planner", "scanner"],
        next_actions=test_plan.recommended_tests[:10] or ["Add test samples and rerun Doctor link."],
        human_confirmed_problem=None,
        evidence_ids=[item.evidence_id for item in evidence],
    )

    ai_task = AITask(
        title="Review Doctor link diagnostic package",
        summary=user_symptom,
        requested_work=[
            "Review the diagnostic report and JSON payload.",
            "Do not guess root causes without evidence.",
            "Identify missing test samples or missing runtime evidence.",
        ],
        investigation_boundary=investigation_boundary,
        do_not_change=do_not_change,
        evidence_ids=[item.evidence_id for item in evidence],
        verification_steps=strategy.verification_rules
        or [
            "Confirm the diagnostic package was generated.",
            "Confirm missing categories are listed.",
            "Confirm next actions are explicit.",
        ],
    )

    adapter_name = resolve_adapter_name(scan_result.root)
    event = DiagnosticEvent(
        project=project,
        adapter=adapter_name,
        severity="warning" if missing_count else "info",
        category="test_library_incomplete" if missing_count else "diagnostic_package_created",
        summary=user_symptom,
        environment={"generated_at": utc_now_iso(), "library_root": str(scan_result.root)},
        timeline=timeline,
        evidence=evidence,
        reproduce_steps=reproduce_steps,
        problem_map=problem_map,
        ai_task=ai_task,
        verification_checklist=VerificationChecklist(items=[]),
        status="ai_ready",
    )
    return finalize_event(event)


def finalize_event(event: DiagnosticEvent) -> DiagnosticEvent:
    """Apply problem-map and verification builders to a diagnostic event."""
    event.problem_map = build_problem_map(event)
    event.verification_checklist = build_verification_checklist(event)
    return event


def build_diagnostic_package(event: DiagnosticEvent, output_root: Path) -> DiagnosticPackage:
    """Write a standard diagnostic package to disk."""
    event = finalize_event(event)
    safe_project = _safe_name(event.project or "project")
    safe_issue = _safe_name(event.category or "issue")
    timestamp = utc_now_iso().replace(":", "-")
    package_root = output_root / f"{timestamp}_{safe_project}_{safe_issue}"

    evidence_root = package_root / "evidence"
    for subdir in [
        evidence_root,
        evidence_root / "logs",
        evidence_root / "screenshots",
        evidence_root / "command-output",
        evidence_root / "test-results",
        evidence_root / "attachments",
    ]:
        subdir.mkdir(parents=True, exist_ok=True)

    files = {
        "summary": package_root / "summary.md",
        "problem_map": package_root / "problem-map.md",
        "timeline": package_root / "timeline.md",
        "evidence_list": package_root / "evidence-list.md",
        "doctor_report_md": package_root / "doctor-report.md",
        "doctor_report_json": package_root / "doctor-report.json",
        "ai_context": package_root / "ai-context.json",
        "reproduce_steps": package_root / "reproduce-steps.md",
        "ai_task": package_root / "ai-task.md",
        "investigation_boundary": package_root / "investigation-boundary.md",
        "verification": package_root / "fix-verification-checklist.md",
        "user_assertions": package_root / "user-assertions.json",
        "environment": evidence_root / "environment.json",
    }

    files["summary"].write_text(_render_summary(event), encoding="utf-8")
    files["problem_map"].write_text(render_problem_map(event.problem_map), encoding="utf-8")
    files["timeline"].write_text(_render_timeline(event), encoding="utf-8")
    files["evidence_list"].write_text(_render_evidence_list(event), encoding="utf-8")
    files["doctor_report_md"].write_text(_render_doctor_report(event), encoding="utf-8")
    files["doctor_report_json"].write_text(_json(event.to_dict()), encoding="utf-8")
    files["ai_context"].write_text(_json(_ai_context(event)), encoding="utf-8")
    files["reproduce_steps"].write_text(_render_reproduce_steps(event), encoding="utf-8")
    files["ai_task"].write_text(_render_ai_task(event), encoding="utf-8")
    files["investigation_boundary"].write_text(_render_investigation_boundary(event), encoding="utf-8")
    files["verification"].write_text(render_verification_checklist(event.verification_checklist), encoding="utf-8")
    files["user_assertions"].write_text(_json([item.to_dict() for item in event.user_assertions]), encoding="utf-8")
    files["environment"].write_text(_json(event.environment), encoding="utf-8")

    return DiagnosticPackage(
        event_id=event.event_id,
        root_dir=package_root,
        status=event.status,
        files={name: str(path) for name, path in files.items()},
    )


def _render_summary(event: DiagnosticEvent) -> str:
    assertions = "Yes" if event.user_assertions else "No"
    return "\n".join(
        [
            "# Doctor link Summary",
            "",
            f"- Project: `{event.project}`",
            f"- Category: `{event.category}`",
            f"- Severity: `{event.severity}`",
            f"- Status: `{event.status}`",
            f"- User confirmed problem: `{assertions}`",
            "",
            "## Summary",
            event.summary or "No summary provided.",
            "",
            "## Next action",
            event.problem_map.next_actions[0] if event.problem_map.next_actions else "No next action generated.",
            "",
        ]
    )


def _render_problem_map(event: DiagnosticEvent) -> str:
    pm = event.problem_map
    lines = [
        "# Problem Map",
        "",
        f"## User symptom\n\n{pm.user_symptom or 'Not provided.'}",
        "",
        f"## Failure stage\n\n`{pm.failure_stage}`",
        "",
        "## Human confirmed problem",
        pm.human_confirmed_problem or "No user assertion has been recorded yet.",
        "",
        "## Possible root causes",
        *_list(pm.possible_root_causes),
        "",
        "## Ruled out causes",
        *_list(pm.ruled_out_causes),
        "",
        "## Related modules",
        *_list(pm.related_modules),
        "",
        "## Next actions",
        *_list(pm.next_actions),
        "",
    ]
    return "\n".join(lines)


def _render_timeline(event: DiagnosticEvent) -> str:
    lines = ["# Timeline", ""]
    if not event.timeline:
        lines.append("No timeline steps recorded.")
    for step in sorted(event.timeline, key=lambda item: item.order):
        marker = " **Failure point**" if step.is_failure_point else ""
        lines.extend(
            [
                f"## Step {step.order}: {step.action}{marker}",
                "",
                f"- Time: `{step.timestamp}`",
                f"- Target: `{step.target or 'N/A'}`",
                f"- Status: `{step.status}`",
                f"- Expected: {step.expected_result or 'N/A'}",
                f"- Actual: {step.actual_result or 'N/A'}",
                f"- Evidence: {', '.join(step.evidence_ids) if step.evidence_ids else 'None'}",
                f"- User note: {step.user_note or 'N/A'}",
                "",
            ]
        )
    return "\n".join(lines)


def _render_evidence_list(event: DiagnosticEvent) -> str:
    lines = ["# Evidence List", ""]
    if not event.evidence:
        lines.append("No evidence recorded.")
    for item in event.evidence:
        lines.extend(
            [
                f"## {item.title}",
                "",
                f"- ID: `{item.evidence_id}`",
                f"- Kind: `{item.kind}`",
                f"- Source: `{item.source}`",
                f"- Path: `{item.path or 'N/A'}`",
                f"- Related step: `{item.related_step_id or 'N/A'}`",
                "",
                item.content or "No content preview.",
                "",
            ]
        )
    return "\n".join(lines)


def _render_doctor_report(event: DiagnosticEvent) -> str:
    return "\n".join(
        [
            "# Doctor Report",
            "",
            f"Event ID: `{event.event_id}`",
            f"Project: `{event.project}`",
            f"Adapter: `{event.adapter}`",
            f"Occurred at: `{event.occurred_at}`",
            f"Severity: `{event.severity}`",
            f"Category: `{event.category}`",
            f"Status: `{event.status}`",
            "",
            "## Summary",
            event.summary or "No summary provided.",
            "",
            "## User assertions",
            *_list([item.user_statement for item in event.user_assertions]),
            "",
            "## Verification",
            *_list(event.verification_checklist.items),
            "",
        ]
    )


def _render_reproduce_steps(event: DiagnosticEvent) -> str:
    return "\n".join(["# Reproduce Steps", "", *_numbered(event.reproduce_steps), ""])


def _render_ai_task(event: DiagnosticEvent) -> str:
    lines = [
        "# AI Debugging Task",
        "",
        "## Problem summary",
        event.ai_task.summary or event.summary or "No summary provided.",
        "",
    ]

    if event.user_assertions:
        lines.extend(
            [
                "## Human-confirmed issue",
                "The human user has confirmed this as the problem. Do not dismiss it as normal behavior without evidence.",
                "",
            ]
        )
        for assertion in event.user_assertions:
            lines.extend(
                [
                    f"- Statement: {assertion.user_statement}",
                    f"  - Expected: {assertion.expected_behavior or 'N/A'}",
                    f"  - Actual: {assertion.actual_behavior or 'N/A'}",
                    f"  - Why wrong: {assertion.why_user_thinks_it_is_wrong or 'N/A'}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Evidence",
            *_list([f"{item.evidence_id}: {item.title}" for item in event.evidence]),
            "",
            "## Requested work",
            *_list(event.ai_task.requested_work),
            "",
            "## Investigation boundary",
            *_list(event.ai_task.investigation_boundary),
            "",
            "## Do not change",
            *_list(event.ai_task.do_not_change),
            "",
            "## Verification steps",
            *_list(event.ai_task.verification_steps or event.verification_checklist.items),
            "",
        ]
    )
    return "\n".join(lines)


def _render_investigation_boundary(event: DiagnosticEvent) -> str:
    return "\n".join(
        [
            "# Investigation Boundary",
            "",
            "## Investigate",
            *_list(event.ai_task.investigation_boundary),
            "",
            "## Do not change without evidence",
            *_list(event.ai_task.do_not_change),
            "",
        ]
    )


def _render_verification(event: DiagnosticEvent) -> str:
    return "\n".join(["# Fix Verification Checklist", "", *_checkboxes(event.verification_checklist.items), ""])


def _ai_context(event: DiagnosticEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "project": event.project,
        "summary": event.summary,
        "category": event.category,
        "severity": event.severity,
        "status": event.status,
        "evidence": [item.to_dict() for item in event.evidence],
        "timeline": [item.to_dict() for item in event.timeline],
        "user_assertions": [item.to_dict() for item in event.user_assertions],
        "problem_map": event.problem_map.to_dict(),
        "ai_task": event.ai_task.to_dict(),
        "verification_checklist": event.verification_checklist.to_dict(),
    }


def _json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-") or "item"


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]


def _numbered(items: list[str]) -> list[str]:
    return [f"{index}. {item}" for index, item in enumerate(items, start=1)] if items else ["1. No reproduce steps recorded."]


def _checkboxes(items: list[str]) -> list[str]:
    return [f"- [ ] {item}" for item in items] if items else ["- [ ] No verification step generated."]