from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.integrity_privacy import verify_integrity_manifest, write_integrity_verify


def register_hardening_commands() -> None:
    """Register post-P7 hardening command overrides.

    The P7.8 implementation introduced ``doctor-link integrity verify``.
    This post-P7 hardening layer keeps the same command name and adds a
    strict mode without rewriting the long P4/P7 CLI module.
    """
    integrity_group = main.commands.get("integrity")
    if not isinstance(integrity_group, click.Group):
        return
    integrity_group.commands["verify"] = integrity_verify_strict


@click.command("verify")
@click.argument("root", type=click.Path(file_okay=False, path_type=Path))
@click.argument("manifest", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional verification report output path.")
@click.option("--strict", is_flag=True, help="Block files present under root but missing from the manifest.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def integrity_verify_strict(root: Path, manifest: Path, output: Path | None, strict: bool, json_output: bool) -> None:
    """Verify hashes, missing files, unsafe paths, and optional untracked files."""
    result = verify_integrity_manifest(root, manifest, strict=strict)
    if output:
        write_integrity_verify(result, output)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Integrity verification status: {result.status}")
        click.echo(f"Checked files: {result.checked_files}")
        click.echo(f"Findings: {len(result.findings)}")
    if result.status != "passed":
        raise click.ClickException("Integrity verification blocked.")
