from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.schema_validator import SchemaValidationResult, validate_diagnostic_package


@dataclass
class ConformanceCaseResult:
    case_id: str
    group: str
    package_dir: str
    expected_valid: bool
    actual_valid: bool
    passed: bool
    error_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConformanceReport:
    fixtures_root: str
    status: str = "passed"
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    compatibility_score: float = 0.0
    results: list[ConformanceCaseResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixtures_root": self.fixtures_root,
            "status": self.status,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "compatibility_score": self.compatibility_score,
            "results": [item.to_dict() for item in self.results],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link Conformance Report",
            "",
            f"- Fixtures root: `{self.fixtures_root}`",
            f"- Status: `{self.status}`",
            f"- Total cases: `{self.total_cases}`",
            f"- Passed cases: `{self.passed_cases}`",
            f"- Failed cases: `{self.failed_cases}`",
            f"- Compatibility score: `{self.compatibility_score}`",
            "",
            "## Results",
        ]
        if not self.results:
            lines.append("- No conformance cases found.")
        for item in self.results:
            lines.append(
                f"- `{item.group}/{item.case_id}`: passed=`{item.passed}`, expected_valid=`{item.expected_valid}`, actual_valid=`{item.actual_valid}`, errors=`{item.error_count}`, warnings=`{item.warning_count}`"
            )
        lines.append("")
        return "\n".join(lines)


CONFORMANCE_GROUPS: dict[str, bool] = {
    "valid": True,
    "invalid": False,
    "backward-compatible": True,
    "migration": True,
}


def run_conformance_suite(fixtures_root: Path) -> ConformanceReport:
    fixtures_root = fixtures_root.resolve()
    report = ConformanceReport(fixtures_root=str(fixtures_root))
    if not fixtures_root.is_dir():
        report.status = "failed"
        return report

    for group, expected_valid in CONFORMANCE_GROUPS.items():
        group_dir = fixtures_root / group
        if not group_dir.exists():
            continue
        for package_dir in sorted(item for item in group_dir.iterdir() if item.is_dir()):
            validation = validate_diagnostic_package(package_dir)
            result = _case_result(group, package_dir, expected_valid, validation)
            report.results.append(result)

    report.total_cases = len(report.results)
    report.passed_cases = sum(1 for item in report.results if item.passed)
    report.failed_cases = report.total_cases - report.passed_cases
    report.compatibility_score = round((report.passed_cases / report.total_cases) * 100, 2) if report.total_cases else 0.0
    report.status = "passed" if report.failed_cases == 0 and report.total_cases > 0 else "failed"
    return report


def write_conformance_report(output_dir: Path, report: ConformanceReport) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "conformance-report.json").write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "conformance-report.md").write_text(report.to_markdown(), encoding="utf-8")


def _case_result(group: str, package_dir: Path, expected_valid: bool, validation: SchemaValidationResult) -> ConformanceCaseResult:
    error_count = sum(1 for item in validation.findings if item.level == "error")
    warning_count = sum(1 for item in validation.findings if item.level == "warning")
    actual_valid = validation.valid
    return ConformanceCaseResult(
        case_id=package_dir.name,
        group=group,
        package_dir=str(package_dir),
        expected_valid=expected_valid,
        actual_valid=actual_valid,
        passed=actual_valid == expected_valid,
        error_count=error_count,
        warning_count=warning_count,
    )
