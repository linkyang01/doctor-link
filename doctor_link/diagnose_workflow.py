from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from doctor_link.core.ai_handoff import build_handoff_package
from doctor_link.core.collector import collect_into_package
from doctor_link.core.config_loader import load_config, merge_collect_cli
from doctor_link.core.diagnosis_strategy import project_context_from_library
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.redactor import RedactionOptions
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.verification_runner import run_verification
from doctor_link.core.web_server import build_web_view
from doctor_link.diagnose_now import diagnose_now as write_quick_summary
@dataclass
class DiagnoseWorkflowResult:
    library: Path
    quick_summary: Path | None = None
    package_dir: Path | None = None
    web_index: Path | None = None
    handoff_dir: Path | None = None
    verification_status: str | None = None
    missing_evidence: list[str] = field(default_factory=list)
    next_commands: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "library": str(self.library),
            "quick_summary": str(self.quick_summary) if self.quick_summary else None,
            "package_dir": str(self.package_dir) if self.package_dir else None,
            "web_index": str(self.web_index) if self.web_index else None,
            "handoff_dir": str(self.handoff_dir) if self.handoff_dir else None,
            "verification_status": self.verification_status,
            "missing_evidence": list(self.missing_evidence),
            "next_commands": list(self.next_commands),
            "next_steps": list(self.next_steps),
        }


def run_diagnose_workflow(
    library: Path,
    *,
    output: Path | None = None,
    summary: str | None = None,
    reports_dir: Path | None = None,
    collect_evidence: bool = True,
    handoff: bool = False,
    handoff_tool: str = "cursor",
    quick_scan: bool = True,
    full_pipeline: bool = True,
) -> DiagnoseWorkflowResult:
    """Run the guided diagnose-now workflow for a project folder."""
    library = library.resolve()
    result = DiagnoseWorkflowResult(library=library)

    if quick_scan:
        result.quick_summary = write_quick_summary(library, output)

    if not full_pipeline:
        result.next_steps.append(f"Open quick summary: {result.quick_summary}")
        result.next_steps.append("Run again with `--full` to generate a complete diagnostic package.")
        return result

    project, strategy = project_context_from_library(library)
    config = load_config(library)
    reports_root = (reports_dir or Path(config.package.output_dir)).resolve()
    if not reports_root.is_absolute():
        reports_root = (library / reports_root).resolve()
    reports_root.mkdir(parents=True, exist_ok=True)

    scan_result = scan_library(library)
    test_plan = generate_test_plan(scan_result)
    event = event_from_scan(scan_result, test_plan, project=project, strategy=strategy, symptom=summary)
    package = build_diagnostic_package(event, reports_root)
    result.package_dir = package.root_dir

    if collect_evidence:
        _collect_evidence(library, package.root_dir, strategy, config.collect)

    verification = run_verification(package.root_dir, write_back=False)
    result.verification_status = verification.status
    result.missing_evidence = list(verification.missing_evidence)
    result.next_commands = list(verification.next_commands)

    web = build_web_view(package.root_dir)
    result.web_index = web.index_path

    if handoff:
        handoff_result = build_handoff_package(package_dir=package.root_dir, tool=handoff_tool)
        result.handoff_dir = handoff_result.output_dir

    result.next_steps = _build_next_steps(result)
    return result


def _collect_evidence(library: Path, package_dir: Path, strategy, collect_config) -> None:
    log_patterns = list(collect_config.logs) or _default_log_patterns(library)
    commands = list(collect_config.commands) or _shell_commands(strategy.default_commands)
    if not log_patterns and not commands:
        return
    merged = merge_collect_cli(collect_config, project_root=library, log_patterns=log_patterns, commands=commands)
    collect_into_package(
        package_dir=package_dir,
        project_root=library,
        log_patterns=merged.logs,
        commands=merged.commands,
        probes=[],
        attachments=[],
        note="Collected automatically by diagnose-now workflow.",
        redact=merged.redact,
        redaction_options=RedactionOptions(
            redact_email=merged.redact_email,
            redact_phone=merged.redact_phone,
            custom_patterns=merged.redact_patterns,
        ),
    )


def _default_log_patterns(library: Path) -> list[str]:
    patterns: list[str] = []
    if (library / "logs").is_dir():
        patterns.append("logs/*.log")
    return patterns


def _shell_commands(commands: list[str]) -> list[str]:
    blocked_prefixes = ("doctor-link ", "doctor_link ")
    return [command for command in commands if not command.strip().startswith(blocked_prefixes)]


def _build_next_steps(result: DiagnoseWorkflowResult) -> list[str]:
    steps: list[str] = []
    if result.web_index:
        steps.append(f"Open the HTML report: {result.web_index}")
    if result.package_dir:
        steps.append(f"Diagnostic package folder: {result.package_dir}")
    if result.handoff_dir:
        steps.append(f"Give this AI handoff folder to your coding tool: {result.handoff_dir}")
    elif result.package_dir:
        steps.append(f"Generate AI handoff: doctor-link handoff {result.package_dir} --tool cursor")
    if result.missing_evidence:
        steps.append(f"Verification status: {result.verification_status} ({len(result.missing_evidence)} missing item(s))")
        for command in result.next_commands[:3]:
            steps.append(f"Run: {command}")
    if result.quick_summary:
        steps.append(f"Quick scan summary: {result.quick_summary}")
    return steps


def files_for_report(library: Path, output: Path | None) -> list[Path]:
    base = library.resolve()
    root = output.resolve() if output is not None else base / ".doctor-link"
    files: list[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if root == resolved or root in resolved.parents:
            continue
        files.append(path)
    return files
