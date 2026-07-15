"""Evidence-bounded repair guidance built from structured diagnosis receipts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from doctor_link.core.command_runner import run_command


def build_repair_guidance(
    root: Path,
    *,
    analysis: Mapping[str, Any],
    hypothesis_verification: Mapping[str, Any] | None,
    commands: Sequence[Mapping[str, Any]],
    baseline: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    hints = list(analysis.get("hints") or [])
    top = hints[0] if hints else {}
    paths = list(top.get("candidate_paths") or [])
    candidate_path = str(paths[0]) if paths else None
    locations = list(top.get("locations") or [])
    location = next((item for item in locations if item.get("path") == candidate_path), locations[0] if locations else {})
    hypothesis = dict(hypothesis_verification or {})
    hypothesis_status = str(hypothesis.get("status") or "not_run")
    failed_ids = {
        str(item.get("command_id"))
        for item in baseline
        if item.get("return_code") not in (0, None)
    }
    focused = [str(item.get("command")) for item in commands if str(item.get("command_id")) in failed_ids]
    regression = [str(item.get("command")) for item in commands if item.get("command")]

    observed: list[str] = []
    for failure in list(analysis.get("failures") or [])[:5]:
        expected, actual = failure.get("expected"), failure.get("actual")
        if expected is not None or actual is not None:
            observed.append(f"Expected `{expected or 'unknown'}` but observed `{actual or 'unknown'}`.")
    if candidate_path:
        observed.extend(str(item) for item in top.get("evidence") or [])

    inferred = []
    if candidate_path:
        inferred.append(
            f"The first inspection candidate is `{candidate_path}` at line {location.get('line') or 'unknown'} "
            f"in `{location.get('function') or 'an unknown function'}`."
        )
    verified = []
    if hypothesis_status == "confirmed":
        verified.append("Restoring the candidate file to Git HEAD made every previously failing check pass.")
        verified.append("The experiment restored the original bytes and complete worktree fingerprint.")
    elif hypothesis_status == "supported":
        verified.append("The counterfactual fixed some, but not all, failing checks.")

    if hypothesis_status == "confirmed" and candidate_path:
        status = "actionable"
        risk = "medium"
        principle = (
            f"Review the changed hunk at `{candidate_path}:{location.get('line') or '?'}` and restore the behavior "
            "demonstrated by the passing Git-HEAD counterfactual with the smallest production-code change."
        )
    elif candidate_path:
        status = "review_required"
        risk = "high"
        principle = "Inspect the candidate and collect stronger evidence before editing; no counterfactual confirmed a fix."
    else:
        status = "insufficient_evidence"
        risk = "high"
        principle = "Obtain a project-owned stack frame or changed production candidate before proposing a code change."

    steps = []
    if candidate_path:
        steps.append(f"Inspect the current diff for `{candidate_path}` and the enclosing function.")
    steps.append(principle)
    if focused:
        steps.append("Run the focused failing command(s) after the change.")
    if regression:
        steps.append("Run the complete discovered regression command set before accepting the repair.")

    return {
        "schema": "doctor-link-repair-guidance-v1",
        "status": status,
        "candidate": {
            "path": candidate_path,
            "line": location.get("line"),
            "function": location.get("function"),
            "source": location.get("source"),
        },
        "diagnosis": {"observed_facts": _unique(observed), "inferences": inferred, "verified_evidence": verified},
        "recommended_change": {"principle": principle, "steps": steps, "current_diff_excerpt": _diff_excerpt(root, candidate_path)},
        "risk": {
            "level": risk,
            "reasons": [
                "Counterfactual verification operates at file scope, not individual-expression scope.",
                "A passing focused check does not replace the complete regression suite.",
            ],
        },
        "verification": {
            "focused_commands": _unique(focused),
            "full_regression_commands": _unique(regression),
        },
    }


def _diff_excerpt(root: Path, path: str | None) -> str | None:
    if not path:
        return None
    result = run_command(["git", "diff", "--unified=2", "HEAD", "--", path], cwd=root, timeout_seconds=15)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    lines = result.stdout.splitlines()
    excerpt = "\n".join(lines[:80])
    return excerpt + ("\n…" if len(lines) > 80 else "")


def _unique(items: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


__all__ = ["build_repair_guidance"]
