"""Reversible counterfactual checks for advisory root-cause candidates."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from doctor_link.core.command_runner import run_command
from doctor_link.core.safe_command_runner import run_safe_command_sequence


@dataclass
class HypothesisVerification:
    status: str
    candidate_path: str | None
    summary: str
    baseline_failed: int = 0
    experiment_passed: int = 0
    commands: list[dict[str, Any]] = field(default_factory=list)
    restored: bool = False
    worktree_unchanged: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_top_hypothesis(
    root: Path,
    *,
    hints: Sequence[Mapping[str, Any]],
    commands: Sequence[Mapping[str, Any]],
    baseline: Sequence[Mapping[str, Any]],
    timeout_seconds: int,
) -> HypothesisVerification:
    """Temporarily restore one changed candidate to HEAD and rerun failing checks.

    This is deliberately conservative: only the first ranked, tracked file that
    differs from HEAD is eligible. Original bytes are restored in ``finally``.
    """
    candidate = _top_candidate(hints)
    if candidate is None:
        return _unavailable(None, "No ranked source-file candidate is available for a safe experiment.")
    target = root / candidate
    if not target.is_file() or not _is_changed_tracked_file(root, candidate):
        return _unavailable(candidate, "The top candidate is not a tracked file changed relative to Git HEAD.")

    failing_ids = {
        str(item.get("command_id"))
        for item in baseline
        if item.get("return_code") not in (0, None) and not item.get("timed_out")
    }
    selected = [item for item in commands if str(item.get("command_id")) in failing_ids]
    if not selected:
        return _unavailable(candidate, "No deterministic failing check is available for the experiment.")

    original = target.read_bytes()
    head = run_command(["git", "show", f"HEAD:{candidate}"], cwd=root, timeout_seconds=30)
    if head.returncode != 0:
        return _unavailable(candidate, "The candidate cannot be read from Git HEAD.")
    before = _worktree_fingerprint(root)
    results: list[dict[str, Any]] = []
    restored = False
    try:
        target.write_bytes(head.stdout.encode("utf-8", errors="surrogateescape"))
        for item in selected:
            completed = run_safe_command_sequence(
                str(item.get("command") or ""),
                cwd=root,
                timeout_seconds=timeout_seconds,
                environment_overrides={"CI": "1", "NO_COLOR": "1", "PYTHONDONTWRITEBYTECODE": "1"},
            )
            results.append(
                {
                    "command_id": item.get("command_id"),
                    "command": item.get("command"),
                    "return_code": completed.returncode,
                    "status": "timed_out" if completed.timed_out else ("passed" if completed.returncode == 0 else "failed"),
                    "timed_out": completed.timed_out,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            )
    finally:
        target.write_bytes(original)
        restored = target.read_bytes() == original

    after = _worktree_fingerprint(root)
    unchanged = before is not None and after is not None and before == after
    if not restored or not unchanged:
        return HypothesisVerification(
            status="unsafe_to_test",
            candidate_path=candidate,
            summary="The experiment could not prove complete worktree restoration; inspect the repository before continuing.",
            baseline_failed=len(selected),
            experiment_passed=sum(item["return_code"] == 0 for item in results),
            commands=results,
            restored=restored,
            worktree_unchanged=unchanged,
            warnings=["Do not trust the hypothesis result until the worktree is reviewed."],
        )
    if any(item["timed_out"] for item in results):
        status = "inconclusive"
        summary = "At least one counterfactual check timed out, so the hypothesis remains unconfirmed."
    elif results and all(item["return_code"] == 0 for item in results):
        status = "confirmed"
        summary = f"Restoring `{candidate}` to Git HEAD made every previously failing check pass."
    elif any(item["return_code"] == 0 for item in results):
        status = "supported"
        summary = f"Restoring `{candidate}` fixed some, but not all, previously failing checks."
    else:
        status = "rejected"
        summary = f"Restoring `{candidate}` did not make any previously failing check pass."
    return HypothesisVerification(
        status=status,
        candidate_path=candidate,
        summary=summary,
        baseline_failed=len(selected),
        experiment_passed=sum(item["return_code"] == 0 for item in results),
        commands=results,
        restored=restored,
        worktree_unchanged=unchanged,
    )


def _top_candidate(hints: Sequence[Mapping[str, Any]]) -> str | None:
    for hint in hints[:1]:
        paths = list(hint.get("candidate_paths") or [])
        if paths:
            return str(paths[0])
    return None


def _is_changed_tracked_file(root: Path, path: str) -> bool:
    tracked = run_command(["git", "ls-files", "--error-unmatch", "--", path], cwd=root, timeout_seconds=15)
    changed = run_command(["git", "diff", "--quiet", "HEAD", "--", path], cwd=root, timeout_seconds=15)
    return tracked.returncode == 0 and changed.returncode == 1


def _unavailable(path: str | None, summary: str) -> HypothesisVerification:
    return HypothesisVerification(status="unavailable", candidate_path=path, summary=summary)


def _worktree_fingerprint(root: Path) -> str | None:
    diff = run_command(["git", "diff", "--no-ext-diff", "--binary", "HEAD"], cwd=root, timeout_seconds=30)
    untracked = run_command(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, timeout_seconds=15)
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


__all__ = ["HypothesisVerification", "verify_top_hypothesis"]
