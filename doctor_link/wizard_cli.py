from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.friendly_errors import friendly_path_error
from doctor_link.diagnose_workflow import run_diagnose_workflow
from doctor_link.p4_cli import main


@main.command("wizard")
@click.option("--folder", "folder", type=click.Path(file_okay=False, path_type=Path), default=None, help="Project folder to inspect.")
@click.option("--summary", default=None, help="Short problem description.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def wizard_command(folder: Path | None, summary: str | None, json_output: bool) -> None:
    """Run an interactive guided diagnosis workflow."""
    if folder is None:
        folder = Path(click.prompt("Which folder should Doctor link inspect?", default=".")).expanduser()
    folder = folder.resolve()
    if not folder.exists() or not folder.is_dir():
        raise friendly_path_error(folder, kind="folder")

    if summary is None:
        summary = click.prompt("What problem are you trying to diagnose?", default="").strip() or None

    collect_evidence = click.confirm("Collect logs and environment evidence automatically?", default=True)
    build_handoff = click.confirm("Generate an AI handoff package for Cursor?", default=True)

    result = run_diagnose_workflow(
        folder,
        summary=summary,
        collect_evidence=collect_evidence,
        handoff=build_handoff,
        handoff_tool="cursor",
        quick_scan=True,
        full_pipeline=True,
    )

    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    click.echo("")
    click.echo("Diagnostic workflow complete.")
    for step in result.next_steps:
        click.echo(f"- {step}")