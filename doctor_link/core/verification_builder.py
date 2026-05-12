from __future__ import annotations

from doctor_link.core.models import DiagnosticEvent, VerificationChecklist


def build_verification_checklist(event: DiagnosticEvent) -> VerificationChecklist:
    """Build a verification checklist from evidence, assertions, and AI task scope."""
    items: list[str] = []

    items.append("Reproduce the original issue before applying any fix.")
    items.append("Apply the smallest possible code change within the investigation boundary.")

    for assertion in event.user_assertions:
        items.append(f"Confirm the human-confirmed issue is resolved: {assertion.user_statement}")

    for step in event.ai_task.verification_steps:
        if step not in items:
            items.append(step)

    if event.evidence:
        items.append("Regenerate the Doctor link diagnostic package after the fix.")
        items.append("Compare before and after doctor-report.json files.")

    if not items:
        items.append("No verification steps were generated. Add project-specific verification rules.")

    return VerificationChecklist(
        title="Fix Verification Checklist",
        items=items,
        status="draft",
    )


def render_verification_checklist(checklist: VerificationChecklist) -> str:
    lines = [f"# {checklist.title}", ""]
    for item in checklist.items:
        lines.append(f"- [ ] {item}")
    lines.append("")
    return "\n".join(lines)
