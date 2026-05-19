from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.reproduction import load_reproduction_catalog, run_reproduction
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


if __name__ == "__main__":
    main()
