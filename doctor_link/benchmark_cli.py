from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.benchmark import run_benchmark
from doctor_link.p4_cli import main


@main.command("benchmark")
@click.argument("manifest", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--out", "output", required=True, type=click.Path(file_okay=False, path_type=Path))
@click.option("--allow-repair", is_flag=True, help="Explicitly allow every benchmark scenario to invoke repairs.")
@click.option("--json", "json_output", is_flag=True, help="Print the complete benchmark result as JSON.")
def benchmark_command(manifest: Path, output: Path, allow_repair: bool, json_output: bool) -> None:
    """Run a reproducible multi-project solve benchmark."""
    try:
        result = run_benchmark(manifest, output_dir=output, allow_repair=allow_repair)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Benchmark status: {result.status}")
        click.echo(f"Scenarios: {result.total}")
        click.echo(f"Reproduction rate: {result.reproduction_rate:.2%}")
        click.echo(f"Report: {Path(result.output_dir) / 'benchmark-result.md'}")
    if result.status != "passed":
        raise click.exceptions.Exit(1)


__all__ = ["benchmark_command"]
