from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.conformance import run_conformance_suite, write_conformance_report
from doctor_link.core.diagnosis_pipeline import run_diagnosis_compare, run_diagnosis_verify
from doctor_link.core.diagnosis_workflow import create_after_package, create_before_package
from doctor_link.core.project_health import write_project_health
from doctor_link.core.reproduction import load_reproduction_catalog, run_reproduction
from doctor_link.core.schema_validator import validate_diagnostic_package, write_schema_validation_result
from doctor_link.core.test_matrix_runner import load_test_matrix, run_test_matrix


@main.group("reproduce")
def reproduce_group() -> None:
    """Manage reproduction entries."""


@reproduce_group.command("list")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def reproduce_list(project_root: Path, json_output: bool) -> None:
    """List reproduction entries from .doctorlink/reproduce.yml."""
    catalog = load_reproduction_catalog(project_root)
    if json_output:
        click.echo(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo("# Reproductions")
    for entry in catalog.entries:
        click.echo(f"- {entry.reproduction_id}: {entry.title} ({entry.kind})")
    for warning in catalog.warnings:
        click.echo(f"Warning: {warning}")


@reproduce_group.command("run")
@click.argument("reproduction_id")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--package-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional diagnostic package to receive reproduction evidence.")
@click.option("--timeout", default=60, show_default=True, type=int, help="Command timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def reproduce_run(reproduction_id: str, project_root: Path, package_dir: Path | None, timeout: int, json_output: bool) -> None:
    """Run a command or test reproduction entry."""
    result = run_reproduction(project_root, reproduction_id, package_dir=package_dir, timeout_seconds=timeout)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Reproduction: {result.reproduction_id}")
    click.echo(f"Status: {result.status}")
    if result.evidence_id:
        click.echo(f"Evidence: {result.evidence_id}")


@main.group("test")
def test_group() -> None:
    """Run project test matrix jobs."""


@test_group.command("list")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def test_list(project_root: Path, json_output: bool) -> None:
    """List executable test matrix jobs."""
    catalog = load_test_matrix(project_root)
    if json_output:
        click.echo(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo("# Test Matrix Jobs")
    for job in catalog.jobs:
        click.echo(f"- {job.job_id}: {job.title}")
    for warning in catalog.warnings:
        click.echo(f"Warning: {warning}")


@test_group.command("run")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--job", "job_id", default=None, help="Optional job id to run.")
@click.option("--package-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional diagnostic package to receive test evidence.")
@click.option("--timeout", default=120, show_default=True, type=int, help="Command timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def test_run(project_root: Path, job_id: str | None, package_dir: Path | None, timeout: int, json_output: bool) -> None:
    """Run executable test matrix jobs."""
    results = run_test_matrix(project_root, package_dir=package_dir, job_id=job_id, timeout_seconds=timeout)
    if json_output:
        click.echo(json.dumps([item.to_dict() for item in results], ensure_ascii=False, indent=2))
        return
    for result in results:
        click.echo(f"Test job: {result.job_id}")
        click.echo(f"Status: {result.status}")
        if result.evidence_id:
            click.echo(f"Evidence: {result.evidence_id}")


@main.group("diagnose")
def diagnose_group() -> None:
    """Run before / after diagnosis workflow commands."""


@diagnose_group.command("before")
@click.option("--project", required=True, help="Project name.")
@click.option("--summary", required=True, help="Before-state diagnostic summary.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def diagnose_before(project: str, summary: str, output: Path) -> None:
    """Create a before diagnostic package."""
    package_dir = create_before_package(project=project, summary=summary, output_dir=output)
    click.echo(f"Created before package: {package_dir}")
    click.echo(f"Before report: {package_dir / 'doctor-report.json'}")


@diagnose_group.command("after")
@click.option("--project", required=True, help="Project name.")
@click.option("--summary", required=True, help="After-state diagnostic summary.")
@click.option("--before-package", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True, help="Before diagnostic package.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def diagnose_after(project: str, summary: str, before_package: Path, output: Path) -> None:
    """Create an after diagnostic package linked to a before package."""
    package_dir = create_after_package(project=project, summary=summary, output_dir=output, before_package=before_package)
    click.echo(f"Created after package: {package_dir}")
    click.echo(f"Before report: {before_package / 'doctor-report.json'}")
    click.echo(f"After report: {package_dir / 'doctor-report.json'}")


@diagnose_group.command("compare")
@click.argument("after_package", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def diagnose_compare(after_package: Path, json_output: bool) -> None:
    """Generate comparison summary for an after package."""
    summary = run_diagnosis_compare(after_package)
    if json_output:
        click.echo(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Comparison status: {summary.comparison_status}")
    click.echo(f"Summary: {after_package / 'diagnosis-pipeline-summary.md'}")


@diagnose_group.command("verify")
@click.argument("after_package", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--no-write-back", is_flag=True, help="Do not write verification into report files.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def diagnose_verify(after_package: Path, no_write_back: bool, json_output: bool) -> None:
    """Run automated comparison and verification for an after package."""
    summary = run_diagnosis_verify(after_package, write_back=not no_write_back)
    if json_output:
        click.echo(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Verification status: {summary.verification_status}")
    click.echo(f"Pipeline success: {summary.success}")
    click.echo(f"Summary: {after_package / 'diagnosis-pipeline-summary.md'}")


@main.group("schema")
def schema_group() -> None:
    """Validate diagnostic package schema compatibility."""


@schema_group.command("validate")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--write", "write_result", is_flag=True, help="Write schema-validation-result files into the package.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def schema_validate(package_dir: Path, write_result: bool, json_output: bool) -> None:
    """Validate a diagnostic package against Doctor link schema v1 policy."""
    result = validate_diagnostic_package(package_dir)
    if write_result:
        write_schema_validation_result(package_dir, result)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Schema validation status: {result.status}")
        click.echo(f"Checked files: {len(result.checked_files)}")
        click.echo(f"Findings: {len(result.findings)}")
    if not result.valid:
        raise click.ClickException("Schema validation failed.")


@main.group("conformance")
def conformance_group() -> None:
    """Run schema compatibility conformance suites."""


@conformance_group.command("run")
@click.argument("fixtures_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports/conformance"), help="Output directory.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def conformance_run(fixtures_root: Path, output: Path, json_output: bool) -> None:
    """Run a compatibility and conformance suite."""
    report = run_conformance_suite(fixtures_root)
    write_conformance_report(output, report)
    if json_output:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Conformance status: {report.status}")
        click.echo(f"Compatibility score: {report.compatibility_score}")
        click.echo(f"Report: {output / 'conformance-report.md'}")
    if report.status != "passed":
        raise click.ClickException("Conformance suite failed.")


@main.command("health")
@click.argument("reports_dir", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), required=False)
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional output directory.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def health_command(reports_dir: Path, output: Path | None, json_output: bool) -> None:
    """Generate project health summary from DoctorReports."""
    summary = write_project_health(reports_dir, output_dir=output)
    if json_output:
        click.echo(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
        return
    out = output or reports_dir
    click.echo(f"Project health status: {summary.status}")
    click.echo(f"Summary: {out / 'project-health.md'}")


if __name__ == "__main__":
    main()
