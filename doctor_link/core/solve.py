from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from doctor_link.core.command_runner import run_command
from doctor_link.core.models import utc_now_iso
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text
from doctor_link.core.preflight import run_preflight
from doctor_link.core.reproduction import load_reproduction_catalog
from doctor_link.core.safe_command_runner import run_safe_command_sequence, validate_safe_command_sequence
from doctor_link.core.test_matrix_runner import load_test_matrix


SOLVE_SCHEMA = "doctor-link-solve-session-v1"
FINAL_STATUSES = {"approval_required", "blocked", "failed", "not_reproduced", "verified"}


@dataclass
class SolveCommand:
    command_id: str
    kind: str
    command: str
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SolveCommandResult:
    command_id: str
    kind: str
    command: str
    status: str
    return_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RepairExecution:
    status: str
    return_code: int
    thread_id: str | None = None
    final_message: str = ""
    event_count: int = 0
    file_change_events: int = 0
    timed_out: bool = False
    error: str | None = None
    raw_stdout: str = field(default="", repr=False)
    raw_stderr: str = field(default="", repr=False)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("raw_stdout", None)
        payload.pop("raw_stderr", None)
        return payload


@dataclass
class SolveRound:
    round_number: int
    repair: dict[str, Any]
    verification: list[dict[str, Any]]
    verified: bool
    prompt_path: str
    events_path: str
    stderr_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SolveResult:
    schema: str
    session_id: str
    project_root: str
    problem: str
    project_type: str
    tool: str
    status: str = "preparing"
    started_at: str = field(default_factory=utc_now_iso)
    completed_at: str | None = None
    output_dir: str | None = None
    original_branch: str | None = None
    repair_branch: str | None = None
    explicit_user_approval: bool = False
    preflight: dict[str, Any] = field(default_factory=dict)
    commands: list[dict[str, Any]] = field(default_factory=list)
    baseline: list[dict[str, Any]] = field(default_factory=list)
    rounds: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status == "verified"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["success"] = self.success
        return payload


class RepairExecutor(Protocol):
    name: str

    def run(self, prompt: str, project_root: Path, timeout_seconds: int) -> RepairExecution: ...


class CodexRepairExecutor:
    name = "codex"

    def __init__(self, binary: str = "codex") -> None:
        self.binary = binary

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def run(self, prompt: str, project_root: Path, timeout_seconds: int) -> RepairExecution:
        command = [
            self.binary,
            "exec",
            "--sandbox",
            "workspace-write",
            "--json",
            "--color",
            "never",
            "--cd",
            str(project_root),
            prompt,
        ]
        completed = run_command(command, cwd=project_root, timeout_seconds=timeout_seconds)
        parsed = _parse_codex_jsonl(completed.stdout)
        status = "completed" if completed.returncode == 0 else ("timed_out" if completed.timed_out else "failed")
        return RepairExecution(
            status=status,
            return_code=completed.returncode,
            thread_id=parsed["thread_id"],
            final_message=parsed["final_message"],
            event_count=parsed["event_count"],
            file_change_events=parsed["file_change_events"],
            timed_out=completed.timed_out,
            error=completed.error,
            raw_stdout=completed.stdout,
            raw_stderr=completed.stderr,
        )


