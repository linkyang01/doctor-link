from __future__ import annotations

import json
import webbrowser
from pathlib import Path

import click

from doctor_link.core.guided_assistant import run_guided_session
from doctor_link.p4_cli import main


@main.command("assist")
@click.argument("project_root", required=False, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--problem", default=None, help="Describe what is wrong in ordinary language.")
@click.option("--package", default=None, help="Optional workspace package relative to PROJECT_ROOT.")
@click.option("--out", "output", default=None, type=click.Path(file_okay=False, path_type=Path))
@click.option("--allow-repair", is_flag=True, help="After reproduction, allow an isolated Codex repair.")
@click.option("--open/--no-open", "open_page", default=True, help="Open the local result page in a browser.")
@click.option("--json", "json_output", is_flag=True, help="Print the complete guided-session JSON.")
def assist_command(
    project_root: Path | None,
    problem: str | None,
    package: str | None,
    output: Path | None,
    allow_repair: bool,
    open_page: bool,
    json_output: bool,
) -> None:
    """Describe a problem; Doctor link finds a reproduction and prepares or performs a verified repair."""
    root = project_root or Path(click.prompt("Choose the project folder", default="."))
    clean_problem = (problem or click.prompt("What is going wrong?", default="")).strip()
    if not clean_problem:
        raise click.UsageError("A problem description is required.")
    if not allow_repair and not json_output:
        click.echo("Doctor link will reproduce and prepare a repair preview. It will not edit code.")
    result = run_guided_session(
        root,
        problem=clean_problem,
        package=package,
        output_root=output,
        allow_repair=allow_repair,
    )
    if open_page:
        webbrowser.open(Path(result.result_page).as_uri())
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Guided result: {result.status}")
        click.echo(f"Result page: {result.result_page}")
        for step in result.next_steps:
            click.echo(f"Next: {step}")
    exit_codes = {"verified": 0, "approval_required": 2, "not_reproduced": 3, "blocked": 4, "failed": 5, "review_required": 6}
    if code := exit_codes.get(result.status, 0):
        raise click.exceptions.Exit(code)


__all__ = ["assist_command"]
