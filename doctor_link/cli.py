from __future__ import annotations

from pathlib import Path

import click

from doctor_link.core.ai_task_generator import generate_ai_task
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.report_generator import generate_basic_report
from doctor_link.core.user_assertion_manager import add_user_assertion


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
