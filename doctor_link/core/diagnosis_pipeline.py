from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from doctor_link.core.diagnosis_workflow import read_workflow_metadata
from doctor_link.core.report_comparator import write_report_comparison_to_package
from doctor_link.core.verification_runner import run_verification
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text, package_transaction


@dataclass
class DiagnosisPipelineSummary:
    package_dir: str
    before_report: str | None
    comparison_status: str
    verification_status: str
    success: bool
    missing_evidence: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Diagnosis Pipeline Summary",
            "",
            f"- Package: `{self.package_dir}`",
            f"- Before report: `{self.before_report or ''}`",
            f"- Comparison status: `{self.comparison_status}`",
            f"- Verification status: `{self.verification_status}`",
            f"- Success: `{self.success}`",
            "",
            "## Missing Evidence",
            *([f"- {item}" for item in self.missing_evidence] if self.missing_evidence else ["- None"]),
            "",
            "## Notes",
            *([f"- {item}" for item in self.notes] if self.notes else ["- None"]),
            "",
        ]
        return "\n".join(lines)


def run_diagnosis_compare(after_package: Path) -> DiagnosisPipelineSummary:
    metadata = read_workflow_metadata(after_package)
    notes: list[str] = []
    before_report = metadata.before_report if metadata is not None else None
    comparison_status = "not_run"
    if before_report and Path(before_report).exists():
        write_report_comparison_to_package(Path(before_report), after_package)
        comparison_status = "generated"
    else:
        notes.append("before_report is missing; comparison was not generated")
    verification = _read_verification(after_package)
    summary = DiagnosisPipelineSummary(
        package_dir=str(after_package),
        before_report=before_report,
        comparison_status=comparison_status,
        verification_status=str(verification.get("status", "not_run")),
        success=False,
        missing_evidence=list(verification.get("missing_evidence", [])),
        notes=notes,
    )
    _write_summary(after_package, summary)
    return summary


def run_diagnosis_verify(after_package: Path, write_back: bool = True) -> DiagnosisPipelineSummary:
    metadata = read_workflow_metadata(after_package)
    before_report = metadata.before_report if metadata is not None else None
    notes: list[str] = []
    comparison_status = "not_run"
    if before_report and Path(before_report).exists():
        write_report_comparison_to_package(Path(before_report), after_package)
        comparison_status = "generated"
    else:
        notes.append("before_report is missing; comparison was not generated")
    result = run_verification(after_package, write_back=write_back)
    success = result.status in {"verified", "candidate_verified", "ready"} and not result.missing_evidence and not result.blocking_test_records
    if not success:
        notes.append("pipeline is not successful until verification evidence is complete")
    summary = DiagnosisPipelineSummary(
        package_dir=str(after_package),
        before_report=before_report,
        comparison_status=comparison_status,
        verification_status=result.status,
        success=success,
        missing_evidence=list(result.missing_evidence),
        notes=notes,
    )
    _write_summary(after_package, summary)
    return summary


def _read_verification(package_dir: Path) -> dict[str, Any]:
    path = package_dir / "verification-result.json"
    if not path.exists():
        return {"status": "not_run", "missing_evidence": ["verification-result.json"]}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"status": "invalid", "missing_evidence": ["verification-result.json"]}


def _write_summary(package_dir: Path, summary: DiagnosisPipelineSummary) -> None:
    payload = summary.to_dict()
    with package_transaction(package_dir):
        atomic_write_json(package_dir / "diagnosis-pipeline-summary.json", payload)
        atomic_write_text(package_dir / "diagnosis-pipeline-summary.md", summary.to_markdown())
        report_path = package_dir / "doctor-report.json"
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if isinstance(report, dict):
                report["diagnosis_pipeline_summary"] = payload
                atomic_write_json(report_path, report)
