from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.ai_handoff import (
    SUPPORTED_TOOLS,
    add_ai_result,
    add_history_round,
    build_assertion_compliance,
    build_risk_review,
)
from doctor_link.core.ai_task_generator import generate_ai_task
from doctor_link.core.collector import collect_into_package
from doctor_link.core.config_loader import load_config, merge_collect_cli, merge_verify_cli
from doctor_link.core.environment_collector import collect_environment
from doctor_link.core.media_probe import probe_media, summarize_media_probe
from doctor_link import __version__
from doctor_link.core.diagnosis_strategy import load_diagnosis_strategy, project_context_from_library
from doctor_link.core.friendly_errors import friendly_path_error, wrap_io_error
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.package_exporter import PackageExportOptions, export_package
from doctor_link.core.preflight import run_preflight
from doctor_link.core.redactor import RedactionOptions
from doctor_link.core.report_comparator import write_report_comparison, write_report_comparison_to_package
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.report_generator import generate_basic_report
from doctor_link.core.test_recorder import record_test_result
from doctor_link.core.user_assertion_manager import add_user_assertion
from doctor_link.core.verification_runner import run_verification
from doctor_link.core.vly_adapter import build_vly_core_proof_matrix, write_vly_core_proof_to_package
from doctor_link.core.web_server import build_web_view, serve_web_view
from doctor_link.core.workbench_writeback import append_workbench_note


@click.group()
@click.version_option(version=__version__, prog_name="doctor-link")
def main() -> None:
    """Doctor link: diagnostic and AI collaboration CLI."""


@main.command()
@click.argument("workspace", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorWorkspace"), required=False)
def init(workspace: Path) -> None:
    """Create a diagnostic workspace."""
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "reports").mkdir(exist_ok=True)
    (workspace / "evidence").mkdir(exist_ok=True)
    (workspace / "test-results").mkdir(exist_ok=True)
    click.echo(f"Doctor link workspace created: {workspace}")


@main.command()
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
def scan(library: Path) -> None:
    """Scan a test library and print detected files."""
    result = scan_library(library)
    click.echo(f"Scanned: {library}")
    click.echo(f"Total files: {len(result.files)}")
    for item in result.files:
        click.echo(f"- {item.relative_path} ({item.size_bytes} bytes)")


@main.command()
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
def plan(library: Path) -> None:
    """Generate a basic test plan from a test library."""
    scan_result = scan_library(library)
    test_plan = generate_test_plan(scan_result)
    click.echo(test_plan.to_markdown())


