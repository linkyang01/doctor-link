from __future__ import annotations

import click

from doctor_link.p4_cli import main


@main.command("diagnose-now")
def diagnose_now() -> None:
    click.echo("ok")
