from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def event_from_scan(scan_result: ScanResult, test_plan: TestPlan, project: str = "Doctor link") -> DiagnosticEvent:
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
            action="Scan library",
            target=str(scan_result.root),
            expected_result="Identify files and formats for diagnostics",
            actual_result=f"Found {len(scan_result.files)} file(s)",
            evidence_ids=[evidence[0].evidence_id],
            status="done",
        )
    ]

    problem_map = ProblemMap(
        symptoms=[f"{len(scan_result.files)} media-related file(s) need diagnostic coverage"],
        affected_files=[str(item.path) for item in scan_result.files],
        likely_areas=["format coverage", "playback compatibility", "transcoding pipeline"],
    )

    return DiagnosticEvent(
        project=project,
        category="library-diagnostics",
        summary="Generated diagnostic event from scanned library",
        details="Scan results and generated test plan were converted into a Doctor link diagnostic package.",
        evidence=evidence,
        timeline=timeline,
        problem_map=problem_map,
        test_plan=test_plan,
    )


def build_diagnostic_package(event: DiagnosticEvent, output_dir: Path) -> DiagnosticPackage:
    """Build and write a standard diagnostic package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    package = DiagnosticPackage(event=event)
    package_dir = output_dir / package.package_id
    package_dir.mkdir(parents=True, exist_ok=True)
    package.root_dir = package_dir

    _write_markdown(package_dir / "summary.md", _render_summary(event, package.package_id))
    _write_markdown(package_dir / "timeline.md", _render_timeline(event.timeline))
    _write_markdown(package_dir / "problem-map.md", _render_problem_map(event.problem_map))
    _write_markdown(package_dir / "evidence-list.md", _render_evidence(event.evidence))
    _write_markdown(package_dir / "test-plan.md", _render_test_plan(event.test_plan))
    _write_markdown(package_dir / "reproduce-steps.md", _render_reproduce_steps(event))
    _write_markdown(package_dir / "fix-verification-checklist.md", _render_verification(event.verification_checklist))
    _write_markdown(package_dir / "ai-task.md", _render_ai_task(event.ai_task))
    _write_markdown(package_dir / "investigation-boundary.md", _render_investigation_boundary(event))
    _write_markdown(package_dir / "doctor-report.md", _render_doctor_report(event, package.package_id))
    _write_json(package_dir / "doctor-report.json", _package_payload(event, package.package_id))
    _write_json(package_dir / "ai-context.json", _ai_context_payload(event, package.package_id))
    _write_json(package_dir / "user-assertions.json", [])
    return package


def _package_payload(event: DiagnosticEvent, package_id: str) -> dict[str, Any]:
    return {
        "package_id": package_id,
        "event": event.to_dict(),
        "files": [
            "summary.md",
            "timeline.md",
            "problem-map.md",
            "evidence-list.md",
            "test-plan.md",
            "reproduce-steps.md",
            "fix-verification-checklist.md",
            "ai-task.md",
            "investigation-boundary.md",
            "doctor-report.md",
            "doctor-report.json",
            "ai-context.json",
            "user-assertions.json",
        ],
    }


def _ai_context_payload(event: DiagnosticEvent, package_id: str) -> dict[str, Any]:
    return {
        "package_id": package_id,
        "project": event.project,
        "category": event.category,
        "summary": event.summary,
        "details": event.details,
        "problem_map": event.problem_map.to_dict(),
        "evidence": [item.to_dict() for item in event.evidence],
        "timeline": [step.to_dict() for step in event.timeline],
        "test_plan": event.test_plan.to_dict(),
        "verification_checklist": event.verification_checklist.to_dict(),
        "ai_task": event.ai_task.to_dict(),
    }


def _render_summary(event: DiagnosticEvent, package_id: str) -> str:
    return f"""# Doctor Link Diagnostic Summary

- Package ID: `{package_id}`
- Project: {event.project}
- Category: {event.category}
- Created: {event.created_at}

## Summary

{event.summary}

## Details

