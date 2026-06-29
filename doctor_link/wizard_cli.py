from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.ai_handoff import DEFAULT_HANDOFF_TOOL, SUPPORTED_TOOLS
from doctor_link.core.friendly_errors import friendly_path_error
from doctor_link.diagnose_workflow import run_diagnose_workflow
from doctor_link.p4_cli import main


@main.command("wizard")
@click.option("--folder", "folder", type=click.Path(file_okay=False, path_type=Path), default=None, help="Project folder to inspect.")
@click.option("--summary", default=None, help="Short problem description.")
@click.option("--tool", default=None, type=click.Choice(sorted(SUPPORTED_TOOLS)), help="AI handoff tool profile when generating a handoff package.")
@click.option("--collect-evidence/--no-collect-evidence", default=None, help="Collect logs and environment evidence (skips prompt when set).")
@click.option("--handoff/--no-handoff", default=None, help="Generate an AI handoff package (skips prompt when set).")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def wizard_command(
    folder: Path | None,
    summary: str | None,
    tool: str | None,
    collect_evidence: bool | None,
    handoff: bool | None,
    json_output: bool,
) -> None:
    """Run an interactive guided diagnosis workflow."""
    if folder is None:
        folder = Path(click.prompt("Which folder should Doctor link inspect?", default=".")).expanduser()
    folder = folder.resolve()
    if not folder.exists() or not folder.is_dir():
        raise friendly_path_error(folder, kind="folder")

    if summary is None:
        summary = click.prompt("What problem are you trying to diagnose?", default="").strip() or None

    if collect_evidence is None:
        collect_evidence = click.confirm("Collect logs and environment evidence automatically?", default=True)
    build_handoff = handoff if handoff is not None else click.confirm(
        "Generate an AI handoff package for an AI coding tool?",
        default=True,
    )

    handoff_tool = DEFAULT_HANDOFF_TOOL
    if build_handoff:
        if tool is None:
            handoff_tool = click.prompt(
                "Which AI tool profile should the handoff package target?",
                default=DEFAULT_HANDOFF_TOOL,
                type=click.Choice(sorted(SUPPORTED_TOOLS)),
            )
        else:
            handoff_tool = tool

    result = run_diagnose_workflow(
        folder,
        summary=summary,
        collect_evidence=collect_evidence,
        handoff=build_handoff,
        handoff_tool=handoff_tool,
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