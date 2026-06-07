from __future__ import annotations

from pathlib import Path

import click

from doctor_link.diagnose_now import diagnose_now as run
from doctor_link.p4_cli import main


@main.command("diagnose-now")
@click.argument("library", default=".", required=False)
def diagnose_now(library: str) -> None:
    summary = run(Path(library))
    click.echo(str(summary))
