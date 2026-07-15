from __future__ import annotations

import json
import hashlib
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text
from doctor_link.core.command_runner import run_command
from doctor_link.core.root_cause import analyze_root_cause
from doctor_link.core.safe_command_runner import run_safe_command_sequence, validate_safe_command_sequence
from doctor_link.core.solve import (
    SolveCommand,
    SolveCommandResult,
    detect_project_type,
    discover_solve_commands,
    resolve_solve_target,
)


@main.command("explain")
@click.argument("project_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--problem", required=True, help="Concrete problem whose failing evidence should be explained.")
@click.option("--package", default=None, help="Workspace package path relative to PROJECT_ROOT.")
@click.option("--reproduce-command", default=None, help="Safe command that fails while the problem exists.")
@click.option("--test-command", default=None, help="Safe regression command used as failing evidence.")
@click.option("--command-timeout", default=120, show_default=True, type=click.IntRange(1), help="Timeout for each check.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Directory for explain receipts.")
@click.option("--json", "json_output", is_flag=True, help="Print the complete explain result as JSON.")
def explain_command(
    project_root: Path,
    problem: str,
    package: str | None,
    reproduce_command: str | None,
    test_command: str | None,
    command_timeout: int,
    output: Path | None,
    json_output: bool,
) -> None:
    """Cluster failing evidence into advisory root-cause source hints (no edits)."""
    workspace = project_root.expanduser().resolve()
    root, package_path, target_error = resolve_solve_target(workspace, package)
    clean_problem = problem.strip()
    if target_error:
        raise click.UsageError(target_error)
    if not clean_problem:
        raise click.UsageError("--problem is required.")
    project_type = detect_project_type(root)
    if project_type not in {"python", "javascript"}:
        raise click.UsageError("explain supports Python and Node.js JavaScript/TypeScript projects.")

    commands = discover_solve_commands(root, reproduce_command=reproduce_command, test_command=test_command)
    if not commands:
        raise click.UsageError("No executable reproduction or test command was found. Supply --reproduce-command or --test-command.")
    command_errors = [
        f"{item.command_id}: {error}"
        for item in commands
        if (error := validate_safe_command_sequence(item.command)) is not None
    ]
    if command_errors:
        raise click.UsageError("One or more commands use unsupported shell syntax: " + "; ".join(command_errors))

    before_worktree = _git_worktree_fingerprint(root)
    baseline = _run_checks(root, commands, command_timeout)
    after_worktree = _git_worktree_fingerprint(root)
    worktree_changed = (
        before_worktree is not None
        and after_worktree is not None
        and before_worktree != after_worktree
    )
    analysis = analyze_root_cause(
        root,
        problem=clean_problem,
        checks=[item.to_dict() for item in baseline],
    )
    result_status = "modified_worktree" if worktree_changed else analysis.status
    result_summary = (
        "A diagnostic check changed the Git working tree. Review and restore those changes before trusting the explanation."
        if worktree_changed
        else analysis.summary
    )
    payload = {
        "schema": "doctor-link-explain-session-v1",
        "project_root": str(root),
        "workspace_root": str(workspace),
        "package_path": package_path,
        "project_type": project_type,
        "problem": clean_problem,
        "commands": [item.to_dict() for item in commands],
        "baseline": [item.to_dict() for item in baseline],
        "analysis": analysis.to_dict(),
        "status": result_status,
        "summary": result_summary,
        "worktree_changed": worktree_changed,
    }

    if output is not None:
        out_dir = output.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(out_dir / "explain-session.json", payload)
        atomic_write_text(out_dir / "root-cause.md", _render_markdown(payload))
        payload["output_dir"] = str(out_dir)

    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        click.echo(f"Explain status: {result_status}")
        click.echo(f"Summary: {result_summary}")
        for hint in analysis.hints[:5]:
            paths = ", ".join(hint.get("candidate_paths") or []) or "(unmapped)"
            click.echo(
                f"- {hint.get('symbol')} [{hint.get('confidence')}] "
                f"evidence={hint.get('evidence_count')} paths={paths}"
            )
            if hint.get("rationale"):
                click.echo(f"  {hint['rationale']}")
        for warning in analysis.warnings:
            click.echo(f"Warning: {warning}")
        if output is not None:
            click.echo(f"Explain session: {payload['output_dir']}")

    if worktree_changed:
        raise click.exceptions.Exit(5)
    if analysis.status in {"no_failures"}:
        raise click.exceptions.Exit(3)
    if analysis.status == "insufficient_evidence":
        raise click.exceptions.Exit(4)


def _run_checks(root: Path, commands: list[SolveCommand], timeout_seconds: int) -> list[SolveCommandResult]:
    results: list[SolveCommandResult] = []
    for item in commands:
        completed = run_safe_command_sequence(
            item.command,
            cwd=root,
            timeout_seconds=timeout_seconds,
            environment_overrides={"CI": "1", "NO_COLOR": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        results.append(
            SolveCommandResult(
                command_id=item.command_id,
                kind=item.kind,
                command=item.command,
                status="passed" if completed.returncode == 0 else ("timed_out" if completed.timed_out else "failed"),
                return_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                timed_out=completed.timed_out,
            )
        )
    return results


def _git_worktree_fingerprint(root: Path) -> str | None:
    top = run_command(["git", "rev-parse", "--show-toplevel"], cwd=root, timeout_seconds=15)
    if top.returncode != 0:
        return None
    diff = run_command(["git", "diff", "--no-ext-diff", "--binary", "HEAD"], cwd=root, timeout_seconds=30)
    untracked = run_command(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=root, timeout_seconds=15
    )
    if diff.returncode != 0 or untracked.returncode != 0:
        return None
    digest = hashlib.sha256(diff.stdout.encode("utf-8", errors="replace"))
    for relative in sorted(item for item in untracked.stdout.splitlines() if item):
        digest.update(relative.encode("utf-8", errors="replace"))
        path = root / relative
        try:
            digest.update(path.read_bytes() if path.is_file() else b"<not-a-file>")
        except OSError:
            digest.update(b"<unreadable>")
    return digest.hexdigest()


def _render_markdown(payload: dict) -> str:
    analysis = payload.get("analysis") or {}
    lines = [
        "# Doctor link root-cause hints",
        "",
        f"Status: `{analysis.get('status')}`",
        f"Problem: {payload.get('problem')}",
        "",
        str(analysis.get("summary") or ""),
        "",
        "These hints are advisory only and do not replace independent verification.",
        "",
        "## Hints",
        "",
    ]
    hints = analysis.get("hints") or []
    if not hints:
        lines.append("- No hints generated.")
    for hint in hints:
        paths = ", ".join(f"`{path}`" for path in hint.get("candidate_paths") or []) or "`(unmapped)`"
        lines.append(
            f"- **{hint.get('symbol')}** (confidence {hint.get('confidence')}, "
            f"evidence {hint.get('evidence_count')}): {hint.get('rationale')} → {paths}"
        )
    patterns = analysis.get("failure_patterns") or []
    if patterns:
        lines.extend(["", "## Failure patterns", ""])
        lines.extend(f"- {item}" for item in patterns)
    return "\n".join(lines) + "\n"


__all__ = ["explain_command"]
