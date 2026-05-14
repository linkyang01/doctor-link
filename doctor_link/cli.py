from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.ai_task_generator import generate_ai_task
from doctor_link.core.environment_collector import collect_environment
from doctor_link.core.media_probe import probe_media, summarize_media_probe
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.package_exporter import PackageExportOptions, export_package
from doctor_link.core.report_comparator import write_report_comparison, write_report_comparison_to_package
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.report_generator import generate_basic_report
from doctor_link.core.test_recorder import record_test_result
from doctor_link.core.user_assertion_manager import add_user_assertion
from doctor_link.core.vly_adapter import build_vly_core_proof_matrix, write_vly_core_proof_to_package


@click.group()
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


@main.command()
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def report(library: Path, output: Path) -> None:
    """Generate a standard Doctor link diagnostic package."""
    output.mkdir(parents=True, exist_ok=True)
    scan_result = scan_library(library)
    test_plan = generate_test_plan(scan_result)
    event = event_from_scan(scan_result, test_plan, project="Doctor link")
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
@click.option("--note", "user_note", default=None, help="Human note for this test result.")
@click.option("--file", "related_file", default=None, help="Related file or test sample.")
def record_command(
    package_dir: Path,
    name: str,
    status: str,
    expected_behavior: str | None,
    actual_behavior: str | None,
    evidence_ids: tuple[str, ...],
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
    if package_dir is not None:
        evidence = write_vly_core_proof_to_package(package_dir, report)
        click.echo(f"Recorded Vly Core Proof evidence: {evidence.evidence_id}")
    text = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) if json_output else report.to_markdown()
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        click.echo(f"Generated Vly Core Proof report: {output}")
    elif package_dir is None:
        click.echo(text)


@main.command("compare")
@click.argument("before_report", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("after_report", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=Path("DoctorReports/comparison"), help="Output directory for comparison files.")
@click.option("--package-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None, help="Optional after diagnostic package to update with comparison evidence.")
def compare_reports(before_report: Path, after_report: Path, output: Path, package_dir: Path | None) -> None:
    """Compare before and after doctor-report.json files."""
    comparison = write_report_comparison(before_report, after_report, output)
    click.echo(f"Generated report comparison: {output}")
    click.echo(f"Verification status: {comparison.status}")
    if package_dir is not None:
        evidence = write_report_comparison_to_package(before_report, package_dir)
        click.echo(f"Recorded report comparison evidence: {evidence.evidence_id}")


@main.command("doctor-package")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(path_type=Path), default=None, help="Output zip path.")
@click.option("--exclude-attachments", is_flag=True, help="Exclude evidence/attachments from the zip.")
@click.option("--exclude-logs", is_flag=True, help="Exclude evidence/logs from the zip.")
@click.option("--exclude-screenshots", is_flag=True, help="Exclude evidence/screenshots from the zip.")
@click.option("--max-file-size", type=int, default=None, help="Skip files larger than this size in bytes.")
def doctor_package(
    package_dir: Path,
    output: Path | None,
    exclude_attachments: bool,
    exclude_logs: bool,
    exclude_screenshots: bool,
    max_file_size: int | None,
) -> None:
    """Export a diagnostic package as a zip handoff package."""
    result = export_package(
        package_dir=package_dir,
        output_zip=output,
        options=PackageExportOptions(
            exclude_attachments=exclude_attachments,
            exclude_logs=exclude_logs,
            exclude_screenshots=exclude_screenshots,
            max_file_size=max_file_size,
        ),
    )
    click.echo(f"Generated diagnostic package zip: {result.output_zip}")
    click.echo(f"Included files: {len(result.included_files)}")
    click.echo(f"Skipped files: {len(result.skipped_files)}")
    if not result.validation.is_valid:
        click.echo("Warning: diagnostic package is missing required files.")


@main.command("assert")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--statement", required=True, help="Human-confirmed problem statement.")
@click.option("--expected", "expected_behavior", default=None, help="Expected behavior.")
@click.option("--actual", "actual_behavior", default=None, help="Actual behavior.")
@click.option("--why", "why_user_thinks_it_is_wrong", default=None, help="Why the user believes this is wrong.")
@click.option("--severity", default="error", show_default=True, help="Assertion severity.")
@click.option("--file", "related_file", default=None, help="Related file or artifact.")
@click.option("--next-ai", "next_ai_instruction", default=None, help="Instruction for the next AI debugging pass.")
def assert_problem(
    package_dir: Path,
    statement: str,
    expected_behavior: str | None,
    actual_behavior: str | None,
    why_user_thinks_it_is_wrong: str | None,
    severity: str,
    related_file: str | None,
    next_ai_instruction: str | None,
) -> None:
    """Add a human-confirmed problem to a diagnostic package."""
    assertion = add_user_assertion(
        package_dir=package_dir,
        user_statement=statement,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        why_user_thinks_it_is_wrong=why_user_thinks_it_is_wrong,
        severity=severity,
        related_file=related_file,
        next_ai_instruction=next_ai_instruction,
    )
    click.echo(f"Added user assertion: {assertion.assertion_id}")


if __name__ == "__main__":
    main()
