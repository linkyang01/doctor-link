from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.diagnose_now import diagnose_now as run
from doctor_link.diagnose_report import build_report
from doctor_link.p4_cli import main


def _files_for_report(library: Path, output: Path | None) -> list[Path]:
    base = library.resolve()
    root = output.resolve() if output is not None else base / ".doctor-link"
    files: list[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if root == resolved or root in resolved.parents:
            continue
        files.append(path)
    return files


@main.command("diagnose-now")
@click.argument("library", default=".", required=False)
@click.option("--json", "j", is_flag=True)
@click.option("--report-json", is_flag=True)
@click.option("--output", "o", type=click.Path(file_okay=False, path_type=str))
def diagnose_now(library: str, j: bool, report_json: bool, o: str | None) -> None:
    output = Path(o) if o else None
    path = run(Path(library), output)
    if report_json:
        report = build_report(_files_for_report(Path(library), output))
        click.echo(json.dumps({"summary": str(path), "report": report}))
    elif j:
        click.echo(json.dumps({"summary": str(path)}))
    else:
        click.echo(str(path))