@main.command("preflight")
@click.argument("project_root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def preflight_command(project_root: Path, json_output: bool) -> None:
    """Inspect project readiness without executing configured commands."""
    report = run_preflight(project_root)
    if json_output:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(report.to_markdown())
    if report.status == "blocked":
        raise click.ClickException("Preflight checks are blocked.")


@main.command()
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def report(library: Path, output: Path) -> None:
    """Generate a standard Doctor link diagnostic package."""
    if not library.exists() or not library.is_dir():
        raise friendly_path_error(library, kind="folder")
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise wrap_io_error(exc, output) from exc
    project, strategy = project_context_from_library(library)
    scan_result = scan_library(library)
    test_plan = generate_test_plan(scan_result)
    event = event_from_scan(scan_result, test_plan, project=project, strategy=strategy)
    package = build_diagnostic_package(event, output)
    click.echo(f"Generated diagnostic package: {package.root_dir}")


@main.command("legacy-report")
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def legacy_report(library: Path, output: Path) -> None:
    """Generate the original basic Markdown and JSON report."""
    output.mkdir(parents=True, exist_ok=True)
    scan_result = scan_library(library)
    test_plan = generate_test_plan(scan_result)
    report_paths = generate_basic_report(scan_result, test_plan, output)
    for path in report_paths:
        click.echo(f"Generated: {path}")


@main.command("ai-task")
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def ai_task(library: Path, output: Path) -> None:
    """Generate an AI-ready debugging task draft."""
    output.mkdir(parents=True, exist_ok=True)
    scan_result = scan_library(library)
    test_plan = generate_test_plan(scan_result)
    path = generate_ai_task(scan_result, test_plan, output)
    click.echo(f"Generated: {path}")


@main.command("env")
@click.option("--project-root", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional project root to include.")
@click.option("--out", "output", type=click.Path(path_type=Path), default=None, help="Optional JSON output path.")
def env_command(project_root: Path | None, output: Path | None) -> None:
    """Collect local environment evidence."""
    payload = collect_environment(project_root)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        click.echo(f"Generated environment evidence: {output}")
    else:
        click.echo(text)


@main.command("probe")
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--ffprobe", "ffprobe_binary", default="ffprobe", show_default=True, help="ffprobe executable.")
@click.option("--out", "output", type=click.Path(path_type=Path), default=None, help="Optional JSON output path.")
@click.option("--summary", "summary_only", is_flag=True, help="Print or write compact probe summary only.")
def probe_command(file: Path, ffprobe_binary: str, output: Path | None, summary_only: bool) -> None:
    """Probe a media file and return structured evidence."""
    payload = probe_media(file, ffprobe_binary=ffprobe_binary)
    if summary_only:
        payload = summarize_media_probe(payload)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        click.echo(f"Generated media probe evidence: {output}")
    else:
        click.echo(text)


@main.command("record")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--name", required=True, help="Test name.")
@click.option("--status", default="unknown", show_default=True, type=click.Choice(["passed", "failed", "partial", "unknown"]), help="Test result status.")
@click.option("--expected", "expected_behavior", default=None, help="Expected behavior.")
@click.option("--actual", "actual_behavior", default=None, help="Actual behavior.")
@click.option("--evidence-id", "evidence_ids", multiple=True, help="Related evidence ID. Can be repeated.")
@click.option("--assertion-id", "related_assertion_ids", multiple=True, help="Related user assertion ID. Can be repeated.")
@click.option("--note", "user_note", default=None, help="Human note for this test result.")
@click.option("--file", "related_file", default=None, help="Related file or test sample.")
def record_command(
    package_dir: Path,
    name: str,
    status: str,
    expected_behavior: str | None,
    actual_behavior: str | None,
    evidence_ids: tuple[str, ...],
    related_assertion_ids: tuple[str, ...],
    user_note: str | None,
    related_file: str | None,
) -> None:
    """Record a test result into a diagnostic package."""
    record = record_test_result(
        package_dir=package_dir,
        name=name,
        status=status,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        evidence_ids=list(evidence_ids),
        related_assertion_ids=list(related_assertion_ids),
        user_note=user_note,
        related_file=related_file,
    )
    click.echo(f"Recorded test result: {record.test_id}")


@main.command("vly-proof")
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=None, help="Optional report output path.")
@click.option("--json", "json_output", is_flag=True, help="Print or write JSON instead of Markdown.")
@click.option("--package-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None, help="Optional diagnostic package to update with this proof as evidence.")
def vly_proof(library: Path, output: Path | None, json_output: bool, package_dir: Path | None) -> None:
    """Build a Vly Core Proof readiness report from a test library."""
    scan_result = scan_library(library)
    report = build_vly_core_proof_matrix(scan_result)
    text = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) if json_output else report.to_markdown()
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        click.echo(f"Generated Vly proof report: {output}")
    else:
        click.echo(text)
    if package_dir is not None:
        write_vly_core_proof_to_package(package_dir, report)
        click.echo(f"Attached Vly proof evidence to package: {package_dir}")


@main.command("collect")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--project-root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None, help="Optional project root for relative log patterns.")
@click.option("--log", "--logs", "log_patterns", multiple=True, help="Log glob pattern. Can be repeated.")
@click.option("--command", "commands", multiple=True, help="Shell command to capture. Can be repeated.")
@click.option("--probe", "probes", multiple=True, type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Media file to probe. Can be repeated.")
@click.option("--attach", "--attachment", "attachments", multiple=True, type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Attachment file to copy into evidence. Can be repeated.")
@click.option("--note", default=None, help="Collector note.")
@click.option("--redact", is_flag=True, help="Enable redaction for collected text evidence.")
@click.option("--redact-email", is_flag=True, help="Redact email addresses when redaction is enabled.")
@click.option("--redact-phone", is_flag=True, help="Redact phone numbers when redaction is enabled.")
@click.option("--redact-pattern", "redact_patterns", multiple=True, help="Custom redaction regex pattern. Can be repeated.")
def collect_command(
    package_dir: Path,
    project_root: Path | None,
    log_patterns: tuple[str, ...],
    commands: tuple[str, ...],
    probes: tuple[Path, ...],
    attachments: tuple[Path, ...],
    note: str | None,
    redact: bool,
    redact_email: bool,
    redact_phone: bool,
    redact_patterns: tuple[str, ...],
) -> None:
    """Collect evidence into a diagnostic package."""
    config = load_config(project_root or package_dir.parent)
    merged = merge_collect_cli(
        config.collect,
        project_root=project_root,
        log_patterns=list(log_patterns),
        commands=list(commands),
        probes=list(probes),
        attachments=list(attachments),
        redact=True if redact else None,
        redact_email=redact_email,
        redact_phone=redact_phone,
        custom_patterns=list(redact_patterns),
    )
    config_root = Path(config.root_dir)
    effective_root = _resolve_collect_root(project_root, merged.project_root, config_root)
    result = collect_into_package(
        package_dir=package_dir,
        project_root=effective_root,
        log_patterns=[_resolve_pattern(item, effective_root) for item in merged.logs],
        commands=merged.commands,
        probes=[_resolve_local_path(item, effective_root) for item in merged.probes],
        attachments=[_resolve_local_path(item, effective_root) for item in merged.attachments],
        note=note,
        redact=merged.redact,
        redaction_options=RedactionOptions(
            redact_email=merged.redact_email,
            redact_phone=merged.redact_phone,
            custom_patterns=merged.redact_patterns,
        ),
    )
    click.echo(f"Collected evidence into package: {package_dir}")
    click.echo(f"Evidence items added: {len(result.evidence)}")


@main.command("assert")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--statement", required=True, help="Human-confirmed issue statement.")
@click.option("--severity", default="medium", show_default=True, help="Issue severity.")
@click.option("--evidence-id", "evidence_ids", multiple=True, help="Related evidence ID. Can be repeated.")
@click.option("--expected", "expected_behavior", default=None, help="Expected behavior.")
@click.option("--actual", "actual_behavior", default=None, help="Actual behavior.")
@click.option("--why-wrong", default=None, help="Why the current behavior is considered wrong.")
@click.option("--file", "related_file", default=None, help="Related file path.")
@click.option("--next-ai", "next_ai_instruction", default=None, help="Instruction for the next AI repair pass.")
def assert_command(
    package_dir: Path,
    statement: str,
    severity: str,
    evidence_ids: tuple[str, ...],
    expected_behavior: str | None,
    actual_behavior: str | None,
    why_wrong: str | None,
    related_file: str | None,
    next_ai_instruction: str | None,
) -> None:
    """Add a human-confirmed issue assertion to a diagnostic package."""
    assertion = add_user_assertion(
        package_dir=package_dir,
        user_statement=statement,
        severity=severity,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        why_user_thinks_it_is_wrong=why_wrong,
        related_file=related_file,
        next_ai_instruction=next_ai_instruction,
        related_evidence_ids=list(evidence_ids),
    )
    click.echo(f"Added user assertion: {assertion.assertion_id}")


@main.command("verify")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--write-back", is_flag=True, help="Write verification results back into the package.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def verify_command(package_dir: Path, write_back: bool, json_output: bool) -> None:
    """Run verification planning for a diagnostic package."""
    config = load_config(package_dir.parent)
    merged = merge_verify_cli(config.verification, write_back=write_back)
    result = run_verification(package_dir, write_back=write_back, config=merged)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Verification status: {result.status}")
    if result.missing_evidence:
        click.echo("Missing evidence:")
        for item in result.missing_evidence:
            click.echo(f"  - {item}")
    if result.next_commands:
        click.echo("Next commands:")
        for item in result.next_commands:
            click.echo(f"  - {item}")


@main.command("compare")
@click.argument("before", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("after", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--package-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None, help="Optional package to write comparison results into.")
@click.option("--out", "output", type=click.Path(path_type=Path), default=None, help="Optional output directory.")
def compare_command(before: Path, after: Path, package_dir: Path | None, output: Path | None) -> None:
    """Compare two diagnostic reports."""
    if package_dir is not None:
        evidence = write_report_comparison_to_package(before, package_dir)
        click.echo(f"Generated comparison evidence: {evidence.path}")
        return
    output_dir = output or Path("DoctorReports")
    write_report_comparison(before, after, output_dir)
    click.echo(f"Generated: {output_dir / 'report-comparison.json'}")
    click.echo(f"Generated: {output_dir / 'report-comparison.md'}")


@main.command("doctor-package")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), required=True, help="Output zip path.")
@click.option("--include-web", is_flag=True, help="Include generated web view assets if present.")
def doctor_package_command(package_dir: Path, output: Path, include_web: bool) -> None:
    """Export a diagnostic package archive."""
    options = PackageExportOptions(include_web_assets=include_web)
    path = export_package(package_dir, output, options=options)
    click.echo(f"Exported diagnostic package: {path}")


@main.command("view")
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--build-only", is_flag=True, help="Build the local HTML workbench without starting a server.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Server host when not using --build-only.")
@click.option("--port", default=8765, show_default=True, type=int, help="Server port when not using --build-only.")
def view_command(target: Path, build_only: bool, host: str, port: int) -> None:
    """Build or serve the local diagnostic workbench."""
    if build_only:
        result = build_web_view(target)
        click.echo(f"Built local workbench: {result.index_path}")
        return
    serve_web_view(target, host=host, port=port)


@main.command("workbench-note")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--note", required=True, help="Workbench note to append.")
@click.option("--enable-write-back", is_flag=True, help="Enable controlled write-back with backup and audit.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def workbench_note_command(package_dir: Path, note: str, enable_write_back: bool, json_output: bool) -> None:
    """Append a workbench note to a diagnostic package."""
    result = append_workbench_note(package_dir, note=note, enable_write_back=enable_write_back)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    if result.wrote:
        click.echo(f"Appended workbench note: {result.target_file}")
    else:
        click.echo("Write-back disabled; no note was written.")


@main.command("ai-result")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--summary", required=True, help="AI repair summary.")
@click.option("--claimed-fix", default="No claimed fix provided; verification required.", show_default=True, help="Claimed fix description.")
@click.option("--tool", default=None, type=click.Choice(sorted(SUPPORTED_TOOLS)), help="AI tool profile.")
@click.option("--repair-session-id", default=None, help="Optional repair session ID.")
@click.option("--file", "files_changed", multiple=True, help="Changed file path. Can be repeated.")
@click.option("--evidence-id", "evidence_used", multiple=True, help="Evidence ID cited by AI. Can be repeated.")
@click.option("--assertion-id", "related_assertion_ids", multiple=True, help="Related assertion ID. Can be repeated.")
@click.option("--verification-step", "verification_steps", multiple=True, help="Verification step. Can be repeated.")
@click.option("--risk", "risks", multiple=True, help="Risk note. Can be repeated.")
@click.option("--assumption", "assumptions", multiple=True, help="Assumption note. Can be repeated.")
def ai_result_command(
    package_dir: Path,
    summary: str,
    claimed_fix: str,
    tool: str | None,
    repair_session_id: str | None,
    files_changed: tuple[str, ...],
    evidence_used: tuple[str, ...],
    related_assertion_ids: tuple[str, ...],
    verification_steps: tuple[str, ...],
    risks: tuple[str, ...],
    assumptions: tuple[str, ...],
) -> None:
    """Record an AI repair result into a diagnostic package."""
    result = add_ai_result(
        package_dir,
        summary=summary,
        claimed_fix=claimed_fix,
        tool=tool or "generic",
        repair_session_id=repair_session_id,
        files_changed=list(files_changed),
        evidence_used=list(evidence_used),
        related_assertion_ids=list(related_assertion_ids),
        verification_steps=list(verification_steps),
        risks=list(risks),
        assumptions=list(assumptions),
    )
    click.echo(f"Recorded AI result: {result['result_id']}")
    if result.get("repair_session_id"):
        click.echo(f"Repair session: {result['repair_session_id']}")


@main.command("diagnosis-history")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--ai-pass", required=True, help="AI pass summary.")
@click.option("--user-correction", default=None, help="Optional user correction.")
@click.option("--tool", default=None, type=click.Choice(sorted(SUPPORTED_TOOLS)), help="AI tool profile.")
@click.option("--repair-session-id", default=None, help="Optional repair session ID.")
@click.option("--evidence-id", "evidence_added", multiple=True, help="Evidence added in this round. Can be repeated.")
@click.option("--verification-attempt", default=None, help="Verification attempt summary.")
def diagnosis_history_command(
    package_dir: Path,
    ai_pass: str,
    user_correction: str | None,
    tool: str | None,
    repair_session_id: str | None,
    evidence_added: tuple[str, ...],
    verification_attempt: str | None,
) -> None:
    """Record a diagnosis history round."""
    result = add_history_round(
        package_dir,
        ai_pass=ai_pass,
        user_correction=user_correction,
        tool=tool or "generic",
        repair_session_id=repair_session_id,
        evidence_added=list(evidence_added),
        verification_attempt=verification_attempt,
    )
    click.echo(f"Recorded diagnosis round: {result['round_id']}")
    if result.get("repair_session_id"):
        click.echo(f"Repair session: {result['repair_session_id']}")


@main.command("assertion-check")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def assertion_check_command(package_dir: Path, json_output: bool) -> None:
    """Build an assertion compliance report."""
    report = build_assertion_compliance(package_dir)
    if json_output:
        click.echo(json.dumps(report, ensure_ascii=False, indent=2))
        return
    click.echo(f"Assertion compliance status: {report.get('summary', 'needs_review')}")


@main.command("risk-review")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--file", "files_changed", multiple=True, help="Changed file path. Can be repeated.")
@click.option("--boundary", "boundary", multiple=True, help="Investigation boundary path prefix. Can be repeated.")
def risk_review_command(package_dir: Path, files_changed: tuple[str, ...], boundary: tuple[str, ...]) -> None:
    """Build a repair risk review report."""
    report = build_risk_review(package_dir, files_changed=list(files_changed), boundary=list(boundary))
    click.echo(f"Repair risk level: {report['risk_level']}")
    click.echo(f"Risks listed: {len(report.get('risks', []))}")


@main.group("strategy")
def strategy_group() -> None:
    """Inspect and validate diagnosis strategy configuration."""


@strategy_group.command("validate")
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def strategy_validate(library: Path, json_output: bool) -> None:
    """Validate .doctorlink/diagnosis.yml for a project."""
    result = load_diagnosis_strategy(library)
    payload = result.to_dict()
    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        click.echo(result.to_markdown())
    if not result.is_valid:
        raise click.ClickException("Strategy validation failed.")


def _resolve_collect_root(explicit: Path | None, configured: str | None, config_root: Path) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    if configured:
        candidate = Path(configured).expanduser()
        return (candidate if candidate.is_absolute() else config_root / candidate).resolve()
    return config_root.resolve()


def _resolve_local_path(value: str, project_root: Path) -> Path:
    candidate = Path(value).expanduser()
    return (candidate if candidate.is_absolute() else project_root / candidate).resolve()


def _resolve_pattern(value: str, project_root: Path) -> str:
    candidate = Path(value).expanduser()
    return str(candidate if candidate.is_absolute() else project_root / candidate)


if __name__ == "__main__":
    main()
