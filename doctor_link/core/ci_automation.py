from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso
from doctor_link.core.project_health import build_project_health


@dataclass
class CIAutomationReport:
    reports_dir: str
    output_dir: str
    generated_at: str = field(default_factory=utc_now_iso)
    status: str = "unknown"
    package_count: int = 0
    failure_triage: list[dict[str, Any]] = field(default_factory=list)
    regression_score: int = 100
    test_matrix_summary: dict[str, Any] = field(default_factory=dict)
    health_trend: dict[str, Any] = field(default_factory=dict)
    artifact_index: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link CI Report",
            "",
            f"- Generated at: `{self.generated_at}`",
            f"- Reports dir: `{self.reports_dir}`",
            f"- Status: `{self.status}`",
            f"- Diagnostic packages: `{self.package_count}`",
            f"- Regression score: `{self.regression_score}`",
            f"- Test jobs: `{self.test_matrix_summary.get('total', 0)}`",
            f"- Failed test jobs: `{self.test_matrix_summary.get('failed', 0)}`",
            "",
            "## Failure Triage",
        ]
        if not self.failure_triage:
            lines.append("- None")
        for item in self.failure_triage:
            lines.append(
                f"- `{item.get('package')}`: severity=`{item.get('severity')}`, "
                f"category=`{item.get('category')}`, reason={item.get('reason')}"
            )
        lines.extend(["", "## Test Matrix Summary", "", _json_block(self.test_matrix_summary), "", "## Health Trend", "", _json_block(self.health_trend), "", "## Artifact Index", ""])
        for artifact in self.artifact_index.get("artifacts", []):
            lines.append(f"- `{artifact.get('path')}` ({artifact.get('kind')}, {artifact.get('size_bytes')} bytes)")
        if not self.artifact_index.get("artifacts"):
            lines.append("- None")
        lines.append("")
        return "\n".join(lines)

    def to_github_markdown(self) -> str:
        icon = "✅" if self.status == "passed" else "⚠️"
        lines = [
            f"# {icon} Doctor link CI Summary",
            "",
            f"**Status:** `{self.status}`  ",
            f"**Packages:** `{self.package_count}`  ",
            f"**Regression score:** `{self.regression_score}`  ",
            f"**Failed test jobs:** `{self.test_matrix_summary.get('failed', 0)}`  ",
            "",
            "## Top failure triage",
        ]
        if not self.failure_triage:
            lines.append("No blocking diagnostic failures detected.")
        for item in self.failure_triage[:10]:
            lines.append(f"- `{item.get('package')}` — **{item.get('category')}**: {item.get('reason')}")
        lines.extend(["", "## Artifacts", ""])
        for artifact in self.artifact_index.get("artifacts", [])[:20]:
            lines.append(f"- `{artifact.get('path')}`")
        if not self.artifact_index.get("artifacts"):
            lines.append("No artifacts indexed.")
        lines.append("")
        return "\n".join(lines)


def build_ci_report(reports_dir: Path, output_dir: Path | None = None) -> CIAutomationReport:
    reports_dir = reports_dir.resolve()
    output = (output_dir or reports_dir / "ci").resolve()
    package_dirs = _package_dirs(reports_dir)
    triage = _build_failure_triage(package_dirs)
    test_summary = _build_test_matrix_summary(package_dirs)
    trend = _build_health_trend(reports_dir, package_dirs)
    artifact_index = _build_artifact_index(reports_dir, output)
    regression_score = _compute_regression_score(triage, test_summary, trend)
    status = "passed" if regression_score >= 80 and not any(item.get("severity") == "blocking" for item in triage) else "needs_attention"
    return CIAutomationReport(
        reports_dir=str(reports_dir),
        output_dir=str(output),
        status=status,
        package_count=len(package_dirs),
        failure_triage=triage,
        regression_score=regression_score,
        test_matrix_summary=test_summary,
        health_trend=trend,
        artifact_index=artifact_index,
    )


