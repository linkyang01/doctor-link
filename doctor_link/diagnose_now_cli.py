from __future__ import annotations

from pathlib import Path

import click

from doctor_link.diagnose_now import diagnose_now as run_diagnose_now
from doctor_link.p4_cli import main


@main.command("diagnose-now")
@click.argument("library", required=False, default=".")
def diagnose_now(library: str) -> None:
    summary, count = run_diagnose_now(Path(library))
    click.echo(f"files: {count