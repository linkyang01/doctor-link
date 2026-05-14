from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WebComparisonView:
    exists: bool
    json_path: str = ""
    markdown_path: str = ""
    status: str = "missing"
    summary: str = ""
    before_report: str = ""
    after_report: str = ""
    resolved_signals: list[str] = field(default_factory=list)
    unresolved_signals: list[str] = field(default_factory=list)
    new_signals: list[str] = field(default_factory=list)
    changed_signals: list[str] = field(default_factory=list)
    evidence_delta: int | None = None
    timeline_delta: int | None = None
    test_record_delta: int | None = None
    notes: list[str] = field(default_factory=list)
    markdown: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def read_web_comparison(package_dir: Path) -> WebComparisonView:
    package_dir = package_dir.resolve()
    json_path = _find_first(package_dir, ["report-comparison.json", "evidence/test-results/report-comparison.json"])
    md_path = _find_first(package_dir, ["report-comparison.md", "evidence/test-results/report-comparison.md"])
    markdown = md_path.read_text(encoding="utf-8", errors="replace") if md_path else ""

    if not json_path and not md_path:
        return WebComparisonView(exists=False)
    if not json_path:
        return WebComparisonView(
            exists=True,
            markdown_path=_relative(package_dir, md_path),
            status="present_without_json",
            markdown=markdown,
            error="Comparison Markdown exists but comparison JSON is missing.",
        )

    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return WebComparisonView(
            exists=True,
            json_path=_relative(package_dir, json_path),
            markdown_path=_relative(package_dir, md_path),
            status="invalid_json",
            markdown=markdown,
            error=str(exc),
        )

    if not isinstance(payload, dict):
        return WebComparisonView(
            exists=True,
            json_path=_relative(package_dir, json_path),
            markdown_path=_relative(package_dir, md_path),
            status="invalid_json",
            markdown=markdown,
            error="Comparison JSON must be an object.",
        )

    return WebComparisonView(
        exists=True,
        json_path=_relative(package_dir, json_path),
        markdown_path=_relative(package_dir, md_path),
        status=str(payload.get("status") or "present"),
        summary=str(payload.get("summary") or ""),
        before_report=str(payload.get("before_report") or ""),
        after_report=str(payload.get("after_report") or ""),
        resolved_signals=_signals(payload, ["resolved_user_assertions", "resolved_signals", "resolved"]),
        unresolved_signals=_signals(payload, ["remaining_user_assertions", "unresolved_signals", "unresolved"]),
        new_signals=_signals(payload, ["new_user_assertions", "new_signals", "new"]),
        changed_signals=_signals(payload, ["changed_signals", "changed"]),
        evidence_delta=_int_or_none(payload.get("evidence_delta")),
        timeline_delta=_int_or_none(payload.get("timeline_delta")),
        test_record_delta=_int_or_none(payload.get("test_record_delta")),
        notes=_signals(payload, ["notes"]),
        markdown=markdown,
        raw=payload,
    )


def _find_first(package_dir: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = package_dir / candidate
        if path.is_file():
            return path
    return None


def _relative(package_dir: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(package_dir))
    except ValueError:
        return str(path)


def _signals(payload: dict[str, Any], keys: list[str]) -> list[str]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [str(item) for item in value]
    return []


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) else None