def solve_project(
    project_root: Path,
    *,
    problem: str,
    reproduce_command: str | None = None,
    test_command: str | None = None,
    output_root: Path | None = None,
    tool: str = "codex",
    allow_repair: bool = False,
    max_rounds: int = 3,
    command_timeout_seconds: int = 120,
    repair_timeout_seconds: int = 900,
    repair_executor: RepairExecutor | None = None,
) -> SolveResult:
    """Reproduce, repair, and independently verify one bounded Python-project problem."""
    root = project_root.expanduser().resolve()
    clean_problem = problem.strip()
    session_id = _session_id(root, clean_problem)
    project_type = detect_project_type(root)
    result = SolveResult(
        schema=SOLVE_SCHEMA,
        session_id=session_id,
        project_root=str(root),
        problem=clean_problem,
        project_type=project_type,
        tool=tool,
        explicit_user_approval=allow_repair,
    )

    if not root.is_dir():
        return _finish(result, "blocked", "Project root does not exist.", blocker="project_root_missing")
    if not clean_problem:
        return _finish(result, "blocked", "A concrete problem statement is required.", blocker="problem_missing")
    if project_type != "python":
        return _finish(
            result,
            "blocked",
            "This first automatic-solve release supports Python projects only.",
            blocker="unsupported_project_type",
        )
    if tool != "codex":
        return _finish(result, "blocked", f"Unsupported repair tool: {tool}", blocker="unsupported_repair_tool")

    git_state = _inspect_git(root)
    result.original_branch = git_state.get("branch")
    if git_state.get("error"):
        return _finish(result, "blocked", str(git_state["error"]), blocker="git_repository_required")
    if git_state.get("dirty"):
        return _finish(
            result,
            "blocked",
            "The Git working tree has uncommitted changes. Commit or stash them before automatic repair.",
            blocker="dirty_worktree",
        )

    result.preflight = run_preflight(root).to_dict()
    if result.preflight.get("status") == "blocked":
        return _finish(result, "blocked", "Doctor link preflight found blocking configuration errors.", blocker="preflight_blocked")

    commands = discover_solve_commands(root, reproduce_command=reproduce_command, test_command=test_command)
    result.commands = [item.to_dict() for item in commands]
    if not commands:
        return _finish(
            result,
            "blocked",
            "No executable reproduction or test command was found. Supply --reproduce-command or --test-command.",
            blocker="verification_command_missing",
        )
    command_errors = [
        f"{item.command_id}: {error}"
        for item in commands
        if (error := validate_safe_command_sequence(item.command)) is not None
    ]
    if command_errors:
        result.blockers.extend(command_errors)
        return _finish(result, "blocked", "One or more commands use unsupported shell syntax.")

    baseline = _run_solve_commands(root, commands, command_timeout_seconds)
    result.baseline = [item.to_dict() for item in baseline]
    post_baseline_git = _inspect_git(root)
    if post_baseline_git.get("dirty"):
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            "A reproduction or test command changed the Git working tree. Restore it before automatic repair.",
            blocker="checks_modified_worktree",
        )
    if _checks_passed(commands, baseline):
        result.next_steps.append("Confirm the problem statement and provide a command that fails when the problem is present.")
        return _persist_and_finish(
            result,
            output_root,
            "not_reproduced",
            "All independent checks already pass, so Doctor link did not authorize a repair.",
        )

    prompt = build_repair_prompt(result, baseline, round_number=1)
    if not allow_repair:
        result.next_steps.append(
            f'doctor-link solve "{root}" --problem "{clean_problem}" --allow-repair'
        )
        return _persist_and_finish(
            result,
            output_root,
            "approval_required",
            "The problem was reproduced. Review the solve plan, then rerun with --allow-repair to create a repair branch and invoke Codex.",
            preview_prompt=prompt,
        )

    executor = repair_executor or CodexRepairExecutor()
    if isinstance(executor, CodexRepairExecutor) and not executor.available():
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            "Codex CLI was not found. Install or expose the codex executable before retrying.",
            blocker="codex_cli_missing",
            preview_prompt=prompt,
        )

    repair_branch = _repair_branch_name(clean_problem, session_id)
    branch_result = run_command(["git", "switch", "-c", repair_branch], cwd=root, timeout_seconds=30)
    if branch_result.returncode != 0:
        result.warnings.append(branch_result.stderr.strip())
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            "Doctor link could not create the isolated repair branch.",
            blocker="repair_branch_creation_failed",
            preview_prompt=prompt,
        )
    result.repair_branch = repair_branch

    session_dir = _prepare_session_dir(result, output_root)
    previous_verification = baseline
    previous_message = ""
    round_limit = min(3, max(1, max_rounds))
    for round_number in range(1, round_limit + 1):
        round_dir = session_dir / f"round-{round_number}"
        round_dir.mkdir(parents=True, exist_ok=True)
        round_prompt = build_repair_prompt(
            result,
            previous_verification,
            round_number=round_number,
            previous_message=previous_message,
        )
        prompt_path = round_dir / "prompt.md"
        events_path = round_dir / "codex-events.jsonl"
        stderr_path = round_dir / "codex-stderr.log"
        atomic_write_text(prompt_path, round_prompt)

        try:
            execution = executor.run(round_prompt, root, repair_timeout_seconds)
        except Exception as exc:  # preserve a local receipt when a provider implementation fails unexpectedly
            execution = RepairExecution(
                status="failed",
                return_code=1,
                error=f"{type(exc).__name__}: {exc}",
                raw_stderr=f"{type(exc).__name__}: {exc}\n",
            )
        atomic_write_text(events_path, execution.raw_stdout)
        atomic_write_text(stderr_path, execution.raw_stderr)
        verification = _run_solve_commands(root, commands, command_timeout_seconds)
        verified = _checks_passed(commands, verification)
        atomic_write_json(round_dir / "verification.json", [item.to_dict() for item in verification])
        solve_round = SolveRound(
            round_number=round_number,
            repair=execution.to_dict(),
            verification=[item.to_dict() for item in verification],
            verified=verified,
            prompt_path=str(prompt_path),
            events_path=str(events_path),
            stderr_path=str(stderr_path),
        )
        result.rounds.append(solve_round.to_dict())
        _write_session_files(session_dir, result)

        if verified:
            result.next_steps.extend(
                [
                    f"Review the changes on branch `{repair_branch}`.",
                    "Commit and push the repair only after reviewing the diff.",
                ]
            )
            return _persist_and_finish(
                result,
                output_root,
                "verified",
                f"Doctor link reproduced the problem, Codex repaired it in {round_number} round(s), and all independent checks passed.",
                session_dir=session_dir,
            )
        if execution.return_code == 127:
            result.blockers.append("repair_executor_unavailable")
            return _persist_and_finish(
                result,
                output_root,
                "blocked",
                "The repair executor could not be started.",
                session_dir=session_dir,
            )
        previous_verification = verification
        previous_message = execution.final_message

    result.next_steps.append("Review the final failing verification logs and refine the problem or commands before retrying.")
    return _persist_and_finish(
        result,
        output_root,
        "failed",
        f"Codex used {round_limit} repair round(s), but independent verification still fails.",
        session_dir=session_dir,
    )


