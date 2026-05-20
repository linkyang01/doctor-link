from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ProjectHealthSummary:
    reports_dir: str
    package_count: int = 0
    unresolved_assertions: int = 0
    failed_or_missing_verifications: int = 0
    recent_regressions: int = 0
    packages: list[dict[str, Any]] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.failed_or_missing_verifications or self.unresolved_assertions or self.recent_regressions:
            return "needs_attention"
        return "healthy"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status
        return payload

    def to_markdown(self) -> str:
        lines = [
            "# Project Health Summary",
            "",
            f"- Reports dir: `{self.reports_dir}`",
            f"- Status: `{self.status}`",
            f"- Diagnostic packages: `{self.package_count}`",
            f"- Unresolved assertions: `{self.unresolved_assertions}`",
            f"- Failed or missing verifications: `{self.failed_or_missing_verifications}`",
            f"- Recent regressions: `{self.recent_regressions}`",
            "",
            "## Packages",
        ]
        if not self.packages:
            lines.append("- None")
        for package in self.packages:
            lines.append(
                f"- `{package['name']}`: verification=`{package['verification_status']}`, "
                f"assertions={package['assertion_count']}, regressions={package['regression_count']}"
            )
        lines.append("")
        return "\n".join(lines)


def build_project_health(reports_dir: Path) -> ProjectHealthSummary:
    reports_dir = reports_dir.resolve()
    packages: list[dict[str, Any]] = []
    unresolved_assertions = 0
    failed_or_missing = 0
    regressions = 0
    for package_dir in sorted(_package_dirs(reports_dir)):
        package = _inspect_package(package_dir)
        packages.append(package)
        unresolved_assertions += package["unresolved_assertion_count"]
        if package["verification_status"] != "verified":
            failed_or_missing += 1
        regressions += package["regression_count"]
    return ProjectHealthSummary(
        reports_dir=str(reports_dir),
        package_count=len(packages),
        unresolved_assertions=unresolved_assertions,
        failed_or_missing_verifications=failed_or_missing,
        recent_regressions=regressions,
        packages=packages,
    )


def write_project_health(reports_dir: Path, output_dir: Path | None = None) -> ProjectHealthSummary:
    summary = build_project_health(reports_dir)
    out = output_dir or reports_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "project-health.json").write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "project-health.md").write_text(summary.to_markdown(), encoding="utf-8")
    return summary


def _package_dirs(reports_dir: Path) -> list[Path]:
    if not reports_dir.exists():
        return []
    return [item for item in reports_dir.iterdir() if item.is_dir() and (item / "doctor-report.json").exists()]


def _inspect_package(package_dir: Path) -> dict[str, Any]:
    report = _read_json(package_dir / "doctor-report.json", {})
    verification = _read_json(package_dir / "verification-result.json", None)
    assertions = _read_json(package_dir / "user-assertions.json", [])
    comparison = _read_json(package_dir / "comparison-result.json", None)
    pipeline = _read_json(package_dir / "diagnosis-pipeline-summary.json", None)
    assertion_items = assertions if isinstance(assertions, list) else []
    verification_status = "missing"
    if isinstance(verification, dict):
        verification_status = str(verification.get("status") or "unknown")
    regression_count = _regression_count(comparison, pipeline, report)
    return {
        "name": package_dir.name,
        "path": str(package_dir),
        "verification_status": verification_status,
        "assertion_count": len(assertion_items),
        "unresolved_assertion_count": len(assertion_items) if verification_status != "verified" else 0,
        "regression_count": regression_count,
    }


def _regression_count(*payloads: Any) -> int:
    count = 0
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        text = json.dumps(payload, ensure_ascii=False).lower()
        if "regression" in text or "failed" in text:
            count += 1
    return count


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
