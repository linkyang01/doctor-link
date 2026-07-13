from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import EvidenceItem, TimelineStep, new_id, utc_now_iso
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text, package_transaction

VALID_STATUSES = {"passed", "failed", "partial", "unknown"}


@dataclass
class TestRecord:
    """Structured evidence for one diagnostic test result."""

    test_id: str = field(default_factory=lambda: new_id("test"))
    name: str = "Diagnostic test"
    status: str = "unknown"
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    evidence_ids: list[str] = field(default_factory=list)
    related_assertion_ids: list[str] = field(default_factory=list)
    user_note: str | None = None
    related_file: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_test_record(
    name: str,
    status: str = "unknown",
    expected_behavior: str | None = None,
    actual_behavior: str | None = None,
    evidence_ids: list[str] | None = None,
    related_assertion_ids: list[str] | None = None,
    user_note: str | None = None,
    related_file: str | None = None,
) -> TestRecord:
    normalized = status.lower().strip()
    if normalized not in VALID_STATUSES:
        raise ValueError("status must be one of: passed, failed, partial, unknown")
    return TestRecord(
        name=name,
        status=normalized,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        evidence_ids=evidence_ids or [],
        related_assertion_ids=_dedupe(related_assertion_ids or []),
        user_note=user_note,
        related_file=related_file,
    )


def record_test_result(
    package_dir: Path,
    name: str,
    status: str = "unknown",
    expected_behavior: str | None = None,
    actual_behavior: str | None = None,
    evidence_ids: list[str] | None = None,
    related_assertion_ids: list[str] | None = None,
    user_note: str | None = None,
    related_file: str | None = None,
) -> TestRecord:
    """Write a test result into an existing diagnostic package."""
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    record = create_test_record(
        name=name,
        status=status,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        evidence_ids=evidence_ids,
        related_assertion_ids=related_assertion_ids,
        user_note=user_note,
        related_file=related_file,
    )

    with package_transaction(package_dir):
        _record_test_result_locked(package_dir, record)
    return record


def _record_test_result_locked(package_dir: Path, record: TestRecord) -> None:
    results_dir = package_dir / "evidence" / "test-results"
    results_dir.mkdir(parents=True, exist_ok=True)
    result_path = results_dir / f"{record.test_id}.json"
    atomic_write_json(result_path, record.to_dict())

    evidence = EvidenceItem(
        kind="test_result",
        title=f"Test result: {record.name}",
        source="doctor-link record",
        path=str(result_path.relative_to(package_dir)),
        content=_record_summary(record),
    )
    step = TimelineStep(
        order=_next_order(package_dir),
        action="record_test_result",
        target=record.related_file or record.name,
        expected_result=record.expected_behavior,
        actual_result=record.actual_behavior,
        status=record.status,
        evidence_ids=[evidence.evidence_id, *record.evidence_ids],
        is_failure_point=record.status in {"failed", "partial"},
        user_note=_timeline_note(record),
    )

    _update_report_json(package_dir, record, evidence, step)
    _append_evidence_markdown(package_dir, evidence)
    _append_timeline_markdown(package_dir, step)
    _append_ai_task(package_dir, record, evidence)
    _append_summary(package_dir, record)


def _update_report_json(package_dir: Path, record: TestRecord, evidence: EvidenceItem, step: TimelineStep) -> None:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    payload.setdefault("test_records", []).append(record.to_dict())
    payload.setdefault("evidence", []).append(evidence.to_dict())
    payload.setdefault("timeline", []).append(step.to_dict())
    ai_task = payload.setdefault("ai_task", {})
    ai_task.setdefault("evidence_ids", []).append(evidence.evidence_id)
    if record.related_assertion_ids:
        existing = ai_task.setdefault("related_assertion_ids", [])
        for assertion_id in record.related_assertion_ids:
            if assertion_id not in existing:
                existing.append(assertion_id)
    if record.status in {"failed", "partial"}:
        suffix = f" Related assertions: {_assertion_text(record)}." if record.related_assertion_ids else ""
        ai_task.setdefault("requested_work", []).append(
            f"Investigate `{record.name}` using evidence `{evidence.evidence_id}`.{suffix}"
        )
        ai_task.setdefault("verification_steps", []).append(
            f"Rerun `{record.name}` and confirm the result is passed."
        )
    atomic_write_json(path, payload)


def _append_evidence_markdown(package_dir: Path, evidence: EvidenceItem) -> None:
    _append(
        package_dir / "evidence-list.md",
        f"\n## {evidence.title}\n\n- ID: `{evidence.evidence_id}`\n- Kind: `{evidence.kind}`\n- Source: `{evidence.source}`\n- Path: `{evidence.path}`\n\n{evidence.content}\n",
    )


def _append_timeline_markdown(package_dir: Path, step: TimelineStep) -> None:
    marker = " **Failure point**" if step.is_failure_point else ""
    _append(
        package_dir / "timeline.md",
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


def _append_ai_task(package_dir: Path, record: TestRecord, evidence: EvidenceItem) -> None:
    _append(
        package_dir / "ai-task.md",
        "\n".join(
            [
                "\n## Recorded test result evidence",
                "",
                f"- Test: {record.name}",
                f"- Status: `{record.status}`",
                f"- Evidence: `{evidence.evidence_id}`",
                f"- Related user assertions: {_assertion_markdown(record)}",
                f"- Expected: {record.expected_behavior or 'N/A'}",
                f"- Actual: {record.actual_behavior or 'N/A'}",
                "- Instruction: Treat this as diagnostic evidence and verify the fix by rerunning the same test.",
                "",
            ]
        ),
    )


def _append_summary(package_dir: Path, record: TestRecord) -> None:
    _append(
        package_dir / "summary.md",
        f"\n## Test result recorded\n\n- Test: {record.name}\n- Status: `{record.status}`\n- Related user assertions: {_assertion_markdown(record)}\n- Expected: {record.expected_behavior or 'N/A'}\n- Actual: {record.actual_behavior or 'N/A'}\n",
    )


def _record_summary(record: TestRecord) -> str:
    return "\n".join(
        [
            f"Test: {record.name}",
            f"Status: {record.status}",
            f"Related user assertions: {_assertion_text(record)}",
            f"Expected: {record.expected_behavior or 'N/A'}",
            f"Actual: {record.actual_behavior or 'N/A'}",
            f"Related file: {record.related_file or 'N/A'}",
            f"User note: {record.user_note or 'N/A'}",
        ]
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
    orders = [item for item in orders if isinstance(item, int)]
    return max(orders, default=0) + 1


def _append(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    atomic_write_text(path, current.rstrip() + "\n" + text.lstrip("\n"))


def _json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def _assertion_text(record: TestRecord) -> str:
    return ", ".join(record.related_assertion_ids) if record.related_assertion_ids else "N/A"


def _assertion_markdown(record: TestRecord) -> str:
    if not record.related_assertion_ids:
        return "N/A"
    return ", ".join(f"`{item}`" for item in record.related_assertion_ids)


def _timeline_note(record: TestRecord) -> str | None:
    if not record.related_assertion_ids:
        return record.user_note
    note = f"Related user assertions: {_assertion_text(record)}"
    return f"{record.user_note} | {note}" if record.user_note else note