def detect_project_type(project_root: Path) -> str:
    root = project_root.expanduser().resolve()
    python_markers = [root / "pyproject.toml", root / "setup.py", root / "setup.cfg", root / "requirements.txt"]
    if any(path.is_file() for path in python_markers):
        return "python"
    common_python_sources = [root / "src", root / "app"]
    if (
        any(root.glob("*.py"))
        or (root / "tests").is_dir()
        or any(source.is_dir() and next(source.rglob("*.py"), None) is not None for source in common_python_sources)
    ):
        return "python"
    return "unsupported"


def discover_solve_commands(
    project_root: Path,
    *,
    reproduce_command: str | None = None,
    test_command: str | None = None,
) -> list[SolveCommand]:
    commands: list[SolveCommand] = []
    if reproduce_command:
        commands.append(SolveCommand("explicit-reproduction", "reproduction", reproduce_command))
    else:
        catalog = load_reproduction_catalog(project_root)
        commands.extend(
            SolveCommand(f"reproduction-{entry.reproduction_id}", "reproduction", entry.command)
            for entry in catalog.entries
            if entry.kind != "manual" and entry.command
        )
    if test_command:
        commands.append(SolveCommand("explicit-test", "test", test_command))
    else:
        matrix = load_test_matrix(project_root)
        commands.extend(
            SolveCommand(f"test-{job.job_id}", "test", job.command, required=job.required)
            for job in matrix.jobs
        )
        if not matrix.jobs and (project_root / "tests").is_dir():
            commands.append(SolveCommand("test-pytest", "test", "python -m pytest"))
    return _dedupe_commands(commands)


