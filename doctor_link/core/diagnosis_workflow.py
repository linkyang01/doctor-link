from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from doctor_link.core.models import DiagnosticEvent, utc_now_iso
from doctor_link.core.package_builder import build_diagnostic_package


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
    (package_dir / "diagnosis-workflow.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "diagnosis-workflow.md").write_text(_metadata_markdown(metadata), encoding="utf-8")
    report_path = package_dir / "doctor-report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if isinstance(report, dict):
            report["diagnosis_workflow"] = payload
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


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
