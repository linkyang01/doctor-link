from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.knowledge_archive import (
    append_archive_audit,
    check_archive_policy,
    create_archive,
    export_archive,
    export_knowledge,
    inspect_archive,
    query_knowledge,
    write_knowledge_index,
)


@main.group("knowledge")
def knowledge_group() -> None:
    """Build, query, and export local diagnostic knowledge indexes."""


@knowledge_group.command("build")
@click.argument("reports_root", type=click.Path(file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=Path("DoctorReports/knowledge-index.json"), help="Knowledge index output path.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def knowledge_build(reports_root: Path, output: Path, json_output: bool) -> None:
    """Build a local diagnostic knowledge index from DoctorReports."""
    index = write_knowledge_index(reports_root, output)
    if json_output:
        click.echo(json.dumps(index.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Knowledge index: {output}")
    click.echo(f"Records: {len(index.records)}")
    click.echo(f"Recurring failures: {len(index.recurring_failures)}")


@knowledge_group.command("query")
@click.argument("index", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("query")
@click.option("--limit", default=20, show_default=True, type=int, help="Maximum records to return.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def knowledge_query(index: Path, query: str, limit: int, json_output: bool) -> None:
    """Query a local diagnostic knowledge index."""
    result = query_knowledge(index, query, limit=limit)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Matched records: {result.matched_count}")
    for record in result.records:
        click.echo(f"- {record.get('path')}: {record.get('status')} {record.get('summary')}")


@knowledge_group.command("export")
@click.argument("index", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("output", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def knowledge_export(index: Path, output: Path, json_output: bool) -> None:
    """Export a local diagnostic knowledge index."""
    exported = export_knowledge(index, output)
    if json_output:
        click.echo(json.dumps(exported.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Knowledge export: {output}")
    click.echo(f"Records: {len(exported.records)}")


@main.group("archive")
def archive_group() -> None:
    """Create, inspect, export, and policy-check local diagnostic archives."""


@archive_group.command("create")
@click.argument("source_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("archive_root", type=click.Path(file_okay=False, path_type=Path))
@click.option("--metadata", "metadata_items", multiple=True, help="Metadata key=value pair. Can be repeated.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def archive_create(source_root: Path, archive_root: Path, metadata_items: tuple[str, ...], json_output: bool) -> None:
    """Create a local archive from a source directory."""
    metadata = _metadata_dict(metadata_items)
    record = create_archive(source_root, archive_root, metadata)
    if json_output:
        click.echo(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Archive: {archive_root}")
    click.echo(f"Files: {len(record.files)}")


@archive_group.command("inspect")
@click.argument("archive_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def archive_inspect(archive_root: Path, json_output: bool) -> None:
    """Inspect local archive metadata."""
    record = inspect_archive(archive_root)
    append_archive_audit(archive_root, "archive-inspected", {"file_count": len(record.files)})
    if json_output:
        click.echo(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Archive: {archive_root}")
    click.echo(f"Files: {len(record.files)}")


@archive_group.command("policy-check")
@click.argument("archive_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--max-files", type=int, default=None, help="Maximum allowed archived file count.")
@click.option("--max-size-bytes", type=int, default=None, help="Maximum allowed archived total size in bytes.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def archive_policy_check(archive_root: Path, max_files: int | None, max_size_bytes: int | None, json_output: bool) -> None:
    """Check local archive retention policy."""
    result = check_archive_policy(archive_root, max_files=max_files, max_size_bytes=max_size_bytes)
    append_archive_audit(archive_root, "archive-policy-checked", result.policy)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Archive policy status: {result.status}")
        click.echo(f"Findings: {len(result.findings)}")
    if result.status != "passed":
        raise click.ClickException("Archive policy check blocked.")


@archive_group.command("export")
@click.argument("archive_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("output", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def archive_export(archive_root: Path, output: Path, json_output: bool) -> None:
    """Export a local archive as a zip file."""
    final = export_archive(archive_root, output)
    payload = {"output": str(final), "status": "passed"}
    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    click.echo(f"Archive export: {final}")


def _metadata_dict(items: tuple[str, ...]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for item in items:
        if "=" in item:
            key, value = item.split("=", 1)
            metadata[key] = value
    return metadata