{event.details or 'No additional details provided.'}
"""


def _render_timeline(timeline: list[TimelineStep]) -> str:
    lines = ["# Timeline", ""]
    for step in sorted(timeline, key=lambda item: item.order):
        lines.extend(
            [
                f"## {step.order}. {step.action}",
                "",
                f"- Target: {step.target}",
                f"- Expected: {step.expected_result}",
                f"- Actual: {step.actual_result}",
                f"- Status: {step.status}",
                f"- Evidence IDs: {', '.join(step.evidence_ids) if step.evidence_ids else 'None'}",
                "",
            ]
        )
    return "\n".join(lines)


def _render_problem_map(problem_map: ProblemMap) -> str:
    return "\n".join(
        [
            "# Problem Map",
            "",
            "## Symptoms",
            *_bullet(problem_map.symptoms),
            "",
            "## Affected Files",
            *_bullet(problem_map.affected_files),
            "",
            "## Likely Areas",
            *_bullet(problem_map.likely_areas),
            "",
        ]
    )


def _render_evidence(evidence: list[EvidenceItem]) -> str:
    lines = ["# Evidence List", ""]
    for item in evidence:
        lines.extend(
            [
                f"## {item.evidence_id}: {item.title}",
                "",
                f"- Kind: {item.kind}",
                f"- Source: {item.source}",
                f"- Path: {item.path or 'N/A'}",
                "",
                item.content or "No content provided.",
                "",
            ]
        )
    return "\n".join(lines)


def _render_test_plan(test_plan: TestPlan) -> str:
    lines = ["# Test Plan", ""]
    for area in test_plan.areas:
        lines.extend([f"## {area.name}", ""])
        lines.extend(_bullet(area.checks))
        lines.append("")
    return "\n".join(lines)


def _render_reproduce_steps(event: DiagnosticEvent) -> str:
    return "\n".join(
        [
            "# Reproduce Steps",
            "",
            "1. Confirm the affected project and package ID.",
            "2. Review `problem-map.md` and `evidence-list.md`.",
            "3. Execute the checks listed in `test-plan.md`.",
            "4. Record observed behavior in `timeline.md` before applying fixes.",
            "",
            f"Context: {event.summary}",
            "",
        ]
    )


def _render_verification(checklist: VerificationChecklist) -> str:
    lines = ["# Fix Verification Checklist", ""]
    for item in checklist.items:
        lines.append(f"- [ ] {item}")
    lines.append("")
    return "\n".join(lines)


def _render_ai_task(ai_task: AITask) -> str:
    lines = ["# AI Task", "", "## Prompt", "", ai_task.prompt, "", "## Constraints", ""]
    lines.extend(_bullet(ai_task.constraints))
    lines.extend(["", "## Expected Outputs", ""])
    lines.extend(_bullet(ai_task.expected_outputs))
    lines.append("")
    return "\n".join(lines)


def _render_investigation_boundary(event: DiagnosticEvent) -> str:
    return "\n".join(
        [
            "# Investigation Boundary",
            "",
            "## In Scope",
            "- Files, evidence, and checks referenced in this package.",
            "- Reproduction and verification steps listed in this package.",
            "",
            "## Out of Scope",
            "- Large refactors not required to resolve the described issue.",
            "- Unrelated code style changes.",
            "",
            f"Primary issue: {event.summary}",
            "",
        ]
    )


def _render_doctor_report(event: DiagnosticEvent, package_id: str) -> str:
    return "\n".join(
        [
            "# Doctor Report",
            "",
            f"Package `{package_id}` is ready for human and AI-assisted diagnosis.",
            "",
            "Recommended order:",
            "",
            "1. Read `summary.md`.",
            "2. Inspect `problem-map.md`.",
            "3. Review `evidence-list.md`.",
            "4. Follow `reproduce-steps.md`.",
            "5. Use `ai-task.md` only after evidence review.",
            "6. Validate fixes with `fix-verification-checklist.md`.",
            "",
            f"Summary: {event.summary}",
            "",
        ]
    )


def _bullet(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]


def _write_markdown(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
