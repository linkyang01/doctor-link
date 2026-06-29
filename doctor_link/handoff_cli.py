from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.ai_handoff import (
    DEFAULT_HANDOFF_TOOL,
    SUPPORTED_TOOLS,
    build_handoff_package,
    check_handoff_compatibility,
    list_handoff_profiles,
)
from doctor_link.p4_cli import main


class HandoffGroup(click.Group):
    """Allow `doctor-link handoff <package_dir>` as shorthand for `handoff generate`."""

    def resolve_command(self, ctx: click.Context, args: list[str]) -> tuple[str | None, click.Command | None, list[str]]:
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            return "generate", self.get_command(ctx, "generate"), args
        return super().resolve_command(ctx, args)


@main.group("handoff", cls=HandoffGroup)
def handoff_group() -> None:
    """Generate, inspect, and pre-check AI Coding handoff packages."""


@handoff_group.command("generate")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--tool", default=DEFAULT_HANDOFF_TOOL, show_default=True, type=click.Choice(sorted(SUPPORTED_TOOLS)), help="Target AI Coding tool profile.")
@click.option("--out", "output", type=click.Path(path_type=Path), default=None, help="Optional output directory.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def handoff_generate_command(package_dir: Path, tool: str, output: Path | None, json_output: bool) -> None:
    """Generate an AI Coding handoff package."""
    result = build_handoff_package(package_dir=package_dir, tool=tool, output_dir=output)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Generated AI handoff package: {result.output_dir}")
    click.echo(f"Manifest: {result.manifest_path}")
    click.echo(f"Instruction: {result.instruction_path}")
    click.echo(f"Included files: {len(result.included_files)}")
    click.echo(f"Missing files: {len(result.missing_files)}")
    if result.compatibility_path:
        click.echo(f"Compatibility: {result.compatibility_path}")


@handoff_group.command("list")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def handoff_list_command(json_output: bool) -> None:
    """List supported AI handoff tool profiles."""
    profiles = list_handoff_profiles()
    if json_output:
        click.echo(json.dumps({"profiles": profiles}, ensure_ascii=False, indent=2))
        return
    click.echo("Supported AI handoff profiles:")
    for profile in profiles:
        click.echo(f"- {profile['tool']}: {profile['display_name']} ({profile['instruction_file']})")


@handoff_group.command("check")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--tool", default=DEFAULT_HANDOFF_TOOL, show_default=True, type=click.Choice(sorted(SUPPORTED_TOOLS)), help="Target AI Coding tool profile.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def handoff_check_command(package_dir: Path, tool: str, json_output: bool) -> None:
    """Pre-check handoff compatibility without generating a package."""
    report = check_handoff_compatibility(package_dir, tool=tool)
    if json_output:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Handoff compatibility status: {report.status}")
    click.echo(f"Tool profile: {report.tool}")
    click.echo(f"Required missing: {len(report.required_missing)}")
    click.echo(f"Optional missing: {len(report.optional_missing)}")
    click.echo(f"Missing evidence warnings: {len(report.missing_evidence_warnings)}")
    click.echo(f"Privacy warnings: {len(report.privacy_warnings)}")
    if report.required_missing:
        for item in report.required_missing:
            click.echo(f"  - {item}")