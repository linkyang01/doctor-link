from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.web_package_reader import DiagnosticPackageView


@dataclass
class EvidenceReferenceSummary:
    evidence_path: str
    evidence_ids: list[str] = field(default_factory=list)
    timeline_refs: list[str] = field(default_factory=list)
    assertion_refs: list[str] = field(default_factory=list)
    test_record_refs: list[str] = field(default_factory=list)
    verification_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def total_refs(self) -> int:
        return len(self.timeline_refs) + len(self.assertion_refs) + len(self.test_record_refs) + len(self.verification_refs)


def build_evidence_reference_summaries(view: DiagnosticPackageView) -> dict[str, EvidenceReferenceSummary]:
    """Build reverse references for evidence cards.

    The function is read-only and best-effort. It searches structured package
    sections for evidence IDs, evidence paths, and file names.
    """
    report = _dict(view.json_data("doctor_report"))
    verification = _dict(view.json_data("verification_result"))
    assertions = _list(view.json_data("user_assertions"))
    timeline = _list(report.get("timeline"))
    test_records = _list(report.get("test_records"))

    result: dict[str, EvidenceReferenceSummary] = {}
    for preview in view.evidence_previews:
        tokens = _tokens_for_evidence(preview.path, preview.evidence_ids)
        summary = EvidenceReferenceSummary(evidence_path=preview.path, evidence_ids=list(preview.evidence_ids))
        for index, item in enumerate(timeline, start=1):
            if _contains_any(item, tokens):
                summary.timeline_refs.append(_label(item, index, "timeline"))
        for index, item in enumerate(assertions, start=1):
            if _contains_any(item, tokens):
                summary.assertion_refs.append(_label(item, index, "assertion"))
        for index, item in enumerate(test_records, start=1):
            if _contains_any(item, tokens):
                summary.test_record_refs.append(_label(item, index, "test"))
        if _contains_any(verification, tokens):
            summary.verification_refs.append("verification-result")
        result[preview.path] = summary
    return result


def verification_status_reasons(view: DiagnosticPackageView) -> list[str]:
    result = _dict(view.json_data("verification_result"))
    report = _dict(view.json_data("doctor_report"))
    status = str(result.get("status") or "missing")
    missing = _list(result.get("missing_evidence"))
    tests = _list(result.get("tests_to_rerun"))
    comparison = result.get("report_comparison_status") or _nested(report, ["verification_result", "report_comparison_status"])
    vly = result.get("vly_core_proof_status") or _nested(report, ["verification_result", "vly_core_proof_status"])
    coverage = _list(result.get("assertion_test_coverage") or _nested(report, ["verification_result", "assertion_test_coverage"]))

    reasons: list[str] = []
    if status == "missing":
        reasons.append("No verification-result.json is available yet.")
    if missing:
        reasons.append(f"Verification is blocked by {len(missing)} missing evidence item(s).")
    if tests:
        reasons.append(f"{len(tests)} test or verification action(s) should be rerun.")
    if comparison:
        reasons.append(f"Report comparison status is {comparison}.")
    if vly:
        reasons.append(f"Vly Core Proof status is {vly}.")
    missing_coverage = [item for item in coverage if isinstance(item, dict) and item.get("status") != "covered"]
    if missing_coverage:
        reasons.append(f"{len(missing_coverage)} user assertion(s) still need linked test coverage.")
    if not reasons:
        reasons.append("No structured verification blocker was found. Review the checklist and test records before closing.")
    return reasons


def test_record_status_map(view: DiagnosticPackageView) -> dict[str, str]:
    report = _dict(view.json_data("doctor_report"))
    records = _list(report.get("test_records"))
    result: dict[str, str] = {}
    for item in records:
        if not isinstance(item, dict):
            continue
        test_id = str(item.get("test_id") or item.get("id") or item.get("name") or "")
        if test_id:
            result[test_id] = str(item.get("status") or "unknown")
    return result


def _tokens_for_evidence(path: str, ids: list[str]) -> list[str]:
    tokens = [path, Path(path).name, *ids]
    return [token for token in tokens if token]


def _contains_any(value: Any, tokens: list[str]) -> bool:
    text = json.dumps(value, ensure_ascii=False, default=str) if not isinstance(value, str) else value
    return any(token in text for token in tokens)


def _label(value: Any, index: int, prefix: str) -> str:
    if isinstance(value, dict):
        for key in ["title", "name", "action", "user_statement", "statement", "test_id", "id"]:
            if value.get(key):
                return f"{prefix}-{index}: {value[key]}"
    return f"{prefix}-{index}"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nested(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
