from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doctor_link.core.models import EvidenceItem, TimelineStep


@dataclass
class TestMatrixJob:
    job_id: str
    title: str
    command: str
    required: bool = True
    related_verification_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TestMatrixCatalog:
    path: str
    jobs: list[TestMatrixJob] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "jobs": [job.to_dict() for job in self.jobs], "warnings": self.warnings}


@dataclass
class TestMatrixRunResult:
    job_id: str
    status: str
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    evidence_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def test_matrix_path(project_root: Path) -> Path:
    return project_root / ".doctorlink" / "test-matrix.yml"


def load_test_matrix(project_root: Path) -> TestMatrixCatalog:
    path = test_matrix_path(project_root)
    if not path.exists():
        return TestMatrixCatalog(path=str(path), warnings=["Missing .doctorlink/test-matrix.yml"])
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return TestMatrixCatalog(path=str(path), warnings=["test-matrix.yml must be a mapping"])
    jobs_raw = raw.get("jobs") or []
    cases_raw = raw.get("cases") or []
    warnings: list[str] = []
    jobs: list[TestMatrixJob] = []
    if jobs_raw and not isinstance(jobs_raw, list):
        warnings.append("jobs must be a list")
        jobs_raw = []
    for index, item in enumerate(jobs_raw, start=1):
        if not isinstance(item, dict):
            warnings.append(f"jobs[{index}] must be a mapping")
            continue
        command = str(item.get("command") or "")
        if not command:
            warnings.append(f"{item.get('id', index)} missing command")
            continue
        jobs.append(
            TestMatrixJob(
                job_id=str(item.get("id") or f"job-{index}"),
                title=str(item.get("title") or item.get("name") or f"Test job {index}"),
                command=command,
                required=bool(item.get("required", True)),
                related_verification_steps=[str(value) for value in item.get("related_verification_steps", []) or []],
            )
        )
    if not jobs and isinstance(cases_raw, list):
        warnings.append("No executable jobs configured; legacy cases are informational only")
    return TestMatrixCatalog(path=str(path), jobs=jobs, warnings=warnings)


def run_test_matrix(project_root: Path, package_dir: Path | None = None, job_id: str | None = None, timeout_seconds: int = 120) -> list[TestMatrixRunResult]:
    catalog = load_test_matrix(project_root)
    selected = [job for job in catalog.jobs if job_id is None or job.job_id == job_id]
    if job_id is not None and not selected:
        raise ValueError(f"Unknown test matrix job id: {job_id}")
    results: list[TestMatrixRunResult] = []
    for job in selected:
        completed = subprocess.run(job.command, shell=True, cwd=project_root, text=True, capture_output=True, timeout=timeout_seconds, check=False)
        result = TestMatrixRunResult(job_id=job.job_id, status="passed" if completed.returncode == 0 else "failed", return_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        if package_dir is not None:
            result.evidence_id = write_test_matrix_evidence(package_dir, job, result)
        results.append(result)
    return results


def write_test_matrix_evidence(package_dir: Path, job: TestMatrixJob, result: TestMatrixRunResult) -> str:
    evidence_dir = package_dir / "evidence" / "test-results"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_id = f"test-matrix-{job.job_id}"
    output_path = evidence_dir / f"{job.job_id}.json"
    relative_path = str(output_path.relative_to(package_dir))
    output_path.write_text(json.dumps({"job": job.to_dict(), "result": result.to_dict()}, ensure_ascii=False, indent=2), encoding="utf-8")
    evidence = EvidenceItem(evidence_id=evidence_id, kind="test_result", title=f"Test matrix {job.job_id}", source="doctor-link test run", path=relative_path, content=f"Status: {result.status}")
    _append_evidence(package_dir, evidence)
    step = TimelineStep(step_id=evidence_id, action="run_test_matrix", target=job.job_id, actual_result=f"Status: {result.status}", status=result.status, evidence_ids=[evidence_id])
    _append_timeline(package_dir, step)
    return evidence_id


def _append_evidence(package_dir: Path, item: EvidenceItem) -> None:
    path = package_dir / "evidence-list.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Evidence List\n\n"
    path.write_text(existing.rstrip() + f"\n- `{item.evidence_id}` ({item.kind}): {item.title} — {item.path}\n", encoding="utf-8")


def _append_timeline(package_dir: Path, step: TimelineStep) -> None:
    path = package_dir / "timeline.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Timeline\n\n"
    label = step.target or step.step_id
    path.write_text(existing.rstrip() + f"\n- `{step.step_id}` Run test matrix {label}: {step.actual_result}\n", encoding="utf-8")
