from __future__ import annotations

import fnmatch
import hashlib
import json
import os
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
from doctor_link.core.change_receipt import build_change_receipt, receipt_to_markdown
from doctor_link.core.root_cause import analyze_root_cause
from doctor_link.core.safe_command_runner import (
    parse_safe_command_sequence,
    run_safe_command_sequence,
    validate_safe_command_sequence,
)
from doctor_link.core.test_matrix_runner import load_test_matrix


SOLVE_SCHEMA = "doctor-link-solve-session-v2"
SUPPORTED_PROJECT_TYPES = {"javascript", "python"}
FINAL_STATUSES = {
    "approval_required",
    "blocked",
    "failed",
    "not_reproduced",
    "review_required",
    "suggestion_ready",
    "verified",
}
VERIFICATION_CONFIG_PATHS = {
    ".yarnrc.yml",
    ".coveragerc",
    "bun.lock",
    "bun.lockb",
    "jsconfig.json",
    "noxfile.py",
    "npm-shrinkwrap.json",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
    "pyproject.toml",
    "pytest.ini",
    "setup.cfg",
    "tsconfig.json",
    "tox.ini",
    "yarn.lock",
}
VERIFICATION_CONFIG_PATTERNS = (
    "cypress.config.*",
    "jest.config.*",
    "playwright.config.*",
    "vitest.config.*",
)
VERIFICATION_CATALOG_PATHS = {
    ".doctorlink/reproduce.yml",
    ".doctorlink/reproduce.yaml",
    ".doctorlink/test-matrix.yml",
    ".doctorlink/test-matrix.yaml",
}
JAVASCRIPT_EXTENSIONS = {".cjs", ".cts", ".js", ".jsx", ".mjs", ".mts", ".ts", ".tsx"}
VERIFICATION_TEST_DIRECTORIES = ("__tests__", "spec", "test", "tests")
VERIFICATION_TEST_PATTERNS = (
    "conftest.py",
    "test_*.py",
    "*_test.py",
    *(f"*.test{extension}" for extension in sorted(JAVASCRIPT_EXTENSIONS)),
    *(f"*.spec{extension}" for extension in sorted(JAVASCRIPT_EXTENSIONS)),
)
IGNORED_VERIFICATION_PARTS = {
    ".cache",
    ".git",
    ".next",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}


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
    verification_input_changes: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SolveResult:
    schema: str
    session_id: str
    project_root: str
    workspace_root: str
    package_path: str | None
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
    allow_verification_changes: bool = False
    preflight: dict[str, Any] = field(default_factory=dict)
    commands: list[dict[str, Any]] = field(default_factory=list)
    baseline: list[dict[str, Any]] = field(default_factory=list)
    rounds: list[dict[str, Any]] = field(default_factory=list)
    protected_verification_inputs: list[str] = field(default_factory=list)
    verification_input_hashes: dict[str, str] = field(default_factory=dict)
    verification_input_changes: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    root_cause: dict[str, Any] = field(default_factory=dict)
    change_receipt: dict[str, Any] = field(default_factory=dict)
    suggest_only: bool = False

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
    allow_verification_changes: bool = False,
    suggest_only: bool = False,
    max_rounds: int = 3,
    command_timeout_seconds: int = 120,
    repair_timeout_seconds: int = 900,
    repair_executor: RepairExecutor | None = None,
    package: str | Path | None = None,
) -> SolveResult:
    """Reproduce, repair, and independently verify one bounded project problem."""
    workspace_root = project_root.expanduser().resolve()
    root, package_path, target_error = resolve_solve_target(workspace_root, package)
    clean_problem = problem.strip()
    session_id = _session_id(root, clean_problem)
    project_type = detect_project_type(root)
    result = SolveResult(
        schema=SOLVE_SCHEMA,
        session_id=session_id,
        project_root=str(root),
        workspace_root=str(workspace_root),
        package_path=package_path,
        problem=clean_problem,
        project_type=project_type,
        tool=tool,
        explicit_user_approval=allow_repair or suggest_only,
        allow_verification_changes=allow_verification_changes,
        suggest_only=suggest_only,
    )

    if target_error:
        return _finish(result, "blocked", target_error, blocker="workspace_package_invalid")

    if not root.is_dir():
        return _finish(result, "blocked", "Project root does not exist.", blocker="project_root_missing")
    if not clean_problem:
        return _finish(result, "blocked", "A concrete problem statement is required.", blocker="problem_missing")
    if project_type not in SUPPORTED_PROJECT_TYPES:
        return _finish(
            result,
            "blocked",
            "Automatic solve supports Python and Node.js JavaScript/TypeScript projects.",
            blocker="unsupported_project_type",
        )
    if tool != "codex":
        return _finish(result, "blocked", f"Unsupported repair tool: {tool}", blocker="unsupported_repair_tool")
    if allow_repair and suggest_only:
        return _finish(
            result,
            "blocked",
            "--suggest-only cannot be combined with --allow-repair.",
            blocker="conflicting_repair_modes",
        )
    if allow_verification_changes and not allow_repair and not suggest_only:
        return _finish(
            result,
            "blocked",
            "--allow-verification-changes is valid only together with --allow-repair or --suggest-only.",
            blocker="verification_change_approval_requires_repair",
        )

    git_state = _inspect_git(root, expected_root=workspace_root)
    result.original_branch = git_state.get("branch")
    if git_state.get("error"):
        return _finish(result, "blocked", str(git_state["error"]), blocker="git_repository_required")
    # Dirty trees only block modes that create branches or apply edits.
    if (allow_repair or suggest_only) and git_state.get("dirty"):
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
    workspace_packages = discover_workspace_packages(root) if package is None else []
    if (
        project_type == "javascript"
        and workspace_packages
        and reproduce_command is None
        and test_command is None
        and [item.command for item in commands] == ["node --test"]
    ):
        result.warnings.append("Workspace packages: " + ", ".join(workspace_packages))
        return _finish(
            result,
            "blocked",
            "The workspace root has no unambiguous test command. Select a package with --package.",
            blocker="workspace_package_required",
        )
    if not commands:
        if project_type == "javascript" and workspace_packages and package is None:
            result.warnings.append("Workspace packages: " + ", ".join(workspace_packages))
            return _finish(
                result,
                "blocked",
                "The workspace root has no unambiguous test command. Select a package with --package.",
                blocker="workspace_package_required",
            )
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

    baseline_porcelain = str(git_state.get("porcelain") or "")
    baseline = _run_solve_commands(root, commands, command_timeout_seconds)
    result.baseline = [item.to_dict() for item in baseline]
    post_baseline_git = _inspect_git(root, expected_root=workspace_root)
    if post_baseline_git.get("error"):
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            str(post_baseline_git["error"]),
            blocker="git_repository_required",
        )
    if str(post_baseline_git.get("porcelain") or "") != baseline_porcelain:
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            "A reproduction or test command changed the Git working tree. Restore it before automatic repair.",
            blocker="checks_modified_worktree",
        )
    required_command_ids = {item.command_id for item in commands if item.required}
    unavailable_checks = [
        item for item in baseline if item.command_id in required_command_ids and item.return_code == 127
    ]
    if unavailable_checks:
        result.warnings.extend(
            f"{item.command_id}: {item.stderr.strip() or 'executable not found'}" for item in unavailable_checks
        )
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            "A required verification executable was not found. Install the project toolchain before automatic repair.",
            blocker="verification_tool_missing",
        )
    timed_out_checks = [item for item in baseline if item.command_id in required_command_ids and item.timed_out]
    if timed_out_checks:
        result.warnings.extend(f"{item.command_id}: command timed out" for item in timed_out_checks)
        return _persist_and_finish(
            result,
            output_root,
            "blocked",
            "A required baseline check timed out, so Doctor link could not prove the problem safely.",
            blocker="baseline_check_timed_out",
        )
    if _checks_passed(commands, baseline):
        result.next_steps.append("Confirm the problem statement and provide a command that fails when the problem is present.")
        return _persist_and_finish(
            result,
            output_root,
            "not_reproduced",
            "All independent checks already pass, so Doctor link did not authorize a repair.",
        )

    verification_snapshot = snapshot_verification_inputs(root, commands)
    result.protected_verification_inputs = sorted(verification_snapshot)
    result.verification_input_hashes = dict(sorted(verification_snapshot.items()))

    root_cause = analyze_root_cause(
        root,
        problem=clean_problem,
        checks=[item.to_dict() for item in baseline],
    )
    result.root_cause = root_cause.to_dict()
    if root_cause.status in {"explained", "partial"} and root_cause.hints:
        top = root_cause.hints[0]
        paths = ", ".join(top.get("candidate_paths") or []) or "unmapped"
        result.warnings.append(
            f"Advisory root-cause hint: {top.get('symbol')} → {paths} "
            f"(confidence {top.get('confidence')}; not verified)."
        )

    prompt = build_repair_prompt(result, baseline, round_number=1)
    if not allow_repair and not suggest_only:
        result.next_steps.append(
            f'doctor-link solve "{root}" --problem "{clean_problem}" --allow-repair'
        )
        result.next_steps.append(
            f'doctor-link solve "{root}" --problem "{clean_problem}" --suggest-only'
        )
        return _persist_and_finish(
            result,
            output_root,
            "approval_required",
            "The problem was reproduced. Review the solve plan, then rerun with --suggest-only for a branch + diff proposal or --allow-repair for verified repair.",
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
    branch_result = run_command(["git", "switch", "-c", repair_branch], cwd=workspace_root, timeout_seconds=30)
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
    result.status = "repairing"
    result.completed_at = None
    _write_session_files(session_dir, result)
    round_limit = 1 if suggest_only else min(3, max(1, max_rounds))
    return _run_repair_rounds(
        result,
        root,
        commands,
        verification_snapshot,
        executor,
        output_root=output_root,
        session_dir=session_dir,
        start_round=1,
        round_limit=round_limit,
        command_timeout_seconds=command_timeout_seconds,
        repair_timeout_seconds=repair_timeout_seconds,
        previous_verification=baseline,
        suggest_only=suggest_only,
    )


def _run_repair_rounds(
    result: SolveResult,
    root: Path,
    commands: list[SolveCommand],
    verification_snapshot: dict[str, str],
    executor: RepairExecutor,
    *,
    output_root: Path | None,
    session_dir: Path,
    start_round: int,
    round_limit: int,
    command_timeout_seconds: int,
    repair_timeout_seconds: int,
    previous_verification: list[SolveCommandResult],
    previous_message: str = "",
    suggest_only: bool = False,
) -> SolveResult:
    original_commit = run_command(["git", "rev-parse", "HEAD"], cwd=root, timeout_seconds=15)
    base_commit = original_commit.stdout.strip() if original_commit.returncode == 0 else None
    for round_number in range(start_round, round_limit + 1):
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
        pre_verification_snapshot = snapshot_verification_inputs(root, commands)
        pre_verification_changes = compare_verification_inputs(
            verification_snapshot,
            pre_verification_snapshot,
            round_number=round_number,
            detected_at="before_verification",
        )
        verification = (
            _run_solve_commands(root, commands, command_timeout_seconds)
            if not pre_verification_changes or result.allow_verification_changes or suggest_only
            else []
        )
        post_verification_changes = compare_verification_inputs(
            verification_snapshot,
            snapshot_verification_inputs(root, commands),
            round_number=round_number,
            detected_at="after_verification",
        )
        input_changes = _merge_verification_input_changes(
            pre_verification_changes,
            post_verification_changes,
        )
        if input_changes:
            result.verification_input_changes.extend(input_changes)
        checks_passed = _checks_passed(commands, verification)
        verified = checks_passed and not input_changes
        atomic_write_json(round_dir / "verification.json", [item.to_dict() for item in verification])
        atomic_write_json(round_dir / "verification-input-changes.json", input_changes)
        solve_round = SolveRound(
            round_number=round_number,
            repair=execution.to_dict(),
            verification=[item.to_dict() for item in verification],
            verified=verified,
            prompt_path=str(prompt_path),
            events_path=str(events_path),
            stderr_path=str(stderr_path),
            verification_input_changes=input_changes,
        )
        result.rounds.append(solve_round.to_dict())
        if base_commit:
            receipt = build_change_receipt(
                root,
                base_ref=base_commit,
                head_ref="HEAD",  # includes uncommitted repair edits in the working tree
                protected_paths=result.protected_verification_inputs,
                verification_input_changes=result.verification_input_changes,
            )
            result.change_receipt = receipt.to_dict()
            atomic_write_json(round_dir / "change-receipt.json", receipt.to_dict())
            atomic_write_text(round_dir / "change-receipt.md", receipt_to_markdown(receipt))
            atomic_write_json(session_dir / "change-receipt.json", receipt.to_dict())
            atomic_write_text(session_dir / "change-receipt.md", receipt_to_markdown(receipt))
        _write_session_files(session_dir, result)

        if suggest_only:
            result.next_steps.extend(
                [
                    f"Review the proposed changes on branch `{result.repair_branch}`.",
                    f'doctor-link diff "{session_dir}"',
                    "This is not verified. Either review and independently test/commit the proposal, "
                    "or discard its working-tree edits before rerunning with --allow-repair.",
                ]
            )
            return _persist_and_finish(
                result,
                output_root,
                "suggestion_ready",
                "Doctor link reproduced the problem and produced a repair proposal with a structured change receipt. Independent verification was recorded for information only; the result is not verified.",
                session_dir=session_dir,
            )

        if input_changes and not result.allow_verification_changes:
            result.blockers.append("verification_inputs_modified")
            changed_paths = ", ".join(item["path"] for item in input_changes[:8])
            if len(input_changes) > 8:
                changed_paths += f", and {len(input_changes) - 8} more"
            result.warnings.append(f"Repair changed protected verification inputs: {changed_paths}")
            result.next_steps.append(
                "Restore the original verification inputs and repair production behavior, or explicitly rerun with "
                "--allow-verification-changes for a review-required result."
            )
            return _persist_and_finish(
                result,
                output_root,
                "blocked",
                "The repair changed protected verification inputs, so Doctor link refused to trust the altered acceptance contract.",
                session_dir=session_dir,
            )
        if checks_passed:
            result.next_steps.extend(
                [
                    f"Review the changes on branch `{result.repair_branch}`.",
                    f'doctor-link diff "{session_dir}"',
                    "Commit and push the repair only after reviewing the diff.",
                ]
            )
            if input_changes:
                result.next_steps.insert(
                    0,
                    "Review every verification-input change; this result is not equivalent to an unchanged-contract verification.",
                )
                return _persist_and_finish(
                    result,
                    output_root,
                    "review_required",
                    "All checks pass, but protected verification inputs changed under explicit authorization; human review is required.",
                    session_dir=session_dir,
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


def resume_solve_session(
    session_dir: Path,
    *,
    allow_repair: bool = False,
    max_rounds: int = 3,
    command_timeout_seconds: int = 120,
    repair_timeout_seconds: int = 900,
    repair_executor: RepairExecutor | None = None,
) -> SolveResult:
    """Continue an interrupted repair session without weakening its original contract."""
    directory = session_dir.expanduser().resolve()
    payload_path = directory / "solve-session.json"
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _resume_error(directory, f"Solve session could not be read: {exc}", "resume_session_invalid")
    if payload.get("schema") != SOLVE_SCHEMA:
        return _resume_error(directory, "Solve session schema is not resumable by this version.", "resume_schema_unsupported")
    stored = {key: value for key, value in payload.items() if key in SolveResult.__dataclass_fields__}
    result = SolveResult(**stored)
    result.output_dir = str(directory)
    if not allow_repair:
        return _finish(result, "approval_required", "Resume requires fresh explicit approval with --allow-repair.")
    if result.status not in {"repairing", "failed"}:
        return _persist_and_finish(
            result,
            None,
            "blocked",
            f"Session status {result.status!r} cannot be resumed.",
            blocker="resume_status_invalid",
            session_dir=directory,
        )
    root = Path(result.project_root).resolve()
    if not root.is_dir():
        return _persist_and_finish(
            result,
            None,
            "blocked",
            "The original project root no longer exists.",
            blocker="project_root_missing",
            session_dir=directory,
        )
    git_state = _inspect_git(root, expected_root=Path(result.workspace_root).resolve())
    if git_state.get("error") or git_state.get("branch") != result.repair_branch:
        return _persist_and_finish(
            result,
            None,
            "blocked",
            "Resume requires the original repair branch to be checked out.",
            blocker="resume_branch_mismatch",
            session_dir=directory,
        )
    commands = [SolveCommand(**item) for item in result.commands]
    snapshot = dict(result.verification_input_hashes)
    input_changes = compare_verification_inputs(
        snapshot,
        snapshot_verification_inputs(root, commands),
        round_number=len(result.rounds) + 1,
        detected_at="before_resume",
    )
    if input_changes and not result.allow_verification_changes:
        result.verification_input_changes.extend(input_changes)
        return _persist_and_finish(
            result,
            None,
            "blocked",
            "Protected verification inputs changed before resume.",
            blocker="verification_inputs_modified",
            session_dir=directory,
        )
    start_round = len(result.rounds) + 1
    round_limit = min(3, max(1, max_rounds))
    if start_round > round_limit:
        return _persist_and_finish(
            result,
            None,
            "blocked",
            "The session has no remaining repair rounds.",
            blocker="resume_round_limit_exhausted",
            session_dir=directory,
        )
    executor = repair_executor or CodexRepairExecutor()
    if isinstance(executor, CodexRepairExecutor) and not executor.available():
        return _persist_and_finish(
            result,
            None,
            "blocked",
            "Codex CLI was not found. Install or expose it before resuming.",
            blocker="codex_cli_missing",
            session_dir=directory,
        )
    previous_payload = result.rounds[-1]["verification"] if result.rounds else result.baseline
    previous_verification = [SolveCommandResult(**item) for item in previous_payload]
    previous_message = result.rounds[-1]["repair"].get("final_message", "") if result.rounds else ""
    result.status = "repairing"
    result.completed_at = None
    result.explicit_user_approval = True
    _write_session_files(directory, result)
    return _run_repair_rounds(
        result,
        root,
        commands,
        snapshot,
        executor,
        output_root=None,
        session_dir=directory,
        start_round=start_round,
        round_limit=round_limit,
        command_timeout_seconds=command_timeout_seconds,
        repair_timeout_seconds=repair_timeout_seconds,
        previous_verification=previous_verification,
        previous_message=previous_message,
    )


def _resume_error(directory: Path, summary: str, blocker: str) -> SolveResult:
    result = SolveResult(
        schema=SOLVE_SCHEMA,
        session_id="invalid",
        project_root="",
        workspace_root="",
        package_path=None,
        problem="",
        project_type="unsupported",
        tool="codex",
        output_dir=str(directory),
    )
    return _finish(result, "blocked", summary, blocker=blocker)


def resolve_solve_target(workspace_root: Path, package: str | Path | None) -> tuple[Path, str | None, str | None]:
    """Resolve an optional workspace package while preventing path escape."""
    workspace = workspace_root.expanduser().resolve()
    if package is None:
        return workspace, None, None
    raw = Path(package)
    if raw.is_absolute():
        return workspace, None, "--package must be a path relative to the workspace root."
    target = (workspace / raw).resolve()
    try:
        relative = target.relative_to(workspace)
    except ValueError:
        return workspace, None, "--package must stay inside the workspace root."
    if not target.is_dir():
        return target, relative.as_posix(), f"Workspace package does not exist: {relative.as_posix()}"
    return target, relative.as_posix(), None


def discover_workspace_packages(project_root: Path) -> list[str]:
    """Return package directories declared by npm/Yarn/pnpm-style workspaces."""
    root = project_root.expanduser().resolve()
    patterns: list[str] = []
    package_path = root / "package.json"
    if package_path.is_file():
        try:
            payload = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        workspaces = payload.get("workspaces") if isinstance(payload, dict) else None
        if isinstance(workspaces, list):
            patterns.extend(str(item) for item in workspaces)
        elif isinstance(workspaces, dict) and isinstance(workspaces.get("packages"), list):
            patterns.extend(str(item) for item in workspaces["packages"])
    pnpm_workspace = root / "pnpm-workspace.yaml"
    if pnpm_workspace.is_file():
        try:
            import yaml

            payload = yaml.safe_load(pnpm_workspace.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("packages"), list):
            patterns.extend(str(item) for item in payload["packages"])
    packages: set[str] = set()
    for pattern in patterns:
        if pattern.startswith("!") or Path(pattern).is_absolute() or ".." in Path(pattern).parts:
            continue
        for candidate in root.glob(pattern):
            if candidate.is_dir() and (candidate / "package.json").is_file() and "node_modules" not in candidate.parts:
                packages.add(candidate.relative_to(root).as_posix())
    return sorted(packages)


def detect_project_type(project_root: Path) -> str:
    root = project_root.expanduser().resolve()
    if not root.is_dir():
        return "unsupported"
    python_markers = [root / "pyproject.toml", root / "setup.py", root / "setup.cfg", root / "requirements.txt"]
    if any(path.is_file() for path in python_markers):
        return "python"
    if (root / "package.json").is_file():
        return "javascript"
    common_python_sources = [root / "src", root / "app", root / "tests"]
    if (
        any(root.glob("*.py"))
        or any(source.is_dir() and next(source.rglob("*.py"), None) is not None for source in common_python_sources)
    ):
        return "python"
    if any(path.suffix.lower() in JAVASCRIPT_EXTENSIONS for path in root.iterdir() if path.is_file()):
        return "javascript"
    if any(_contains_javascript_source(source) for source in (root / "src", root / "app", root / "lib")):
        return "javascript"
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
        if not matrix.jobs:
            project_type = detect_project_type(project_root)
            if project_type == "python" and (project_root / "tests").is_dir():
                commands.append(SolveCommand("test-pytest", "test", "python -m pytest"))
            elif project_type == "javascript":
                javascript_command = _discover_javascript_test_command(project_root)
                if javascript_command:
                    commands.append(SolveCommand("test-javascript", "test", javascript_command))
    return _dedupe_commands(commands)


def _discover_javascript_test_command(project_root: Path) -> str | None:
    package_path = project_root / "package.json"
    package_payload: dict[str, Any] = {}
    if package_path.is_file():
        try:
            loaded = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = {}
        if isinstance(loaded, dict):
            package_payload = loaded

    scripts = package_payload.get("scripts")
    test_script = scripts.get("test") if isinstance(scripts, dict) else None
    if isinstance(test_script, str) and test_script.strip() and "no test specified" not in test_script.lower():
        manager = _javascript_package_manager(project_root, package_payload)
        return {
            "bun": "bun run test",
            "npm": "npm test",
            "pnpm": "pnpm test",
            "yarn": "yarn test",
        }[manager]

    if any(
        path.suffix.lower() in {".cjs", ".js", ".mjs"}
        and (".test." in path.name or ".spec." in path.name)
        for path in _iter_project_files(project_root)
    ):
        return "node --test"
    return None


def _javascript_package_manager(project_root: Path, package_payload: dict[str, Any]) -> str:
    declared = str(package_payload.get("packageManager") or "").partition("@")[0].lower()
    if declared in {"bun", "npm", "pnpm", "yarn"}:
        return declared
    if (project_root / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (project_root / "yarn.lock").is_file():
        return "yarn"
    if (project_root / "bun.lock").is_file() or (project_root / "bun.lockb").is_file():
        return "bun"
    return "npm"


def _contains_javascript_source(directory: Path) -> bool:
    return directory.is_dir() and any(path.suffix.lower() in JAVASCRIPT_EXTENSIONS for path in _iter_project_files(directory))


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
    protected_summary = [
        f"- Doctor link snapshotted {len(result.protected_verification_inputs)} protected verification input(s).",
    ]
    if result.allow_verification_changes:
        protected_summary.append(
            "- Verification-input changes were explicitly allowed, but avoid them unless essential and explain every change."
        )
    else:
        protected_summary.append(
            "- Do not modify tests, package manifests or lockfiles, test configuration, reproduction/test catalogs, "
            "or scripts referenced by verification commands."
        )
    compact_protected = _compact_protected_paths(result.protected_verification_inputs)
    if compact_protected:
        protected_summary.append("- Protected inputs (patterns): " + ", ".join(f"`{item}`" for item in compact_protected))
    if result.allow_verification_changes:
        protected_summary.append(
            "- The user explicitly allowed verification-input changes, but any passing result will still require human review."
        )
    root_cause_section = _format_root_cause_prompt_section(result.root_cause)
    sections = [
        "# Doctor link bounded automatic repair",
        "",
        f"Repair round: {round_number}",
        f"Project root: {result.project_root}",
        f"Project type: {result.project_type}",
        f"Problem: {result.problem}",
        previous,
        "## Independent failing evidence",
        "",
        *evidence,
        "",
    ]
    if root_cause_section:
        sections.extend([root_cause_section.rstrip(), ""])
    sections.extend(
        [
            "## Required behavior",
            "",
            *protected_summary,
            "- Inspect the repository and identify the grounded root cause. Use any advisory hints above only as starting points.",
            "- Make the smallest production-quality change that fixes the stated problem without weakening its acceptance contract.",
            "- Stay inside this workspace. Do not switch branches, commit, push, publish, or change Git configuration.",
            "- Preserve unrelated behavior and existing user changes.",
            "- You may run focused tests, but Doctor link will independently rerun every command above.",
            "- Do not claim success merely because a patch was written; finish with the root cause, changed files, risks, and tests run.",
            "- If the issue cannot be safely fixed, stop and explain the concrete blocker instead of fabricating success.",
            "",
        ]
    )
    return "\n".join(sections)


def _compact_protected_paths(paths: list[str], *, max_items: int = 12) -> list[str]:
    """Collapse long protected-path lists into readable globs for repair prompts."""
    if not paths:
        return []
    buckets: dict[str, list[str]] = {}
    singles: list[str] = []
    for path in sorted(paths):
        normalized = path.replace("\\", "/")
        parts = normalized.split("/")
        if len(parts) >= 2 and parts[0] in {"tests", "test", "__tests__", "spec"}:
            buckets.setdefault(f"{parts[0]}/**", []).append(normalized)
        elif len(parts) >= 2 and parts[0] in {"src", "lib", "app", "packages"}:
            # Keep package-level roots compact when many files share a prefix.
            prefix = "/".join(parts[:2]) + "/**"
            buckets.setdefault(prefix, []).append(normalized)
        else:
            singles.append(normalized)
    compact: list[str] = []
    for pattern, members in sorted(buckets.items()):
        if len(members) >= 3:
            compact.append(pattern)
        else:
            compact.extend(members)
    compact.extend(singles)
    # Prefer globs first, then keep the list bounded.
    compact = sorted(set(compact), key=lambda item: (0 if "*" in item else 1, item))
    if len(compact) > max_items:
        remaining = len(compact) - (max_items - 1)
        compact = compact[: max_items - 1] + [f"... and {remaining} more protected paths"]
    return compact


def _format_root_cause_prompt_section(root_cause: dict[str, Any] | None) -> str:
    if not root_cause:
        return ""
    status = str(root_cause.get("status") or "")
    hints = list(root_cause.get("hints") or [])
    if status not in {"explained", "partial"} or not hints:
        return ""
    lines = [
        "## Suspected root cause (advisory only)",
        "",
        str(root_cause.get("summary") or "Heuristic source hints are available."),
        "",
        "These hints are heuristic. Verify against the failing evidence before editing.",
        "",
    ]
    for index, hint in enumerate(hints[:5], start=1):
        if not isinstance(hint, dict):
            continue
        paths = ", ".join(f"`{path}`" for path in (hint.get("candidate_paths") or [])[:4]) or "no local path mapped"
        lines.append(
            f"{index}. **{hint.get('symbol', 'unknown')}** "
            f"(confidence {hint.get('confidence', 0):.2f}, evidence {hint.get('evidence_count', 0)}): "
            f"{hint.get('rationale', '')} Inspect: {paths}."
        )
        for location in (hint.get("locations") or [])[:2]:
            lines.append(
                f"   - Location: `{location.get('path')}:{location.get('line') or '?'}` "
                f"in `{location.get('function') or 'unknown'}`."
            )
        for evidence in (hint.get("evidence") or [])[:3]:
            lines.append(f"   - Evidence: {evidence}")
    failures = list(root_cause.get("failures") or [])
    if failures:
        lines.extend(["", "Structured failure facts:"])
        for failure in failures[:3]:
            lines.append(
                f"- Test `{failure.get('test') or 'unknown'}`: expected "
                f"`{failure.get('expected') or 'unknown'}`, actual `{failure.get('actual') or 'unknown'}`."
            )
    chains = list(root_cause.get("call_chains") or [])
    if chains:
        lines.extend(["", "Project-owned call paths:"])
        for chain in chains[:3]:
            nodes = chain.get("nodes") or []
            rendered = " → ".join(
                f"{node.get('path')}:{node.get('line') or '?'}:{node.get('function') or 'unknown'}"
                for node in nodes[:8]
            )
            if rendered:
                lines.append(f"- {rendered}")
    patterns = list(root_cause.get("failure_patterns") or [])
    if patterns:
        lines.extend(["", "Observed failure patterns:", *[f"- {item}" for item in patterns[:5]]])
    lines.append("")
    return "\n".join(lines)


def _run_solve_commands(root: Path, commands: list[SolveCommand], timeout_seconds: int) -> list[SolveCommandResult]:
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


def snapshot_verification_inputs(root: Path, commands: list[SolveCommand]) -> dict[str, str]:
    """Hash files that define the acceptance contract for this solve session."""
    paths = _discover_verification_input_paths(root, commands)
    snapshot: dict[str, str] = {}
    for path in sorted(paths, key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        try:
            snapshot[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            snapshot[relative] = "unreadable"
    return snapshot


def compare_verification_inputs(
    baseline: dict[str, str],
    current: dict[str, str],
    *,
    round_number: int,
    detected_at: str,
) -> list[dict[str, Any]]:
    """Return structured added, deleted, and modified acceptance inputs."""
    changes: list[dict[str, Any]] = []
    for path in sorted(set(baseline) | set(current)):
        before = baseline.get(path)
        after = current.get(path)
        if before == after:
            continue
        change_type = "added" if before is None else ("deleted" if after is None else "modified")
        changes.append(
            {
                "round_number": round_number,
                "detected_at": detected_at,
                "path": path,
                "change_type": change_type,
                "before_sha256": before,
                "after_sha256": after,
            }
        )
    return changes


def _merge_verification_input_changes(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for group in groups:
        for item in group:
            key = (
                item.get("path"),
                item.get("change_type"),
                item.get("before_sha256"),
                item.get("after_sha256"),
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def _discover_verification_input_paths(root: Path, commands: list[SolveCommand]) -> set[Path]:
    paths: set[Path] = set()
    for relative in VERIFICATION_CONFIG_PATHS | VERIFICATION_CATALOG_PATHS:
        candidate = root / relative
        if candidate.is_file():
            paths.add(candidate)

    for directory_name in VERIFICATION_TEST_DIRECTORIES:
        directory = root / directory_name
        if directory.is_dir():
            paths.update(path for path in _iter_project_files(directory) if _is_protected_file(root, path))

    for path in _iter_project_files(root):
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in (*VERIFICATION_TEST_PATTERNS, *VERIFICATION_CONFIG_PATTERNS)):
            paths.add(path)

    for command in commands:
        try:
            segments = parse_safe_command_sequence(command.command)
        except ValueError:
            continue
        for segment in segments:
            paths.update(_command_referenced_paths(root, segment.argv))
    return paths


def _iter_project_files(root: Path):
    for directory, directory_names, file_names in os.walk(root):
        directory_names[:] = [name for name in directory_names if name not in IGNORED_VERIFICATION_PARTS]
        base = Path(directory)
        for file_name in file_names:
            yield base / file_name


def _is_protected_file(root: Path, path: Path) -> bool:
    if not path.is_file() or path.suffix in {".pyc", ".pyo"}:
        return False
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return not any(part in IGNORED_VERIFICATION_PARTS for part in relative.parts)


def _command_referenced_paths(root: Path, argv: list[str]) -> set[Path]:
    referenced: set[Path] = set()
    for raw_token in argv:
        token = raw_token.split("::", 1)[0]
        if not token or token.startswith("-"):
            continue
        candidate = Path(token).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            candidate = candidate.resolve()
            candidate.relative_to(root)
        except (OSError, ValueError):
            continue
        if candidate.is_file():
            referenced.add(candidate)

    if "-m" in argv:
        index = argv.index("-m")
        if index + 1 < len(argv):
            module_name = argv[index + 1]
            if module_name not in {"pytest", "unittest"}:
                module_path = root.joinpath(*module_name.split("."))
                for candidate in (module_path.with_suffix(".py"), module_path / "__main__.py"):
                    if candidate.is_file():
                        referenced.add(candidate.resolve())
    return referenced


def _checks_passed(commands: list[SolveCommand], results: list[SolveCommandResult]) -> bool:
    required_ids = {item.command_id for item in commands if item.required}
    return bool(required_ids) and all(
        item.status == "passed" for item in results if item.command_id in required_ids
    )


def _inspect_git(root: Path, *, expected_root: Path | None = None) -> dict[str, Any]:
    top = run_command(["git", "rev-parse", "--show-toplevel"], cwd=root, timeout_seconds=15)
    if top.returncode != 0:
        return {"error": "Automatic repair requires a Git repository."}
    top_level = Path(top.stdout.strip()).resolve()
    expected = (expected_root or root).resolve()
    if top_level != expected:
        return {"error": f"Use the Git repository root as PROJECT_ROOT: {top_level}"}
    branch = run_command(["git", "branch", "--show-current"], cwd=root, timeout_seconds=15)
    status = run_command(["git", "status", "--porcelain"], cwd=root, timeout_seconds=15)
    if branch.returncode != 0 or status.returncode != 0:
        return {"error": "Doctor link could not inspect the Git working tree."}
    porcelain = status.stdout
    return {
        "branch": branch.stdout.strip() or "DETACHED",
        "dirty": bool(porcelain.strip()),
        "porcelain": porcelain,
    }


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
        f"- Workspace: `{result.workspace_root}`",
        f"- Package: `{result.package_path or 'workspace root'}`",
        f"- Project type: `{result.project_type}`",
        f"- Tool: `{result.tool}`",
        f"- Explicit repair approval: `{str(result.explicit_user_approval).lower()}`",
        f"- Verification-input changes allowed: `{str(result.allow_verification_changes).lower()}`",
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
    if result.protected_verification_inputs:
        lines.extend(
            [
                "",
                "## Protected verification inputs",
                "",
                *[f"- `{item}`" for item in result.protected_verification_inputs],
            ]
        )
    if result.verification_input_changes:
        lines.extend(
            [
                "",
                "## Verification input changes",
                "",
                *[
                    f"- Round {item['round_number']}: `{item['path']}` ({item['change_type']})"
                    for item in result.verification_input_changes
                ],
            ]
        )
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
