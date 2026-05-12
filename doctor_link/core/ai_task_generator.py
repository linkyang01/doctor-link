from __future__ import annotations

from pathlib import Path

from doctor_link.core.models import ScanResult, TestPlan


def generate_ai_task(scan_result: ScanResult, test_plan: TestPlan, output: Path) -> Path:
    """Generate an AI-ready debugging task draft."""
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

    lines.extend([
        "",
        "## Requested work",
        "",
        "1. Review the diagnostic report and JSON data.",
        "2. Identify what information is missing for reliable diagnosis.",
        "3. Propose the next test steps.",
        "4. Do not guess root causes without evidence.",
        "5. If code changes are needed, make the smallest possible change and add verification steps.",
        "",
        "## Verification checklist",
        "",
        "- Confirm the issue is reproducible.",
        "- Confirm the failing category is covered by a test sample.",
        "- Confirm the fix changes the failing result.",
        "- Update Doctor link reports after the fix.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
