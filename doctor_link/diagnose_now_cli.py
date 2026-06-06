from __future__ import annotations

from pathlib import Path

import click

from doctor_link.p4_cli import main


@main.command("diagnose-now")
@click.argument("library", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--out", "output", type=click.Path(path_type=Path), default=Path("DoctorReports"))
def diagnose_now(library: