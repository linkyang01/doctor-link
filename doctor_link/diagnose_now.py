from __future__ import annotations

from pathlib import Path

import click


def diagnose_now(library: Path) -> Path:
    root = library / ".doctor-link"
    root.mkdir(exist_ok=True)
    summary = root / "summary.md"
    summary.write_text("# Doctor link diagnose-now\n", encoding="utf-8")
    return summary


@click.command("diagnose-now")
@click.argument("library", required=False, default=".")
def