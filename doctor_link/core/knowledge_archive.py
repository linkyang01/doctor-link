from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso

KNOWLEDGE_SCHEMA = "doctor-link-knowledge-index-v1"
ARCHIVE_SCHEMA = "doctor-link-archive-v1"
DEFAULT_REPORT_GLOBS = ["**/doctor-report.json", "**/diagnosis-pipeline-summary.json", "**/verification-result.json"]


@dataclass
class KnowledgeIndex:
    root: str
    generated_at: str = field(default_factory=utc_now_iso)
    schema: str = KNOWLEDGE_SCHEMA
    records: list[dict[str, Any]] = field(default_factory=list)
    recurring_failures: list[dict[str, Any]] = field(default_factory=list)
    repair_outcomes: dict[str, Any] = field(default_factory=dict)
    health_trend: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeQueryResult:
    query: str
    matched_count: int
    records: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArchiveRecord:
    archive_root: str
    source_root: str
    generated_at: str = field(default_factory=utc_now_iso)
    schema: str = ARCHIVE_SCHEMA
    metadata: dict[str, Any] = field(default_factory=dict)
    files: list[dict[str, Any]] = field(default_factory=list)
    audit: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PolicyCheckResult:
    status: str
    archive_root: str
    checked_at: str = field(default_factory=utc_now_iso)
    findings: list[dict[str, Any]] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_knowledge_index(reports_root: Path) -> KnowledgeIndex:
    reports_root = reports_root.resolve()
    records = _load_report_records(reports_root)
    return KnowledgeIndex(
        root=str(reports_root),
        records=records,
        recurring_failures=_extract_recurring_failures(records),
        repair_outcomes=_aggregate_repair_outcomes(records),
        health_trend=_aggregate_health_trend(records),
    )


