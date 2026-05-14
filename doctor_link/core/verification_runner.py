from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from doctor_link.core.models import utc_now_iso

VerificationStatus = Literal["ready", "missing_evidence", "not_verified", "candidate_verified", "needs_review"]


@dataclass
class VerificationResult:
    package_dir: str
    generated_at: str = field(default_factory=utc_now_iso)
    status: VerificationStatus = "needs_review"
    summary: str = ""
    missing_evidence: list[str] = field(default_factory=list)
    tests_to_rerun: list[str] = field(default_factory=list)
    next_commands: list[str] = field(default_factory=list)
    checklist_present: bool = False
    user_assertion_count: int = 0
    test_record_count: int = 0
    report_comparison_status: str | None = None
    vly_core_proof_status: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link Verification Plan",
            "",
            f"- Package: `{self.package_dir}`",
            f"- Generated at: `{self.generated_at}`",
            f"- Status: `{self.status}`",
            "",
            "## Summary",
            self.summary or "No summary generated.",
            "",
            "## Missing evidence",
            *_list(self.missing_evidence),
            "",
            "## Tests to rerun",
            *_list(self.tests_to_rerun),
            "",
            "## Suggested next commands",
            *_list(self.next_commands),
            "",
            "## Signals",
            f"- Checklist present: `{self.checklist_present}`",
            f"- User assertions: `{self.user_assertion_count}`",
            f"- Test records: `{self.test_record_count}`",
            f"- Report comparison status: `{self.report_comparison_status or 'N/A'}`",
            f"- Vly Core Proof status: `{self.vly_core_proof_status or 'N/A'}`",
            "",
            "## Notes",
            *_list(self.notes),
            "",
        ]
        return "\n".join(lines)


def run_verification(package_dir: Path, write_back: bool = False) -> VerificationResult:
    """Generate a verification result from a diagnostic package.

    The runner does not claim production readiness. It checks whether evidence,
    user assertions, test records, report comparison, and readiness signals are
    present enough to continue or mark the fix as a candidate for verification.
    """
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    report = _read_json(package_dir / "doctor-report.json")
    user_assertions = _read_json(package_dir / "user-assertions.json", default=[])
    if isinstance(user_assertions, dict):
        user_assertions = user_assertions.get("assertions", []) or user_assertions.get("user_assertions", []) or []

    checklist_present = (package_dir / "fix-verification-checklist.md").is_file()
    test_records = report.get("test_records", []) or []
    evidence = report.get("evidence", []) or []
    report_comparison = report.get("report_comparison")
    vly_core_proof = report.get("vly_core_proof")

    result = VerificationResult(
        package_dir=str(package_dir),
        checklist_present=checklist_present,
        user_assertion_count=len(user_assertions),
        test_record_count=len(test_records),
        report_comparison_status=_comparison_status(report_comparison),
        vly_core_proof_status=_vly_status(vly_core_proof),
    )

    _assess_missing_evidence(result, evidence, checklist_present, test_records, report_comparison, vly_core_proof)
    _assess_tests(result, test_records, user_assertions)
    _assess_status(result)
    _add_next_commands(result, package_dir)
    result.summary = _summary(result)

    _write_outputs(package_dir, result)
    if write_back:
        _write_back(package_dir, report, result)
    return result


def _assess_missing_evidence(
    result: VerificationResult,
    evidence: list[Any],
    checklist_present: bool,
    test_records: list[Any],
    report_comparison: Any,
    vly_core_proof: Any,
) -> None:
    if not checklist_present:
        result.missing_evidence.append("fix-verification-checklist.md")
    if not evidence:
        result.missing_evidence.append("evidence entries in doctor-report.json")
    if not test_records:
        result.missing_evidence.append("test_records")
    if report_comparison is None:
        result.missing_evidence.append("report_comparison")
    if vly_core_proof is None:
        result.notes.append("No Vly Core Proof readiness signal found. This may be acceptable for non-Vly packages.")


def _assess_tests(result: VerificationResult, test_records: list[Any], user_assertions: list[Any]) -> None:
    if not test_records:
        result.tests_to_rerun.append("Run the relevant reproduction or regression tests and record them with `doctor-link record`.")
    for assertion in user_assertions:
        statement = assertion.get("user_statement") if isinstance(assertion, dict) else None
        if statement:
            result.tests_to_rerun.append(f"Rerun a test that verifies user assertion: {statement}")


def _assess_status(result: VerificationResult) -> None:
    if result.report_comparison_status == "not_verified":
        result.status = "not_verified"
        result.notes.append("Report comparison says the fix is not verified.")
        return
    if result.missing_evidence:
        result.status = "missing_evidence"
        result.notes.append("Verification is blocked by missing evidence.")
        return
    if result.report_comparison_status == "candidate_verified":
        result.status = "candidate_verified"
        result.notes.append("Report comparison is candidate_verified; human review and test evidence should confirm final acceptance.")
        return
    if result.test_record_count > 0 and result.checklist_present:
        result.status = "ready"
        result.notes.append("Verification inputs are present. Review test records and checklist before closing.")
        return
    result.status = "needs_review"
    result.notes.append("Verification needs manual review.")


def _add_next_commands(result: VerificationResult, package_dir: Path) -> None:
    if "test_records" in result.missing_evidence:
        result.next_commands.append(
            f"doctor-link record {package_dir} --name \"Verification test\" --status passed --expected \"Expected behavior\" --actual \"Actual behavior\""
        )
    if "report_comparison" in result.missing_evidence:
        result.next_commands.append(
            f"doctor-link compare before-doctor-report.json {package_dir / 'doctor-report.json'} --package-dir {package_dir}"
        )
    result.next_commands.append(f"doctor-link doctor-package {package_dir} --out DoctorReports/package.zip")


def _write_outputs(package_dir: Path, result: VerificationResult) -> None:
    (package_dir / "verification-result.json").write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (package_dir / "verification-plan.md").write_text(result.to_markdown(), encoding="utf-8")


def _write_back(package_dir: Path, report: dict[str, Any], result: VerificationResult) -> None:
    report["verification_result"] = result.to_dict()
    ai_task = report.setdefault("ai_task", {})
    ai_task.setdefault("verification_steps", []).extend(result.next_commands)
    if result.status in {"missing_evidence", "not_verified"}:
        ai_task.setdefault("requested_work", []).append("Resolve verification blockers before marking the fix complete.")
    (package_dir / "doctor-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    _append(
        package_dir / "summary.md",
        f"\n## Verification runner result\n\n- Status: `{result.status}`\n- Summary: {result.summary}\n",
    )
    _append(
        package_dir / "ai-task.md",
        "\n".join(
            [
                "\n## Verification runner result",
                "",
                f"- Status: `{result.status}`",
                f"- Summary: {result.summary}",
                "- Boundary: Do not claim final verification unless evidence and human review support it.",
                "",
            ]
        ),
    )


def _read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _comparison_status(report_comparison: Any) -> str | None:
    if isinstance(report_comparison, dict):
        return report_comparison.get("status")
    return None


def _vly_status(vly_core_proof: Any) -> str | None:
    if isinstance(vly_core_proof, dict):
        return vly_core_proof.get("go_no_go")
    return None


def _summary(result: VerificationResult) -> str:
    return (
        f"Status {result.status}. Missing evidence: {len(result.missing_evidence)}. "
        f"Tests to rerun: {len(result.tests_to_rerun)}. "
        f"Report comparison: {result.report_comparison_status or 'N/A'}."
    )


def _append(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(current.rstrip() + "\n" + text.lstrip("\n"), encoding="utf-8")


def _list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]
