from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import EvidenceItem, TimelineStep, utc_now_iso


@dataclass
class ReportComparison:
    """Structured comparison between before and after diagnostic reports."""

    before_report: str
    after_report: str
    compared_at: str = field(default_factory=utc_now_iso)
    status: str = "unknown"
    summary: str = ""
    resolved_user_assertions: list[str] = field(default_factory=list)
    remaining_user_assertions: list[str] = field(default_factory=list)
    new_user_assertions: list[str] = field(default_factory=list)
    evidence_delta: int = 0
    timeline_delta: int = 0
    test_record_delta: int = 0
    before_category: str | None = None
    after_category: str | None = None
    before_status: str | None = None
    after_status: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link Report Comparison",
            "",
            f"- Before report: `{self.before_report}`",
            f"- After report: `{self.after_report}`",
            f"- Compared at: `{self.compared_at}`",
            f"- Status: `{self.status}`",
            "",
            "## Summary",
            self.summary or "No summary generated.",
            "",
            "## User assertions",
            "",
            "### Resolved",
            *_list(self.resolved_user_assertions),
            "",
            "### Remaining",
            *_list(self.remaining_user_assertions),
            "",
            "### New",
            *_list(self.new_user_assertions),
            "",
            "## Evidence and timeline delta",
            "",
            f"- Evidence delta: `{self.evidence_delta}`",
            f"- Timeline delta: `{self.timeline_delta}`",
            f"- Test record delta: `{self.test_record_delta}`",
            "",
            "## Report status",
            "",
            f"- Before category: `{self.before_category or 'N/A'}`",
            f"- After category: `{self.after_category or 'N/A'}`",
            f"- Before status: `{self.before_status or 'N/A'}`",
            f"- After status: `{self.after_status or 'N/A'}`",
            "",
            "## Notes",
            *_list(self.notes),
            "",
        ]
        return "\n".join(lines)


def compare_doctor_reports(before_report: Path, after_report: Path) -> ReportComparison:
    """Compare two doctor-report.json files without guessing fix success.

    The comparison is evidence-oriented: it highlights changed assertions,
    timeline/evidence growth, and status/category changes. It does not declare a
    fix successful unless all human-confirmed assertions from the before report
    are absent from the after report.
    """
    before = _read_report(before_report)
    after = _read_report(after_report)

    before_assertions = _assertion_statements(before)
    after_assertions = _assertion_statements(after)

    resolved = sorted(before_assertions - after_assertions)
    remaining = sorted(before_assertions & after_assertions)
    new = sorted(after_assertions - before_assertions)

    evidence_delta = len(after.get("evidence", []) or []) - len(before.get("evidence", []) or [])
    timeline_delta = len(after.get("timeline", []) or []) - len(before.get("timeline", []) or [])
    test_record_delta = len(after.get("test_records", []) or []) - len(before.get("test_records", []) or [])

    notes: list[str] = []
    if remaining:
        notes.append("Some human-confirmed assertions remain in the after report. Do not mark the fix as verified.")
    if new:
        notes.append("The after report contains new human-confirmed assertions that require review.")
    if evidence_delta <= 0:
        notes.append("No additional evidence was added after the fix. Verification may be incomplete.")
    if test_record_delta <= 0:
        notes.append("No additional test records were added after the fix. Rerun relevant tests before closing.")

    if remaining or new:
        status = "not_verified"
    elif before_assertions and not remaining:
        status = "candidate_verified"
        notes.append("All before-report user assertions are absent from the after report; confirm with recorded test evidence.")
    else:
        status = "needs_review"
        notes.append("No before-report user assertions were found; compare evidence and tests manually.")

    summary = _build_summary(resolved, remaining, new, evidence_delta, test_record_delta)

    return ReportComparison(
        before_report=str(before_report),
        after_report=str(after_report),
        status=status,
        summary=summary,
        resolved_user_assertions=resolved,
        remaining_user_assertions=remaining,
        new_user_assertions=new,
        evidence_delta=evidence_delta,
        timeline_delta=timeline_delta,
        test_record_delta=test_record_delta,
        before_category=before.get("category"),
        after_category=after.get("category"),
        before_status=before.get("status"),
        after_status=after.get("status"),
        notes=notes,
    )


