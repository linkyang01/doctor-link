from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.solve import resume_solve_session, solve_project


EXIT_CODES = {
    "verified": 0,
    "approval_required": 2,
    "not_reproduced": 3,
    "blocked": 4,
    "failed": 5,
    "review_required": 6,
    "suggestion_ready": 7,
}

SUPPORTED_REPAIR_TOOLS = ("codex",)


def _validate_repair_tool(_ctx: click.Context, _param: click.Parameter, value: str) -> str:
    """Validate --tool without click.Choice, which can break under pre-release click builds."""
    cleaned = (value or "").strip().casefold()
    if cleaned not in SUPPORTED_REPAIR_TOOLS:
        supported = ", ".join(SUPPORTED_REPAIR_TOOLS)
        raise click.BadParameter(f"Unsupported repair tool {value!r}. Supported tools: {supported}.")
    return cleaned


@main.command("solve")
@click.argument("project_root", required=False, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--problem", required=False, help="Concrete problem Doctor link must reproduce and repair.")
@click.option("--package", default=None, help="Workspace package path relative to PROJECT_ROOT.")
@click.option("--resume", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None, help="Resume an interrupted solve-session directory.")
@click.option("--reproduce-command", default=None, help="Safe command that fails while the problem exists.")
@click.option("--test-command", default=None, help="Safe regression command that must pass after repair.")
@click.option(
    "--tool",
    default="codex",
    show_default=True,
    type=str,
    callback=_validate_repair_tool,
    help="Repair executor.",
)
@click.option(
    "--require-grounded-root-cause",
    is_flag=True,
    help="Block repair unless failing evidence maps to project source with a precise location or production frame.",
)
@click.option("--allow-repair", is_flag=True, help="Explicitly allow branch creation, Codex execution, and code edits.")
@click.option(
    "--suggest-only",
    is_flag=True,
    help="Create a repair branch and produce a structured change proposal without claiming verified.",
)
@click.option(
    "--allow-verification-changes",
    is_flag=True,
    help="Allow protected test/config changes, but require human review instead of returning verified.",
)
@click.option("--max-rounds", default=3, show_default=True, type=click.IntRange(1, 3), help="Maximum repair and verification rounds.")
@click.option("--command-timeout", default=120, show_default=True, type=click.IntRange(1), help="Timeout for each independent check in seconds.")
@click.option("--repair-timeout", default=900, show_default=True, type=click.IntRange(30), help="Timeout for each Codex repair round in seconds.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Solve-session parent directory. Defaults outside the target Git repository.")
@click.option("--json", "json_output", is_flag=True, help="Print the complete solve result as JSON.")
def solve_command(
    project_root: Path | None,
    problem: str | None,
    package: str | None,
    resume: Path | None,
    reproduce_command: str | None,
    test_command: str | None,
    tool: str,
    allow_repair: bool,
    suggest_only: bool,
    allow_verification_changes: bool,
    require_grounded_root_cause: bool,
    max_rounds: int,
    command_timeout: int,
    repair_timeout: int,
    output: Path | None,
    json_output: bool,
) -> None:
    """Reproduce, repair with Codex, and independently verify a Python or Node.js project problem."""
    if resume is not None:
        if project_root is not None or problem is not None or package is not None or reproduce_command or test_command or output:
            raise click.UsageError("--resume cannot be combined with a project, problem, package, commands, or --out.")
        if suggest_only:
            raise click.UsageError("--suggest-only cannot be combined with --resume.")
        result = resume_solve_session(
            resume,
            allow_repair=allow_repair,
            max_rounds=max_rounds,
            command_timeout_seconds=command_timeout,
            repair_timeout_seconds=repair_timeout,
        )
    else:
        if project_root is None or not problem:
            raise click.UsageError("PROJECT_ROOT and --problem are required unless --resume is used.")
        result = solve_project(
            project_root,
            problem=problem,
            reproduce_command=reproduce_command,
            test_command=test_command,
            output_root=output,
            tool=tool,
            allow_repair=allow_repair,
            allow_verification_changes=allow_verification_changes,
            suggest_only=suggest_only,
            require_grounded_root_cause=require_grounded_root_cause,
            max_rounds=max_rounds,
            command_timeout_seconds=command_timeout,
            repair_timeout_seconds=repair_timeout,
            package=package,
        )
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Automatic solve status: {result.status}")
        click.echo(f"Summary: {result.summary}")
        if result.repair_branch:
            click.echo(f"Repair branch: {result.repair_branch}")
        if result.output_dir:
            click.echo(f"Solve session: {result.output_dir}")
        for blocker in result.blockers:
            click.echo(f"Blocker: {blocker}")
        for step in result.next_steps:
            click.echo(f"Next: {step}")
    exit_code = EXIT_CODES.get(result.status, 1)
    if exit_code:
        raise click.exceptions.Exit(exit_code)


__all__ = ["solve_command"]
