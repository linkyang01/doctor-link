from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.adapter_runtime import run_adapter
from doctor_link.core.integrity_privacy import verify_integrity_manifest, write_integrity_verify
from doctor_link.core.plugin_runtime import run_plugin


def register_hardening_commands() -> None:
    """Register post-P7 hardening command overrides."""
    integrity_group = main.commands.get("integrity")
    if isinstance(integrity_group, click.Group):
        integrity_group.commands["verify"] = integrity_verify_strict

    adapter_group = main.commands.get("adapter")
    if isinstance(adapter_group, click.Group):
        adapter_group.commands["run"] = adapter_run_guarded

    plugin_group = main.commands.get("plugin")
    if isinstance(plugin_group, click.Group):
        plugin_group.commands["run"] = plugin_run_guarded


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


@click.command("run")
@click.argument("adapter_id")
@click.argument("capability")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--adapters-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Adapter directory override.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Output directory for adapter run records.")
@click.option("--timeout", default=60, show_default=True, type=int, help="Adapter command timeout in seconds.")
@click.option("--allow-run", is_flag=True, help="Explicitly execute the local adapter command. Without this flag, only a dry-run record is written.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def adapter_run_guarded(
    adapter_id: str,
    capability: str,
    project_root: Path,
    adapters_dir: Path | None,
    output: Path | None,
    timeout: int,
    allow_run: bool,
    json_output: bool,
) -> None:
    """Dry-run or explicitly execute a configured local adapter capability."""
    result = run_adapter(
        project_root,
        adapter_id,
        capability,
        adapters_dir=adapters_dir,
        output_dir=output,
        timeout_seconds=timeout,
        allow_run=allow_run,
    )
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Adapter run status: {result.status}")
    click.echo(f"Adapter: {result.adapter_id}")
    click.echo(f"Capability: {result.capability}")
    click.echo(f"Dry run: {result.dry_run}")
    click.echo(f"Explicit approval: {result.explicit_user_approval}")
    click.echo(f"Return code: {result.return_code}")
    if result.status == "failed":
        raise click.ClickException("Adapter run failed.")


@click.command("run")
@click.argument("plugin_id")
@click.argument("extension_point")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--plugins-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Plugin directory override.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Output directory for plugin run records.")
@click.option("--timeout", default=60, show_default=True, type=int, help="Plugin command timeout in seconds.")
@click.option("--allow-run", is_flag=True, help="Explicitly execute the local plugin command. Without this flag, only a dry-run record is written.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def plugin_run_guarded(
    plugin_id: str,
    extension_point: str,
    project_root: Path,
    plugins_dir: Path | None,
    output: Path | None,
    timeout: int,
    allow_run: bool,
    json_output: bool,
) -> None:
    """Dry-run or explicitly execute a configured local plugin extension point."""
    result = run_plugin(
        project_root,
        plugin_id,
        extension_point,
        plugins_dir=plugins_dir,
        output_dir=output,
        timeout_seconds=timeout,
        allow_run=allow_run,
    )
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Plugin run status: {result.status}")
    click.echo(f"Plugin: {result.plugin_id}")
    click.echo(f"Extension point: {result.extension_point}")
    click.echo(f"Dry run: {result.dry_run}")
    click.echo(f"Explicit approval: {result.explicit_user_approval}")
    click.echo(f"Return code: {result.return_code}")
    if result.status == "failed":
        raise click.ClickException("Plugin run failed.")