def write_report_comparison(before_report: Path, after_report: Path, output_dir: Path) -> ReportComparison:
    """Compare two reports and write Markdown plus JSON outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    comparison = compare_doctor_reports(before_report, after_report)
    (output_dir / "report-comparison.json").write_text(
        json.dumps(comparison.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "report-comparison.md").write_text(comparison.to_markdown(), encoding="utf-8")
    return comparison


def write_report_comparison_to_package(before_report: Path, after_package_dir: Path) -> EvidenceItem:
    """Compare a before report with an after package and write verification evidence into the after package."""
    after_package_dir = after_package_dir.resolve()
    if not after_package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {after_package_dir}")
    after_report = after_package_dir / "doctor-report.json"
    comparison = compare_doctor_reports(before_report, after_report)

    evidence_dir = after_package_dir / "evidence" / "test-results"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / "report-comparison.json"
    md_path = evidence_dir / "report-comparison.md"
    json_path.write_text(json.dumps(comparison.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(comparison.to_markdown(), encoding="utf-8")

    evidence = EvidenceItem(
        kind="report_comparison",
        title="Before/after diagnostic report comparison",
        source="doctor-link compare",
        path=str(json_path.relative_to(after_package_dir)),
        content=f"Verification status: {comparison.status}\n{comparison.summary}",
    )
    step = TimelineStep(
        order=_next_order(after_package_dir),
        action="compare_doctor_reports",
        target=str(before_report),
        expected_result="After report should contain evidence that the original human-confirmed issue is resolved.",
        actual_result=f"{comparison.status}: {comparison.summary}",
        status="passed" if comparison.status == "candidate_verified" else "failed",
        evidence_ids=[evidence.evidence_id],
        is_failure_point=comparison.status != "candidate_verified",
        user_note="Comparison status is evidence for verification, not a standalone proof of production readiness.",
    )

    _update_after_package(after_package_dir, comparison, evidence, step)
    _append_evidence_markdown(after_package_dir, evidence, md_path.relative_to(after_package_dir))
    _append_timeline_markdown(after_package_dir, step)
    _append_ai_task(after_package_dir, comparison, evidence)
    _append_summary(after_package_dir, comparison)
    return evidence


def _read_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"doctor-report.json not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"doctor-report.json must contain a JSON object: {path}")
    return payload


def _assertion_statements(report: dict[str, Any]) -> set[str]:
    assertions = report.get("user_assertions") or []
    statements: set[str] = set()
    for item in assertions:
        if isinstance(item, dict) and item.get("user_statement"):
            statements.add(str(item["user_statement"]))
    return statements


def _update_after_package(
    after_package_dir: Path,
    comparison: ReportComparison,
    evidence: EvidenceItem,
    step: TimelineStep,
) -> None:
    path = after_package_dir / "doctor-report.json"
    payload = _read_report(path)
    payload["report_comparison"] = comparison.to_dict()
    payload.setdefault("evidence", []).append(evidence.to_dict())
    payload.setdefault("timeline", []).append(step.to_dict())
    ai_task = payload.setdefault("ai_task", {})
    ai_task.setdefault("evidence_ids", []).append(evidence.evidence_id)
    if comparison.status != "candidate_verified":
        ai_task.setdefault("requested_work", []).append(
            "Review report comparison evidence before marking the fix as verified."
        )
    ai_task.setdefault("verification_steps", []).append(
        "Review `evidence/test-results/report-comparison.md` and confirm verification status is acceptable."
    )
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_evidence_markdown(after_package_dir: Path, evidence: EvidenceItem, markdown_path: Path) -> None:
    _append(
        after_package_dir / "evidence-list.md",
        "\n".join(
            [
                f"\n## {evidence.title}",
                "",
                f"- ID: `{evidence.evidence_id}`",
                f"- Kind: `{evidence.kind}`",
                f"- Source: `{evidence.source}`",
                f"- JSON Path: `{evidence.path}`",
                f"- Markdown Path: `{markdown_path}`",
                "",
                evidence.content or "No content preview.",
                "",
            ]
        ),
    )


def _append_timeline_markdown(after_package_dir: Path, step: TimelineStep) -> None:
    marker = " **Failure point**" if step.is_failure_point else ""
    _append(
        after_package_dir / "timeline.md",
        "\n".join(
            [
                f"\n## Step {step.order}: {step.action}{marker}",
                "",
                f"- Time: `{step.timestamp}`",
                f"- Target: `{step.target or 'N/A'}`",
                f"- Status: `{step.status}`",
                f"- Expected: {step.expected_result or 'N/A'}",
                f"- Actual: {step.actual_result or 'N/A'}",
                f"- Evidence: {', '.join(step.evidence_ids)}",
                f"- User note: {step.user_note or 'N/A'}",
                "",
            ]
        ),
    )


def _append_ai_task(after_package_dir: Path, comparison: ReportComparison, evidence: EvidenceItem) -> None:
    lines = [
        "\n## Report comparison verification evidence",
        "",
        f"- Verification status: `{comparison.status}`",
        f"- Evidence: `{evidence.evidence_id}`",
        f"- Summary: {comparison.summary}",
        "- Boundary: Do not claim the fix is verified unless comparison status and test evidence support it.",
    ]
    if comparison.status != "candidate_verified":
        lines.append("- Instruction: Continue investigation or add missing verification evidence before closing.")
    _append(after_package_dir / "ai-task.md", "\n".join(lines) + "\n")


def _append_summary(after_package_dir: Path, comparison: ReportComparison) -> None:
    _append(
        after_package_dir / "summary.md",
        f"\n## Report comparison verification\n\n- Status: `{comparison.status}`\n- Summary: {comparison.summary}\n",
    )


def _next_order(package_dir: Path) -> int:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return 1
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 1
    orders = [item.get("order") for item in payload.get("timeline", []) if isinstance(item, dict)]
    numeric_orders = [item for item in orders if isinstance(item, int)]
    return max(numeric_orders, default=0) + 1


def _build_summary(
    resolved: list[str],
    remaining: list[str],
    new: list[str],
    evidence_delta: int,
    test_record_delta: int,
) -> str:
    parts = [
        f"Resolved assertions: {len(resolved)}.",
        f"Remaining assertions: {len(remaining)}.",
        f"New assertions: {len(new)}.",
        f"Evidence delta: {evidence_delta}.",
        f"Test record delta: {test_record_delta}.",
    ]
    return " ".join(parts)


def _append(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(current.rstrip() + "\n" + text.lstrip("\n"), encoding="utf-8")


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]
