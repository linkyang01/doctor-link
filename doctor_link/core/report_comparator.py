from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import EvidenceItem, TimelineStep, utc_now_iso
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text, package_transaction


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
    fix successful unless every human-confirmed assertion from the before
    report has linked, passing after-state test evidence.
    """
    before = _read_report(before_report)
    after = _read_report(after_report)

    before_assertions = _assertion_refs(before)
    after_assertions = _assertion_refs(after)
    after_tests = [item for item in after.get("test_records", []) or [] if isinstance(item, dict)]

    resolved, remaining = _classify_before_assertions(before_assertions, after_assertions, after_tests)
    before_statements = {item[1] for item in before_assertions}
    new = sorted({item[1] for item in after_assertions if item[1] not in before_statements})

    evidence_delta = len(after.get("evidence", []) or []) - len(before.get("evidence", []) or [])
    timeline_delta = len(after.get("timeline", []) or []) - len(before.get("timeline", []) or [])
    test_record_delta = len(after.get("test_records", []) or []) - len(before.get("test_records", []) or [])

    notes: list[str] = []
    if remaining:
        notes.append("Some human-confirmed assertions remain in the after report. Do not mark the fix as verified.")
    if new:
        notes.append("The after report contains new human-confirmed assertions that require review.")
    blocking_tests = [item for item in after_tests if str(item.get("status") or "unknown") != "passed"]
    if evidence_delta <= 0:
        notes.append("No additional evidence was added after the fix. Verification may be incomplete.")
    if not after_tests:
        notes.append("No after-state test records were recorded. Rerun relevant tests before closing.")
    if blocking_tests:
        names = ", ".join(str(item.get("name") or item.get("test_id") or "unknown") for item in blocking_tests)
        notes.append(f"After-state tests are not passing: {names}.")

    if remaining or new or blocking_tests:
        status = "not_verified"
    elif before_assertions and resolved and after_tests:
        status = "candidate_verified"
        notes.append("All before-report user assertions have linked passing after-state test evidence; human review is still required.")
    else:
        status = "needs_review"
        notes.append("The available after-state evidence is not sufficient to classify the fix as a verified candidate.")

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
    atomic_write_json(output_dir / "report-comparison.json", comparison.to_dict())
    atomic_write_text(output_dir / "report-comparison.md", comparison.to_markdown())
    return comparison


def write_report_comparison_to_package(before_report: Path, after_package_dir: Path) -> EvidenceItem:
    """Compare a before report with an after package and write verification evidence into the after package."""
    after_package_dir = after_package_dir.resolve()
    if not after_package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {after_package_dir}")
    with package_transaction(after_package_dir):
        after_report = after_package_dir / "doctor-report.json"
        comparison = compare_doctor_reports(before_report, after_report)

        evidence_dir = after_package_dir / "evidence" / "test-results"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        json_path = evidence_dir / "report-comparison.json"
        md_path = evidence_dir / "report-comparison.md"
        atomic_write_json(json_path, comparison.to_dict())
        atomic_write_text(md_path, comparison.to_markdown())

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
            expected_result="After report should contain linked passing evidence for every original assertion.",
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


def _assertion_refs(report: dict[str, Any]) -> list[tuple[str, str]]:
    assertions = report.get("user_assertions") or []
    refs: list[tuple[str, str]] = []
    for index, item in enumerate(assertions, start=1):
        if isinstance(item, dict) and item.get("user_statement"):
            assertion_id = str(item.get("assertion_id") or item.get("id") or f"assertion-{index}")
            refs.append((assertion_id, str(item["user_statement"])))
    return refs


def _classify_before_assertions(
    before_assertions: list[tuple[str, str]],
    after_assertions: list[tuple[str, str]],
    after_tests: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    after_ids_by_statement: dict[str, set[str]] = {}
    for assertion_id, statement in after_assertions:
        after_ids_by_statement.setdefault(statement, set()).add(assertion_id)
    resolved: list[str] = []
    remaining: list[str] = []
    for before_id, statement in before_assertions:
        candidate_ids = {before_id, *after_ids_by_statement.get(statement, set())}
        linked = [item for item in after_tests if candidate_ids.intersection(_related_assertion_ids(item))]
        has_passing = any(str(item.get("status") or "unknown") == "passed" for item in linked)
        has_blocking = any(str(item.get("status") or "unknown") != "passed" for item in linked)
        if has_passing and not has_blocking:
            resolved.append(statement)
        else:
            remaining.append(statement)
    return sorted(resolved), sorted(remaining)


def _related_assertion_ids(record: dict[str, Any]) -> set[str]:
    related = record.get("related_assertion_ids") or []
    if isinstance(related, str):
        related = [related]
    return {str(item) for item in related} if isinstance(related, list) else set()


def _update_after_package(
    after_package_dir: Path,
    comparison: ReportComparison,
    evidence: EvidenceItem,
    step: TimelineStep,
) -> None:
    path = after_package_dir / "doctor-report.json"
    payload = _read_report(path)
    old_comparison_ids = {
        str(item.get("evidence_id"))
        for item in payload.get("evidence", [])
        if isinstance(item, dict) and item.get("kind") == "report_comparison" and item.get("evidence_id")
    }
    payload["report_comparison"] = comparison.to_dict()
    payload["evidence"] = [
        item for item in payload.get("evidence", []) if not isinstance(item, dict) or item.get("kind") != "report_comparison"
    ]
    payload["evidence"].append(evidence.to_dict())
    payload["timeline"] = [
        item for item in payload.get("timeline", []) if not isinstance(item, dict) or item.get("action") != "compare_doctor_reports"
    ]
    payload["timeline"].append(step.to_dict())
    ai_task = payload.setdefault("ai_task", {})
    ai_task["evidence_ids"] = [
        item for item in ai_task.get("evidence_ids", []) if str(item) not in old_comparison_ids
    ]
    ai_task["evidence_ids"].append(evidence.evidence_id)
    requested_work = [
        item
        for item in ai_task.get("requested_work", [])
        if item != "Review report comparison evidence before marking the fix as verified."
    ]
    if comparison.status != "candidate_verified":
        requested_work.append("Review report comparison evidence before marking the fix as verified.")
    ai_task["requested_work"] = _dedupe(requested_work)
    verification_step = "Review `evidence/test-results/report-comparison.md` and confirm verification status is acceptable."
    ai_task["verification_steps"] = _dedupe([*ai_task.get("verification_steps", []), verification_step])
    atomic_write_json(path, payload)


def _append_evidence_markdown(after_package_dir: Path, evidence: EvidenceItem, markdown_path: Path) -> None:
    _replace_heading_section(
        after_package_dir / "evidence-list.md",
        "## Before/after diagnostic report comparison",
        "\n".join(
            [
                f"## {evidence.title}",
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
        "## Report comparison verification evidence",
        "",
        f"- Verification status: `{comparison.status}`",
        f"- Evidence: `{evidence.evidence_id}`",
        f"- Summary: {comparison.summary}",
        "- Boundary: Do not claim the fix is verified unless comparison status and test evidence support it.",
    ]
    if comparison.status != "candidate_verified":
        lines.append("- Instruction: Continue investigation or add missing verification evidence before closing.")
    _replace_heading_section(
        after_package_dir / "ai-task.md",
        "## Report comparison verification evidence",
        "\n".join(lines) + "\n",
    )


def _append_summary(after_package_dir: Path, comparison: ReportComparison) -> None:
    _replace_heading_section(
        after_package_dir / "summary.md",
        "## Report comparison verification",
        f"## Report comparison verification\n\n- Status: `{comparison.status}`\n- Summary: {comparison.summary}\n",
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
    atomic_write_text(path, current.rstrip() + "\n" + text.lstrip("\n"))


def _replace_heading_section(path: Path, heading: str, replacement: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = current.splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        if line.strip() == heading:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept.append(line)
    prefix = "\n".join(kept).rstrip()
    atomic_write_text(path, prefix + "\n\n" + replacement.strip() + "\n")


def _dedupe(values: list[Any]) -> list[Any]:
    result: list[Any] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]
