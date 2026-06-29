from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.ai_handoff import SUPPORTED_TOOLS
from doctor_link.core.friendly_errors import friendly_path_error
from doctor_link.diagnose_report import build_report
from doctor_link.diagnose_workflow import files_for_report, run_diagnose_workflow
from doctor_link.p4_cli import main


@main.command("diagnose-now")
@click.argument("library", default=".", required=False)
@click.option("--summary", default=None, help="Short problem description.")
@click.option("--json", "json_output", is_flag=True)
@click.option("--report-json", is_flag=True)
@click.option("--output", "output", type=click.Path(file_okay=False, path_type=str), default=None)
@click.option("--full", is_flag=True, help="Run the full diagnostic workflow (report, collect, verify, view).")
@click.option("--handoff", is_flag=True, help="Generate an AI handoff package (implies --full).")
@click.option("--tool", default="cursor", show_default=True, type=click.Choice(sorted(SUPPORTED_TOOLS)), help="AI handoff tool profile when --handoff is set.")
@click.option("--no-collect", is_flag=True, help="Skip automatic evidence collection in full workflow.")
@click.option("--reports", "reports_dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="DoctorReports output directory for --full.")
def diagnose_now_command(
    library: str,
    summary: str | None,
    json_output: bool,
    report_json: bool,
    output: str | None,
    full: bool,
    handoff: bool,
    tool: str,
    no_collect: bool,
    reports_dir: Path | None,
) -> None:
    """Quick scan or full guided diagnosis for a project folder."""
    library_path = Path(library).expanduser().resolve()
    if not library_path.exists() or not library_path.is_dir():
        raise friendly_path_error(library_path, kind="folder")

    output_path = Path(output).resolve() if output else None
    run_full = full or handoff

    if run_full:
        result = run_diagnose_workflow(
            library_path,
            output=output_path,
            summary=summary,
            reports_dir=reports_dir,
            collect_evidence=not no_collect,
            handoff=handoff,
            handoff_tool=tool,
            quick_scan=True,
            full_pipeline=True,
        )
        if report_json:
            payload = result.to_dict()
            payload["report"] = build_report(files_for_report(library_path, output_path))
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        elif json_output:
            click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            click.echo("Diagnostic workflow complete.")
            for step in result.next_steps:
                click.echo(step)
        return

    from doctor_link.diagnose_now import diagnose_now as write_quick_summary

    summary_path = write_quick_summary(library_path, output_path)
    if report_json:
        report = build_report(files_for_report(library_path, output_path))
        click.echo(json.dumps({"summary": str(summary_path), "report": report}, ensure_ascii=False, indent=2))
    elif json_output:
        click.echo(json.dumps({"summary": str(summary_path)}))
    else:
        click.echo(str(summary_path))
        click.echo("Tip: add --full to generate a complete diagnostic package and HTML report.")