def write_knowledge_index(reports_root: Path, output: Path) -> KnowledgeIndex:
    index = build_knowledge_index(reports_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return index


def load_knowledge_index(path: Path) -> KnowledgeIndex:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return KnowledgeIndex(
        root=str(payload.get("root") or ""),
        generated_at=str(payload.get("generated_at") or utc_now_iso()),
        schema=str(payload.get("schema") or KNOWLEDGE_SCHEMA),
        records=payload.get("records") if isinstance(payload.get("records"), list) else [],
        recurring_failures=payload.get("recurring_failures") if isinstance(payload.get("recurring_failures"), list) else [],
        repair_outcomes=payload.get("repair_outcomes") if isinstance(payload.get("repair_outcomes"), dict) else {},
        health_trend=payload.get("health_trend") if isinstance(payload.get("health_trend"), dict) else {},
    )


def query_knowledge(index_path: Path, query: str, limit: int = 20) -> KnowledgeQueryResult:
    index = load_knowledge_index(index_path)
    terms = [term.lower() for term in re.findall(r"\w+", query)]
    matches: list[dict[str, Any]] = []
    for record in index.records:
        text = json.dumps(record, ensure_ascii=False).lower()
        if all(term in text for term in terms):
            matches.append(record)
    return KnowledgeQueryResult(query=query, matched_count=len(matches), records=matches[:limit])


def export_knowledge(index_path: Path, output: Path) -> KnowledgeIndex:
    index = load_knowledge_index(index_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return index


def create_archive(source_root: Path, archive_root: Path, metadata: dict[str, Any] | None = None) -> ArchiveRecord:
    source_root = source_root.resolve()
    archive_root = archive_root.resolve()
    if archive_root == source_root or _is_relative_to(archive_root, source_root):
        raise ValueError("archive_root must not be the source root or inside the source root.")
    archive_root.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
        rel = source.relative_to(source_root)
        target = archive_root / "files" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        files.append({"path": rel.as_posix(), "size_bytes": target.stat().st_size})
    record = ArchiveRecord(
        archive_root=str(archive_root),
        source_root=str(source_root),
        metadata=metadata or {},
        files=files,
        audit=[_audit("archive-created", {"file_count": len(files)})],
    )
    _write_archive_record(archive_root, record)
    append_archive_audit(archive_root, "archive-created", {"file_count": len(files)})
    return record


def inspect_archive(archive_root: Path) -> ArchiveRecord:
    record_path = archive_root / "archive-record.json"
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    return ArchiveRecord(
        archive_root=str(payload.get("archive_root") or archive_root),
        source_root=str(payload.get("source_root") or ""),
        generated_at=str(payload.get("generated_at") or utc_now_iso()),
        schema=str(payload.get("schema") or ARCHIVE_SCHEMA),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        files=payload.get("files") if isinstance(payload.get("files"), list) else [],
        audit=payload.get("audit") if isinstance(payload.get("audit"), list) else [],
    )


def check_archive_policy(archive_root: Path, max_files: int | None = None, max_size_bytes: int | None = None) -> PolicyCheckResult:
    record = inspect_archive(archive_root)
    total_size = sum(int(item.get("size_bytes") or 0) for item in record.files)
    findings: list[dict[str, Any]] = []
    if max_files is not None and len(record.files) > max_files:
        findings.append(_finding("blocking", "retention-file-count-exceeded", f"Archive has {len(record.files)} files."))
    if max_size_bytes is not None and total_size > max_size_bytes:
        findings.append(_finding("blocking", "retention-size-exceeded", f"Archive size is {total_size} bytes."))
    status = "passed" if not findings else "blocked"
    return PolicyCheckResult(
        status=status,
        archive_root=str(archive_root.resolve()),
        findings=findings,
        policy={"max_files": max_files, "max_size_bytes": max_size_bytes, "total_size_bytes": total_size},
    )


def append_archive_audit(archive_root: Path, event: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    audit = _audit(event, details or {})
    audit_path = archive_root / "archive-audit.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(audit, ensure_ascii=False) + "\n")
    return audit


def export_archive(archive_root: Path, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    shutil.make_archive(str(output.with_suffix("")), "zip", archive_root)
    final = output.with_suffix(".zip")
    append_archive_audit(archive_root, "archive-exported", {"output": str(final)})
    return final


def _load_report_records(reports_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for pattern in DEFAULT_REPORT_GLOBS:
        for path in sorted(reports_root.glob(pattern)):
            if path in seen:
                continue
            seen.add(path)
            payload = _read_json(path)
            if payload is None:
                continue
            records.append(_normalize_record(reports_root, path, payload))
    return records


def _normalize_record(root: Path, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    status = str(payload.get("status") or payload.get("verification_status") or payload.get("comparison_status") or "unknown")
    project = str(payload.get("project") or payload.get("project_name") or payload.get("adapter_id") or path.parent.name)
    text = json.dumps(payload, ensure_ascii=False).lower()
    failure_terms = sorted(set(re.findall(r"(?:error|failed|missing|regression|blocked|unresolved)[\w-]*", text)))
    return {
        "path": path.relative_to(root).as_posix(),
        "project": project,
        "status": status,
        "failure_terms": failure_terms,
        "summary": str(payload.get("summary") or payload.get("message") or ""),
        "payload": payload,
    }


def _extract_recurring_failures(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    paths: dict[str, list[str]] = {}
    for record in records:
        for term in record.get("failure_terms", []):
            counts[term] = counts.get(term, 0) + 1
            paths.setdefault(term, []).append(str(record.get("path") or ""))
    return [
        {"signature": term, "count": count, "paths": paths.get(term, [])}
        for term, count in sorted(counts.items())
        if count >= 2
    ]


def _aggregate_repair_outcomes(records: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(1 for record in records if str(record.get("status")) in {"passed", "verified", "candidate_verified"})
    blocked = sum(1 for record in records if str(record.get("status")) in {"blocked", "failed", "missing"})
    unknown = max(len(records) - passed - blocked, 0)
    return {"passed": passed, "blocked": blocked, "unknown": unknown, "total": len(records)}


def _aggregate_health_trend(records: list[dict[str, Any]]) -> dict[str, Any]:
    points = []
    for index, record in enumerate(records):
        status = str(record.get("status") or "unknown")
        score = 100 if status in {"passed", "verified", "candidate_verified"} else 50 if status == "unknown" else 0
        points.append({"index": index, "path": record.get("path"), "status": status, "score": score})
    average = round(sum(point["score"] for point in points) / len(points), 2) if points else 100.0
    return {"average_score": average, "points": points}


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_archive_record(archive_root: Path, record: ArchiveRecord) -> None:
    (archive_root / "archive-record.json").write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _audit(event: str, details: dict[str, Any]) -> dict[str, Any]:
    return {"event": event, "timestamp": utc_now_iso(), "details": details}


def _finding(severity: str, code: str, message: str) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message}