def write_ci_report(reports_dir: Path, output_dir: Path | None = None) -> CIAutomationReport:
    report = build_ci_report(reports_dir, output_dir)
    out = Path(report.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    artifact_index = _build_artifact_index(Path(report.reports_dir), out)
    report.artifact_index = artifact_index
    (out / "ci-report.json").write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "ci-report.md").write_text(report.to_markdown(), encoding="utf-8")
    (out / "github-step-summary.md").write_text(report.to_github_markdown(), encoding="utf-8")
    (out / "ci-artifact-index.json").write_text(json.dumps(report.artifact_index, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "project-health-trend.json").write_text(json.dumps(report.health_trend, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def _package_dirs(reports_dir: Path) -> list[Path]:
    if not reports_dir.exists():
        return []
    return sorted(item for item in reports_dir.iterdir() if item.is_dir() and (item / "doctor-report.json").exists())


def _build_failure_triage(package_dirs: list[Path]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for package_dir in package_dirs:
        verification = _read_json(package_dir / "verification-result.json", {})
        pipeline = _read_json(package_dir / "diagnosis-pipeline-summary.json", {})
        comparison = _read_json(package_dir / "report-comparison.json", _read_json(package_dir / "comparison-result.json", {}))
        if not isinstance(verification, dict):
            verification = {}
        status = str(verification.get("status") or pipeline.get("verification_status") or "missing") if isinstance(pipeline, dict) else str(verification.get("status") or "missing")
        missing = verification.get("missing_evidence") if isinstance(verification.get("missing_evidence"), list) else []
        if status not in {"verified", "passed", "candidate_verified"}:
            items.append({
                "package": package_dir.name,
                "severity": "blocking" if status in {"missing", "missing_evidence", "failed", "not_verified"} else "warning",
                "category": "verification",
                "reason": f"verification status is {status}",
                "missing_evidence": missing,
            })
        if missing:
            items.append({
                "package": package_dir.name,
                "severity": "blocking",
                "category": "missing_evidence",
                "reason": f"{len(missing)} missing evidence item(s)",
                "missing_evidence": missing,
            })
        if isinstance(pipeline, dict) and pipeline.get("success") is False:
            items.append({"package": package_dir.name, "severity": "warning", "category": "pipeline", "reason": "diagnosis pipeline success is false"})
        comparison_text = json.dumps(comparison, ensure_ascii=False).lower() if isinstance(comparison, dict) else ""
        if "regression" in comparison_text or "unresolved" in comparison_text:
            items.append({"package": package_dir.name, "severity": "warning", "category": "comparison", "reason": "comparison contains regression or unresolved signal"})
    return items


def _build_test_matrix_summary(package_dirs: list[Path]) -> dict[str, Any]:
    jobs: list[dict[str, Any]] = []
    for package_dir in package_dirs:
        for path in sorted((package_dir / "evidence" / "test-results").glob("*.json")):
            payload = _read_json(path, {})
            if not isinstance(payload, dict):
                continue
            result = payload.get("result") if isinstance(payload.get("result"), dict) else payload
            job = payload.get("job") if isinstance(payload.get("job"), dict) else {}
            status = str(result.get("status") or payload.get("status") or "unknown")
            job_id = str(job.get("job_id") or result.get("job_id") or path.stem)
            jobs.append({
                "package": package_dir.name,
                "job_id": job_id,
                "status": status,
                "return_code": result.get("return_code"),
                "path": str(path.relative_to(package_dir)),
            })
    total = len(jobs)
    failed = sum(1 for item in jobs if item.get("status") not in {"passed", "success", "verified"})
    passed = sum(1 for item in jobs if item.get("status") in {"passed", "success", "verified"})
    return {"total": total, "passed": passed, "failed": failed, "jobs": jobs}


def _build_health_trend(reports_dir: Path, package_dirs: list[Path]) -> dict[str, Any]:
    health = build_project_health(reports_dir)
    points: list[dict[str, Any]] = []
    for package in health.packages:
        score = 100
        if package.get("verification_status") not in {"verified", "passed", "candidate_verified"}:
            score -= 35
        score -= min(int(package.get("unresolved_assertion_count") or 0) * 10, 30)
        score -= min(int(package.get("regression_count") or 0) * 15, 30)
        points.append({"package": package.get("name"), "score": max(score, 0), "verification_status": package.get("verification_status")})
    average = round(sum(item["score"] for item in points) / len(points), 2) if points else 100.0
    direction = "stable"
    if len(points) >= 2:
        if points[-1]["score"] > points[0]["score"]:
            direction = "improving"
        elif points[-1]["score"] < points[0]["score"]:
            direction = "declining"
    return {"status": health.status, "average_score": average, "direction": direction, "points": points, "source_package_count": len(package_dirs)}


def _build_artifact_index(reports_dir: Path, output_dir: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    roots = [reports_dir]
    if output_dir.exists() and output_dir not in roots:
        roots.append(output_dir)
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if ".git" in path.parts:
                continue
            artifacts.append({
                "path": str(path),
                "relative_path": str(path.relative_to(root)),
                "root": str(root),
                "kind": _artifact_kind(path),
                "size_bytes": path.stat().st_size,
            })
    return {"generated_at": utc_now_iso(), "artifact_count": len(artifacts), "artifacts": artifacts}


def _compute_regression_score(triage: list[dict[str, Any]], test_summary: dict[str, Any], trend: dict[str, Any]) -> int:
    score = 100
    score -= sum(25 for item in triage if item.get("severity") == "blocking")
    score -= sum(10 for item in triage if item.get("severity") == "warning")
    score -= int(test_summary.get("failed", 0)) * 15
    if trend.get("direction") == "declining":
        score -= 10
    return max(score, 0)


def _artifact_kind(path: Path) -> str:
    name = path.name
    if name.endswith(".json"):
        return "json"
    if name.endswith(".md"):
        return "markdown"
    if name.endswith(".html"):
        return "html"
    if name.endswith(".zip"):
        return "archive"
    return "file"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
