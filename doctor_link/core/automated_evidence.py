from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from doctor_link.core.models import EvidenceItem, TimelineStep, utc_now_iso
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text, package_transaction


def record_automated_result(
    package_dir: Path,
    *,
    output_relative_path: str,
    output_payload: dict[str, Any],
    evidence_id: str,
    evidence_kind: str,
    evidence_title: str,
    evidence_source: str,
    action: str,
    target: str,
    status: str,
    expected: str | None,
    actual: str | None,
    explicit_assertion_ids: list[str] | None = None,
    assertion_statements: list[str] | None = None,
) -> str:
    """Persist one automated reproduction/test result as package evidence.

    The update is serialized across processes and the stable evidence/test IDs
    make reruns replace the previous result instead of appending stale copies.
    """
    package_dir = package_dir.resolve()
    with package_transaction(package_dir):
        assertion_ids = _resolve_assertion_ids(
            package_dir,
            explicit_assertion_ids or [],
            assertion_statements or [],
        )
        output_path = package_dir / output_relative_path
        output_payload = dict(output_payload)
        output_payload["related_assertion_ids"] = assertion_ids
        atomic_write_json(output_path, output_payload)

        evidence = EvidenceItem(
            evidence_id=evidence_id,
            kind=evidence_kind,
            title=evidence_title,
            source=evidence_source,
            path=output_relative_path,
            content=f"Status: {status}",
        )
        step = TimelineStep(
            step_id=evidence_id,
            order=_next_order(package_dir),
            action=action,
            target=target,
            expected_result=expected,
            actual_result=actual,
            status=status,
            evidence_ids=[evidence_id],
            is_failure_point=status not in {"passed", "manual"},
        )
        test_record = {
            "test_id": evidence_id,
            "name": evidence_title,
            "status": _test_status(status),
            "expected_behavior": expected,
            "actual_behavior": actual,
            "evidence_ids": [evidence_id],
            "related_assertion_ids": assertion_ids,
            "user_note": f"Recorded automatically by {evidence_source}.",
            "related_file": output_relative_path,
            "created_at": utc_now_iso(),
        }
        _update_report(package_dir, evidence, step, test_record)
        _replace_marked_block(
            package_dir / "evidence-list.md",
            evidence_id,
            "\n".join(
                [
                    f"## {evidence.title}",
                    "",
                    f"- ID: `{evidence.evidence_id}`",
                    f"- Kind: `{evidence.kind}`",
                    f"- Source: `{evidence.source}`",
                    f"- Path: `{evidence.path}`",
                    f"- Status: `{status}`",
                    f"- Assertions: {', '.join(assertion_ids) if assertion_ids else 'none'}",
                ]
            ),
        )
        _replace_marked_block(
            package_dir / "timeline.md",
            evidence_id,
            "\n".join(
                [
                    f"## Step {step.order}: {action}",
                    "",
                    f"- Operation: {action.replace('_', ' ').capitalize()} {target}",
                    f"- Target: `{target}`",
                    f"- Status: `{status}`",
                    f"- Expected: {expected or 'N/A'}",
                    f"- Actual: {actual or 'N/A'}",
                    f"- Evidence: `{evidence_id}`",
                ]
            ),
        )
    return evidence_id


def _resolve_assertion_ids(package_dir: Path, explicit_ids: list[str], statements: list[str]) -> list[str]:
    result = _dedupe(explicit_ids)
    path = package_dir / "user-assertions.json"
    if not path.exists() or not statements:
        return result
    try:
        assertions = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return result
    wanted = {_normalize(value) for value in statements if value.strip()}
    for item in assertions if isinstance(assertions, list) else []:
        if not isinstance(item, dict):
            continue
        statement = str(item.get("user_statement") or item.get("statement") or "")
        assertion_id = str(item.get("assertion_id") or item.get("id") or "")
        if assertion_id and _normalize(statement) in wanted and assertion_id not in result:
            result.append(assertion_id)
    return result


def _update_report(package_dir: Path, evidence: EvidenceItem, step: TimelineStep, test_record: dict[str, Any]) -> None:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    payload["evidence"] = [
        item for item in payload.get("evidence", []) if not isinstance(item, dict) or item.get("evidence_id") != evidence.evidence_id
    ]
    payload["evidence"].append(evidence.to_dict())
    payload["timeline"] = [
        item for item in payload.get("timeline", []) if not isinstance(item, dict) or item.get("step_id") != step.step_id
    ]
    payload["timeline"].append(step.to_dict())
    payload["test_records"] = [
        item for item in payload.get("test_records", []) if not isinstance(item, dict) or item.get("test_id") != test_record["test_id"]
    ]
    payload["test_records"].append(test_record)
    ai_task = payload.setdefault("ai_task", {})
    evidence_ids = ai_task.setdefault("evidence_ids", [])
    if evidence.evidence_id not in evidence_ids:
        evidence_ids.append(evidence.evidence_id)
    related = ai_task.setdefault("related_assertion_ids", [])
    for assertion_id in test_record["related_assertion_ids"]:
        if assertion_id not in related:
            related.append(assertion_id)
    atomic_write_json(path, payload)


def _replace_marked_block(path: Path, key: str, body: str) -> None:
    start = f"<!-- doctor-link:{key}:start -->"
    end = f"<!-- doctor-link:{key}:end -->"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    while start in current and end in current:
        prefix, remainder = current.split(start, 1)
        _, suffix = remainder.split(end, 1)
        current = prefix.rstrip() + "\n" + suffix.lstrip()
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    atomic_write_text(path, current.rstrip() + "\n\n" + block)


def _next_order(package_dir: Path) -> int:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return 1
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 1
    orders = [item.get("order") for item in payload.get("timeline", []) if isinstance(item, dict)]
    return max((item for item in orders if isinstance(item, int)), default=0) + 1


def _test_status(status: str) -> str:
    return status if status in {"passed", "failed", "partial", "unknown"} else "unknown"


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in result:
            result.append(normalized)
    return result
