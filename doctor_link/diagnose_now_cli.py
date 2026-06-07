from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.diagnose_now import diagnose_now as run
from doctor_link.p4_cli import main


@main.command("diagnose-now")
@click.argument("library", default=".", required=False)
@click.option("--json", "as_json", is_flag=True)
def diagnose_now(library: str, as_json: bool) -> None:
    summary = run(Path(library))
