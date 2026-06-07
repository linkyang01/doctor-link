from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.diagnose_now import diagnose_now as run
from doctor_link.p4_cli import main


@main.command("diagnose-now")
@click.argument("library", default=".", required=False)
@click.option("--json", "j", is_flag=True)
@click.option("--output", "o", type=click.Path(file_okay=False, path_type=str))
def diagnose_now(library: str, j: bool, o: str | None) -> None:
    path = run(Path(library), Path(o) if o else None)
    if j:
        click.echo(json.dumps({"summary": str(path)}))
    else:
        click.echo(str(path))
