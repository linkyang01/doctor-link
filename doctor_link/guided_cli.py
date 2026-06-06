from __future__ import annotations

from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.guided_workflow import (
    GuidedWorkflowOptions,
    build_home_page,
    format_guided_result,
    result_to_json,
    run_guided_diagnosis,
)


@main.command("diagnose-now")
@click.argument("project_folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--summary", required=True, help="Plain-language problem summary.")
@click.option("--out", "out_dir", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), show_default=True, help="Output directory for diagnostic reports.")
@click.option("--tool", default="generic", show_default=True, help="AI handoff tool profile.")
@click.option("--no-handoff", is_flag=True, help="Skip AI handoff generation.")
@click.option("--no-view", is_flag=True, help="Skip local HTML report generation.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def diagnose_now(project_folder: Path, summary: str, out_dir: Path, tool: str, no_handoff: bool, no_view: bool, json_output: bool) -> None:
    """Run the no-code guided diagnosis workflow in one command."""
    try:
        result = run_guided_diagnosis(
            GuidedWorkflowOptions(
                project_folder=project_folder,
                summary=summary,
                out_dir=out_dir,
                tool=tool,
                create_handoff=not no_handoff,
                build_view=not no_view,
            )
        )
    except ValueError as exc:
        raise click.ClickException(_friendly_error(str(exc))) from exc

    if json_output:
        click.echo(result_to_json(result))
        return
    click.echo(format_guided_result(result))


@main.command("wizard")
@click.option("--project-folder", type=click.Path(file_okay=False, path_type=Path), default=None, help="Project folder to diagnose. If omitted, the wizard asks for it.")
@click.option("--summary", default=None, help="Problem summary. If omitted, the wizard asks for it.")
@click.option("--out", "out_dir", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), show_default=True, help="Output directory for diagnostic reports.")
@click.option("--tool", default="generic", show_default=True, help="AI handoff tool profile.")
@click.option("--skip-handoff", is_flag=True, help="Skip AI handoff generation.")
@click.option("--skip-view", is_flag=True, help="Skip local HTML report generation.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def wizard(project_folder: Path | None, summary: str | None, out_dir: Path, tool: str, skip_handoff: bool, skip_view: bool, json_output: bool) -> None:
    """Start a plain-language guided diagnosis wizard."""
    folder = project_folder
    if folder is None:
        folder = Path(click.prompt("Project folder to diagnose", default="."))
    problem = summary
    if problem is None:
        problem = click.prompt("Describe the problem in one sentence")

    create_handoff = not skip_handoff
    build_view = not skip_view
    if not json_output:
        create_handoff = click.confirm("Generate an AI handoff package?", default=create_handoff)
        build_view = click.confirm("Build a local HTML report?", default=build_view)

    try:
        result = run_guided_diagnosis(
            GuidedWorkflowOptions(
                project_folder=folder,
                summary=problem,
                out_dir=out_dir,
                tool=tool,
                create_handoff=create_handoff,
                build_view=build_view,
            )
        )
    except ValueError as exc:
        raise click.ClickException(_friendly_error(str(exc))) from exc

    if json_output:
        click.echo(result_to_json(result))
        return
    click.echo(format_guided_result(result))


@main.command("home")
@click.argument("reports_root", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), required=False)
@click.option("--out", "output_dir", type=click.Path(file_okay=False, path_type=Path), default=Path(".doctorlink-home"), show_default=True, help="Output directory for the local homepage.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def home(reports_root: Path, output_dir: Path, json_output: bool) -> None:
    """Build a local static home page for reports and no-code guidance."""
    index = build_home_page(reports_root, output_dir=output_dir)
    if json_output:
        click.echo(f'{{"home_page": "{index}"}}')
        return
    click.echo("Doctor link local home page created.")
    click.echo(f"Open: {index}")


def _friendly_error(message: str) -> str:
    if "Project folder not found" in message:
        return f"{message}\nNext step: check the folder path and try again. You can drag the folder into the terminal to copy its path."
    if "not a folder" in message:
        return f"{message}\nNext step: choose a folder, not a single file."
    if "Problem summary is required" in message:
        return f"{message}\nNext step: add --summary \"Describe what is wrong\"."
    return f"{message}\nNext step: run doctor-link --help or read docs/guides/no-code-quick-start.en.md."
