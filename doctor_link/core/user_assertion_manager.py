from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.models import UserAssertion
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text, package_transaction


def add_user_assertion(
    package_dir: Path,
    user_statement: str,
    expected_behavior: str | None = None,
    actual_behavior: str | None = None,
    why_user_thinks_it_is_wrong: str | None = None,
    severity: str = "error",
    related_file: str | None = None,
    next_ai_instruction: str | None = None,
    related_evidence_ids: list[str] | None = None,
) -> UserAssertion:
    """Add a human-confirmed problem to an existing diagnostic package."""
    package_dir = package_dir.resolve()
    if not package_dir.exists() or not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    report_id = _read_report_id(package_dir)
    assertion = UserAssertion(
        report_id=report_id,
        severity=severity,
        user_statement=user_statement,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        why_user_thinks_it_is_wrong=why_user_thinks_it_is_wrong,
        related_file=related_file,
        related_evidence_ids=related_evidence_ids or [],
        ai_disagreed_or_missed=True,
        next_ai_instruction=next_ai_instruction,
    )

    with package_transaction(package_dir):
        assertions_path = package_dir / "user-assertions.json"
        assertions = _read_json_list(assertions_path)
        assertions.append(assertion.to_dict())
        atomic_write_json(assertions_path, assertions)

        _update_doctor_report_json(package_dir, assertion)
        _append_problem_map(package_dir, assertion)
        _append_ai_task(package_dir, assertion)
        _append_summary(package_dir, assertion)

    return assertion


def _read_report_id(package_dir: Path) -> str | None:
    report_path = package_dir / "doctor-report.json"
    if not report_path.exists():
        return None
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload.get("event_id")


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def _update_doctor_report_json(package_dir: Path, assertion: UserAssertion) -> None:
    report_path = package_dir / "doctor-report.json"
    if not report_path.exists():
        return
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    user_assertions = payload.setdefault("user_assertions", [])
    user_assertions.append(assertion.to_dict())
    problem_map = payload.setdefault("problem_map", {})
    problem_map["human_confirmed_problem"] = assertion.user_statement
    atomic_write_json(report_path, payload)


def _append_problem_map(package_dir: Path, assertion: UserAssertion) -> None:
    path = package_dir / "problem-map.md"
    text = _append_block(
        title="Human-confirmed issue",
        lines=[
            f"Statement: {assertion.user_statement}",
            f"Expected: {assertion.expected_behavior or 'N/A'}",
            f"Actual: {assertion.actual_behavior or 'N/A'}",
            f"Why wrong: {assertion.why_user_thinks_it_is_wrong or 'N/A'}",
        ],
    )
    _append_text(path, text)


def _append_ai_task(package_dir: Path, assertion: UserAssertion) -> None:
    path = package_dir / "ai-task.md"
    text = _append_block(
        title="Human-confirmed issue override",
        lines=[
            "The human user has confirmed this as the problem. Do not dismiss it as normal behavior without evidence.",
            f"Statement: {assertion.user_statement}",
            f"Expected: {assertion.expected_behavior or 'N/A'}",
            f"Actual: {assertion.actual_behavior or 'N/A'}",
            f"Why wrong: {assertion.why_user_thinks_it_is_wrong or 'N/A'}",
            f"Next AI instruction: {assertion.next_ai_instruction or 'Use this assertion as the primary diagnosis target.'}",
        ],
    )
    _append_text(path, text)


def _append_summary(package_dir: Path, assertion: UserAssertion) -> None:
    path = package_dir / "summary.md"
    text = _append_block(
        title="User assertion added",
        lines=[assertion.user_statement],
    )
    _append_text(path, text)


def _append_block(title: str, lines: list[str]) -> str:
    body = "\n".join(f"- {line}" for line in lines)
    return f"\n\n## {title}\n\n{body}\n"


def _append_text(path: Path, text: str) -> None:
    if path.exists():
        current = path.read_text(encoding="utf-8")
    else:
        current = ""
    atomic_write_text(path, current.rstrip() + text)
