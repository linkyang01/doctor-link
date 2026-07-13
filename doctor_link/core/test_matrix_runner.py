from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doctor_link.core.automated_evidence import record_automated_result
from doctor_link.core.safe_command_runner import run_safe_command_sequence


@dataclass
class TestMatrixJob:
    job_id: str
    title: str
    command: str
    required: bool = True
    related_verification_steps: list[str] = field(default_factory=list)
    related_assertion_ids: list[str] = field(default_factory=list)
    related_assertion_statements: list[str] = field(default_factory=list)

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
    required: bool = True
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
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return TestMatrixCatalog(path=str(path), warnings=[f"Invalid test-matrix.yml: {exc}"])
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
                related_assertion_ids=[str(value) for value in item.get("related_assertion_ids", []) or []],
                related_assertion_statements=[str(value) for value in item.get("related_assertion_statements", []) or []],
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
        completed = run_safe_command_sequence(job.command, cwd=project_root, timeout_seconds=timeout_seconds)
        result = TestMatrixRunResult(job_id=job.job_id, status="passed" if completed.returncode == 0 else "failed", required=job.required, return_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        if package_dir is not None:
            result.evidence_id = write_test_matrix_evidence(package_dir, job, result)
        results.append(result)
    return results


def write_test_matrix_evidence(package_dir: Path, job: TestMatrixJob, result: TestMatrixRunResult) -> str:
    evidence_id = f"test-matrix-{job.job_id}"
    payload = {"job": job.to_dict(), "result": result.to_dict()}
    payload["result"]["evidence_id"] = evidence_id
    actual = result.stdout.strip() or result.stderr.strip() or f"Status: {result.status}"
    return record_automated_result(
        package_dir,
        output_relative_path=f"evidence/test-results/{job.job_id}.json",
        output_payload=payload,
        evidence_id=evidence_id,
        evidence_kind="test_result",
        evidence_title=f"Test matrix {job.job_id}",
        evidence_source="doctor-link test run",
        action="run_test_matrix",
        target=job.job_id,
        status=result.status,
        expected="; ".join(job.related_verification_steps) or "Command exits successfully",
        actual=actual,
        explicit_assertion_ids=job.related_assertion_ids,
        assertion_statements=job.related_assertion_statements,
    )
