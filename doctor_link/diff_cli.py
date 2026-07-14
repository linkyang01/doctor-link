from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.change_receipt import build_change_receipt, receipt_to_markdown
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text


@main.command("diff")
@click.argument("session_or_project", type=click.Path(exists=True, path_type=Path))
@click.option("--base", default=None, help="Base git ref. Defaults to session original branch tip or merge-base.")
@click.option("--head", default="HEAD", show_default=True, help="Head git ref.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional directory for receipt files.")
@click.option("--json", "json_output", is_flag=True, help="Print the complete change receipt as JSON.")
def diff_command(
    session_or_project: Path,
    base: str | None,
    head: str,
    output: Path | None,
    json_output: bool,
) -> None:
    """Build a structured change receipt from a solve session or Git project."""
    target = session_or_project.expanduser().resolve()
    session_payload: dict | None = None
    project_root = target
    protected: list[str] = []
    hash_changes: list[dict] = []
    session_file = target / "solve-session.json"
    if session_file.is_file():
        session_payload = json.loads(session_file.read_text(encoding="utf-8"))
        project_root = Path(str(session_payload.get("project_root") or target)).resolve()
        protected = list(session_payload.get("protected_verification_inputs") or [])
        hash_changes = list(session_payload.get("verification_input_changes") or [])
        if base is None:
            base = session_payload.get("original_branch")
        if head == "HEAD" and session_payload.get("repair_branch"):
            head = str(session_payload["repair_branch"])
    elif not (target / ".git").exists() and not (target / "pyproject.toml").exists() and not (target / "package.json").exists():
        raise click.UsageError("Provide a solve-session directory or a Git project root.")

    receipt = build_change_receipt(
        project_root,
        base_ref=base,
        head_ref=head,
        protected_paths=protected,
        verification_input_changes=hash_changes,
    )
    out_dir = output.expanduser().resolve() if output else (target if session_payload else None)
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(out_dir / "change-receipt.json", receipt.to_dict())
        atomic_write_text(out_dir / "change-receipt.md", receipt_to_markdown(receipt))

    if json_output:
        click.echo(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(receipt.summary)
        for item in receipt.files[:30]:
            marker = " protected" if item.get("protected") else ""
            click.echo(
                f"- {item.get('path')} [{item.get('category')}/{item.get('status')}] "
                f"+{item.get('additions', 0)}/-{item.get('deletions', 0)}{marker}"
            )
        if receipt.protected_changes:
            click.echo("Protected changes: " + ", ".join(receipt.protected_changes))
        if out_dir is not None:
            click.echo(f"Change receipt: {out_dir / 'change-receipt.md'}")


__all__ = ["diff_command"]
