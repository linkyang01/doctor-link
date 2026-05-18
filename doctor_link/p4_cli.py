from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.reproduction import load_reproduction_catalog, run_reproduction


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


if __name__ == "__main__":
    main()
