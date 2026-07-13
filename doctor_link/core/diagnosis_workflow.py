from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from doctor_link.core.models import DiagnosticEvent, utc_now_iso
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text, package_transaction


@dataclass
class DiagnosisWorkflowMetadata:
    workflow_id: str
    phase: str
    created_at: str
    project: str
    summary: str
    before_package: str | None = None
    before_report: str | None = None
    after_package: str | None = None
    after_report: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_before_package(project: str, summary: str, output_dir: Path) -> Path:
    workflow_id = _workflow_id(project)
    package = build_diagnostic_package(
        DiagnosticEvent(project=project, category="p4_before", summary=summary),
        output_dir,
    )
    if package.root_dir is None:
        raise RuntimeError("Failed to create before diagnostic package")
    metadata = DiagnosisWorkflowMetadata(
        workflow_id=workflow_id,
        phase="before",
        created_at=utc_now_iso(),
        project=project,
        summary=summary,
        before_package=str(package.root_dir),
        before_report=str(package.root_dir / "doctor-report.json"),
    )
    _write_metadata(package.root_dir, metadata)
    return package.root_dir


def create_after_package(project: str, summary: str, output_dir: Path, before_package: Path) -> Path:
    before_meta = read_workflow_metadata(before_package)
    workflow_id = before_meta.workflow_id if before_meta is not None else _workflow_id(project)
    before_report = str(before_package / "doctor-report.json")
    package = build_diagnostic_package(
        DiagnosticEvent(project=project, category="p4_after", summary=summary),
        output_dir,
    )
    if package.root_dir is None:
        raise RuntimeError("Failed to create after diagnostic package")
    metadata = DiagnosisWorkflowMetadata(
        workflow_id=workflow_id,
        phase="after",
        created_at=utc_now_iso(),
        project=project,
        summary=summary,
        before_package=str(before_package),
        before_report=before_report,
        after_package=str(package.root_dir),
        after_report=str(package.root_dir / "doctor-report.json"),
    )
    _write_metadata(package.root_dir, metadata)
    _inherit_before_context(before_package, package.root_dir)
    return package.root_dir


def read_workflow_metadata(package_dir: Path) -> DiagnosisWorkflowMetadata | None:
    path = package_dir / "diagnosis-workflow.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return DiagnosisWorkflowMetadata(
        workflow_id=str(data.get("workflow_id") or ""),
        phase=str(data.get("phase") or ""),
        created_at=str(data.get("created_at") or ""),
        project=str(data.get("project") or ""),
        summary=str(data.get("summary") or ""),
        before_package=data.get("before_package"),
        before_report=data.get("before_report"),
        after_package=data.get("after_package"),
        after_report=data.get("after_report"),
    )


def _write_metadata(package_dir: Path, metadata: DiagnosisWorkflowMetadata) -> None:
    payload = metadata.to_dict()
    atomic_write_json(package_dir / "diagnosis-workflow.json", payload)
    atomic_write_text(package_dir / "diagnosis-workflow.md", _metadata_markdown(metadata))
    report_path = package_dir / "doctor-report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if isinstance(report, dict):
            report["diagnosis_workflow"] = payload
            atomic_write_json(report_path, report)


def _inherit_before_context(before_package: Path, after_package: Path) -> None:
    """Carry unresolved human context into the after package.

    Assertions remain present until after-state test records linked to their IDs
    demonstrate resolution. Their absence must never be treated as proof.
    """
    with package_transaction(after_package):
        assertions = _read_list(before_package / "user-assertions.json")
        atomic_write_json(after_package / "user-assertions.json", assertions)

        before_report = _read_dict(before_package / "doctor-report.json")
        after_report_path = after_package / "doctor-report.json"
        after_report = _read_dict(after_report_path)
        after_report["user_assertions"] = assertions
        if before_report.get("investigation_boundary"):
            after_report["investigation_boundary"] = before_report["investigation_boundary"]
        before_task = before_report.get("ai_task") if isinstance(before_report.get("ai_task"), dict) else {}
        after_task = after_report.setdefault("ai_task", {})
        for key in ("investigation_boundary", "do_not_change"):
            if before_task.get(key):
                after_task[key] = before_task[key]
        if assertions:
            requested = after_task.setdefault("requested_work", [])
            for assertion in assertions:
                if not isinstance(assertion, dict):
                    continue
                statement = str(assertion.get("user_statement") or assertion.get("statement") or "")
                if statement:
                    instruction = f"Reverify inherited user assertion: {statement}"
                    if instruction not in requested:
                        requested.append(instruction)
        atomic_write_json(after_report_path, after_report)

        boundary_path = before_package / "investigation-boundary.md"
        if boundary_path.exists():
            atomic_write_text(after_package / "investigation-boundary.md", boundary_path.read_text(encoding="utf-8"))
        if assertions:
            lines = ["", "## Inherited user assertions", ""]
            for assertion in assertions:
                if not isinstance(assertion, dict):
                    continue
                assertion_id = str(assertion.get("assertion_id") or assertion.get("id") or "unknown")
                statement = str(assertion.get("user_statement") or assertion.get("statement") or "")
                lines.append(f"- `{assertion_id}`: {statement}")
            lines.extend(["", "These assertions remain unresolved until linked after-state tests pass.", ""])
            task_path = after_package / "ai-task.md"
            current = task_path.read_text(encoding="utf-8") if task_path.exists() else ""
            atomic_write_text(task_path, current.rstrip() + "\n" + "\n".join(lines))


def _read_list(path: Path) -> list[Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return payload if isinstance(payload, list) else []


def _read_dict(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _metadata_markdown(metadata: DiagnosisWorkflowMetadata) -> str:
    return "\n".join(
        [
            "# Diagnosis Workflow",
            "",
            f"- Workflow ID: `{metadata.workflow_id}`",
            f"- Phase: `{metadata.phase}`",
            f"- Created at: `{metadata.created_at}`",
            f"- Project: `{metadata.project}`",
            f"- Summary: {metadata.summary}",
            f"- Before package: `{metadata.before_package or ''}`",
            f"- Before report: `{metadata.before_report or ''}`",
            f"- After package: `{metadata.after_package or ''}`",
            f"- After report: `{metadata.after_report or ''}`",
            "",
        ]
    )


def _workflow_id(project: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in project).strip("-") or "project"
    return f"workflow-{safe}"
