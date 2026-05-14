from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso


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


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]