def build_repair_prompt(
    result: SolveResult,
    checks: list[SolveCommandResult],
    *,
    round_number: int,
    previous_message: str = "",
) -> str:
    evidence = []
    for check in checks:
        evidence.extend(
            [
                f"### {check.command_id} ({check.status})",
                f"Command: `{check.command}`",
                f"Exit code: `{check.return_code}`",
                "```text",
                _bounded_output(check.stdout, check.stderr),
                "```",
            ]
        )
    previous = ""
    if previous_message:
        previous = f"\nPrevious repair summary:\n{previous_message[-3000:]}\n"
    return "\n".join(
        [
            "# Doctor link bounded automatic repair",
            "",
            f"Repair round: {round_number}",
            f"Project root: {result.project_root}",
            f"Problem: {result.problem}",
            previous,
            "## Independent failing evidence",
            "",
            *evidence,
            "",
            "## Required behavior",
            "",
            "- Inspect the repository and identify the grounded root cause.",
            "- Make the smallest production-quality code or test-fixture change that fixes the stated problem.",
            "- Stay inside this workspace. Do not switch branches, commit, push, publish, or change Git configuration.",
            "- Preserve unrelated behavior and existing user changes.",
            "- You may run focused tests, but Doctor link will independently rerun every command above.",
            "- Do not claim success merely because a patch was written; finish with the root cause, changed files, risks, and tests run.",
            "- If the issue cannot be safely fixed, stop and explain the concrete blocker instead of fabricating success.",
            "",
        ]
    )


def _run_solve_commands(root: Path, commands: list[SolveCommand], timeout_seconds: int) -> list[SolveCommandResult]:
    results: list[SolveCommandResult] = []
    for item in commands:
        completed = run_safe_command_sequence(
            item.command,
            cwd=root,
            timeout_seconds=timeout_seconds,
            environment_overrides={"PYTHONDONTWRITEBYTECODE": "1"},
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


def _checks_passed(commands: list[SolveCommand], results: list[SolveCommandResult]) -> bool:
    required_ids = {item.command_id for item in commands if item.required}
    return bool(required_ids) and all(
        item.status == "passed" for item in results if item.command_id in required_ids
    )


def _inspect_git(root: Path) -> dict[str, Any]:
    top = run_command(["git", "rev-parse", "--show-toplevel"], cwd=root, timeout_seconds=15)
    if top.returncode != 0:
        return {"error": "Automatic repair requires a Git repository."}
    top_level = Path(top.stdout.strip()).resolve()
    if top_level != root:
        return {"error": f"Use the Git repository root as PROJECT_ROOT: {top_level}"}
    branch = run_command(["git", "branch", "--show-current"], cwd=root, timeout_seconds=15)
    status = run_command(["git", "status", "--porcelain"], cwd=root, timeout_seconds=15)
    if branch.returncode != 0 or status.returncode != 0:
        return {"error": "Doctor link could not inspect the Git working tree."}
    return {"branch": branch.stdout.strip() or "DETACHED", "dirty": bool(status.stdout.strip())}


def _parse_codex_jsonl(text: str) -> dict[str, Any]:
    thread_id: str | None = None
    final_message = ""
    event_count = 0
    file_change_events = 0
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        event_count += 1
        if event.get("type") == "thread.started":
            thread_id = str(event.get("thread_id") or "") or thread_id
        item = event.get("item")
        if isinstance(item, dict):
            item_type = str(item.get("type") or "")
            if item_type == "agent_message" and item.get("text"):
                final_message = str(item["text"])
            if item_type in {"file_change", "file_changes"}:
                file_change_events += 1
    return {
        "thread_id": thread_id,
        "final_message": final_message,
        "event_count": event_count,
        "file_change_events": file_change_events,
    }


def _prepare_session_dir(result: SolveResult, output_root: Path | None) -> Path:
    if result.output_dir:
        path = Path(result.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    root = Path(result.project_root)
    base = output_root.expanduser().resolve() if output_root is not None else root.parent / "DoctorReports" / root.name
    path = base / f"solve-{result.session_id}"
    path.mkdir(parents=True, exist_ok=True)
    result.output_dir = str(path)
    return path


def _persist_and_finish(
    result: SolveResult,
    output_root: Path | None,
    status: str,
    summary: str,
    *,
    blocker: str | None = None,
    preview_prompt: str | None = None,
    session_dir: Path | None = None,
) -> SolveResult:
    if blocker:
        result.blockers.append(blocker)
    directory = session_dir or _prepare_session_dir(result, output_root)
    if preview_prompt is not None:
        atomic_write_text(directory / "repair-prompt-preview.md", preview_prompt)
    finished = _finish(result, status, summary)
    _write_session_files(directory, finished)
    return finished


def _finish(result: SolveResult, status: str, summary: str, blocker: str | None = None) -> SolveResult:
    if status not in FINAL_STATUSES:
        raise ValueError(f"Unknown solve status: {status}")
    result.status = status
    result.summary = summary
    result.completed_at = utc_now_iso()
    if blocker:
        result.blockers.append(blocker)
    return result


def _write_session_files(session_dir: Path, result: SolveResult) -> None:
    atomic_write_json(session_dir / "solve-session.json", result.to_dict())
    atomic_write_text(session_dir / "solve-summary.md", _summary_markdown(result))


def _summary_markdown(result: SolveResult) -> str:
    lines = [
        "# Doctor link Automatic Solve",
        "",
        f"- Session: `{result.session_id}`",
        f"- Status: `{result.status}`",
        f"- Project: `{result.project_root}`",
        f"- Project type: `{result.project_type}`",
        f"- Tool: `{result.tool}`",
        f"- Explicit repair approval: `{str(result.explicit_user_approval).lower()}`",
        f"- Original branch: `{result.original_branch or 'N/A'}`",
        f"- Repair branch: `{result.repair_branch or 'N/A'}`",
        "",
        "## Problem",
        "",
        result.problem,
        "",
        "## Result",
        "",
        result.summary,
        "",
        "## Commands",
        "",
    ]
    lines.extend(f"- `{item['command_id']}`: `{item['command']}`" for item in result.commands)
    if result.blockers:
        lines.extend(["", "## Blockers", "", *[f"- {item}" for item in result.blockers]])
    if result.warnings:
        lines.extend(["", "## Warnings", "", *[f"- {item}" for item in result.warnings]])
    if result.next_steps:
        lines.extend(["", "## Next steps", "", *[f"- {item}" for item in result.next_steps]])
    lines.append("")
    return "\n".join(lines)


def _session_id(root: Path, problem: str) -> str:
    digest = hashlib.sha256(f"{root}:{problem}".encode("utf-8")).hexdigest()[:6]
    return f"{uuid.uuid4().hex[:8]}-{digest}"


def _repair_branch_name(problem: str, session_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", problem.casefold()).strip("-")[:24] or "repair"
    return f"doctor-link/solve-{slug}-{session_id[:8]}"


def _bounded_output(stdout: str, stderr: str, limit: int = 6000) -> str:
    text = "\n".join(part.strip() for part in (stdout, stderr) if part.strip()) or "No command output."
    if len(text) <= limit:
        return text
    return text[-limit:] + "\n[output truncated to final 6000 characters]"


def _dedupe_commands(commands: list[SolveCommand]) -> list[SolveCommand]:
    seen: set[tuple[str, str]] = set()
    result: list[SolveCommand] = []
    for item in commands:
        key = (item.kind, item.command)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
