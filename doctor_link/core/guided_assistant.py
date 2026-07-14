from __future__ import annotations

import hashlib
import html
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text
from doctor_link.core.reproduction_suggester import ReproductionSuggestionResult, suggest_reproductions
from doctor_link.core.root_cause import analyze_root_cause
from doctor_link.core.solve import SolveResult, resolve_solve_target, solve_project


GUIDED_SCHEMA = "doctor-link-guided-session-v1"


@dataclass
class GuidedSessionResult:
    schema: str
    session_id: str
    project_root: str
    package_path: str | None
    problem: str
    status: str
    started_at: str
    completed_at: str
    reproduction: dict[str, Any]
    solve: dict[str, Any] | None
    output_dir: str
    result_page: str
    next_steps: list[str] = field(default_factory=list)
    root_cause: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_guided_session(
    project_root: Path,
    *,
    problem: str,
    package: str | Path | None = None,
    output_root: Path | None = None,
    allow_repair: bool = False,
    command_timeout_seconds: int = 120,
    repair_timeout_seconds: int = 900,
) -> GuidedSessionResult:
    workspace = project_root.expanduser().resolve()
    target, package_path, target_error = resolve_solve_target(workspace, package)
    clean_problem = problem.strip()
    session_id = hashlib.sha256(f"{workspace}:{package_path}:{clean_problem}:{utc_now_iso()}".encode()).hexdigest()[:12]
    output = (output_root or workspace.parent / "DoctorReports" / workspace.name / "guided").expanduser().resolve()
    session_dir = output / f"guided-{session_id}"
    session_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now_iso()

    if target_error:
        reproduction = ReproductionSuggestionResult(
            schema="doctor-link-reproduction-suggestions-v1",
            project_root=str(target),
            problem=clean_problem,
            project_type="unsupported",
            status="blocked",
            selected_command=None,
            suggestions=[],
            warnings=[target_error],
        )
    else:
        reproduction = suggest_reproductions(
            target,
            clean_problem,
            validate=True,
            timeout_seconds=command_timeout_seconds,
        )

    solve: SolveResult | None = None
    next_steps: list[str] = []
    root_cause: dict[str, Any] = {}
    if reproduction.status == "reproduced" and reproduction.selected_command:
        solve = solve_project(
            workspace,
            package=package,
            problem=clean_problem,
            reproduce_command=reproduction.selected_command,
            output_root=session_dir / "solve",
            allow_repair=allow_repair,
            command_timeout_seconds=command_timeout_seconds,
            repair_timeout_seconds=repair_timeout_seconds,
        )
        status = solve.status
        next_steps.extend(solve.next_steps)
        root_cause = dict(solve.root_cause or {})
        if not root_cause:
            failed_suggestions = [
                item
                for item in reproduction.suggestions
                if item.get("status") in {"reproduced", "setup_failed", "failed"}
            ]
            root_cause = analyze_root_cause(
                target,
                problem=clean_problem,
                checks=failed_suggestions or reproduction.suggestions,
            ).to_dict()
        if root_cause.get("status") in {"explained", "partial"} and root_cause.get("hints"):
            top = root_cause["hints"][0]
            paths = ", ".join(top.get("candidate_paths") or []) or "unmapped"
            next_steps.insert(
                0,
                f"Advisory root-cause hint: inspect {top.get('symbol')} in {paths} "
                f"(confidence {top.get('confidence')}; not verified).",
            )
    else:
        status = reproduction.status
        if status == "not_reproduced":
            next_steps.append("Add observable steps or a failing example, then run the guided assistant again.")
        else:
            next_steps.append("Review the environment and candidate warnings before retrying.")
            failed_suggestions = [
                item
                for item in reproduction.suggestions
                if item.get("status") in {"setup_failed", "failed", "reproduced"}
            ]
            if failed_suggestions:
                root_cause = analyze_root_cause(
                    target,
                    problem=clean_problem,
                    checks=failed_suggestions,
                ).to_dict()

    result_page = session_dir / "index.html"
    result = GuidedSessionResult(
        schema=GUIDED_SCHEMA,
        session_id=session_id,
        project_root=str(workspace),
        package_path=package_path,
        problem=clean_problem,
        status=status,
        started_at=started_at,
        completed_at=utc_now_iso(),
        reproduction=reproduction.to_dict(),
        solve=solve.to_dict() if solve else None,
        output_dir=str(session_dir),
        result_page=str(result_page),
        next_steps=next_steps,
        root_cause=root_cause,
    )
    atomic_write_json(session_dir / "guided-session.json", result.to_dict())
    atomic_write_text(result_page, render_guided_result(result))
    return result


def render_guided_result(result: GuidedSessionResult) -> str:
    reproduction = result.reproduction
    suggestion_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('status', 'proposed')))}</td>"
        f"<td>{html.escape(str(item.get('return_code', '')))}</td>"
        f"<td><code>{html.escape(str(item.get('command', '')))}</code></td>"
        f"<td>{html.escape(str(item.get('rationale', '')))}</td>"
        f"<td><pre>{html.escape(_snippet(item))}</pre></td>"
        "</tr>"
        for item in reproduction.get("suggestions", [])
    ) or '<tr><td colspan="5">No safe candidate was available.</td></tr>'
    warning_items = "".join(f"<li>{html.escape(str(item))}</li>" for item in reproduction.get("warnings", [])) or "<li>None</li>"
    step_items = "".join(f"<li>{html.escape(item)}</li>" for item in result.next_steps) or "<li>Review the result.</li>"
    solve = result.solve or {}
    repair_branch = solve.get("repair_branch") or "Not created"
    selected = reproduction.get("selected_command") or "None"
    summary = solve.get("summary") or _plain_summary(result.status)
    root_cause = result.root_cause or solve.get("root_cause") or {}
    hint_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
        f"<td>{html.escape(str(item.get('confidence', '')))}</td>"
        f"<td>{html.escape(str(item.get('evidence_count', '')))}</td>"
        f"<td><code>{html.escape(', '.join(item.get('candidate_paths') or []) or '(unmapped)')}</code></td>"
        f"<td>{html.escape(str(item.get('rationale', '')))}</td>"
        "</tr>"
        for item in (root_cause.get("hints") or [])
    ) or '<tr><td colspan="5">No advisory root-cause hint was generated.</td></tr>'
    root_summary = html.escape(str(root_cause.get("summary") or "Not available."))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Doctor link guided result</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f4f7fb;color:#14213d;margin:0}}
main{{max-width:1080px;margin:0 auto;padding:32px 20px 64px}}section{{background:#fff;border:1px solid #dbe4f0;border-radius:14px;padding:22px;margin:16px 0;box-shadow:0 8px 24px #183b6610}}
.status{{display:inline-block;background:#e8f1ff;color:#124a8a;border-radius:999px;padding:6px 12px;font-weight:700}}.muted{{color:#5f6f82}}code,pre{{word-break:break-word;white-space:pre-wrap;font-size:12px}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #e5ebf3;padding:10px;text-align:left;vertical-align:top}}
</style></head><body><main>
<h1>Doctor link guided diagnosis</h1><p class="muted">No test-command knowledge required. Results remain local.</p>
<section><span class="status">{html.escape(result.status)}</span><h2>{html.escape(result.problem)}</h2><p>{html.escape(str(summary))}</p>
<p><strong>Selected reproduction:</strong> <code>{html.escape(str(selected))}</code></p>
<p><strong>Repair branch:</strong> {html.escape(str(repair_branch))}</p></section>
<section><h2>What Doctor link tried</h2><table><thead><tr><th>Outcome</th><th>Exit</th><th>Check</th><th>Why</th><th>Evidence snippet</th></tr></thead><tbody>{suggestion_rows}</tbody></table></section>
<section><h2>Suspected root cause <span class="muted">(advisory)</span></h2>
<p>{root_summary}</p>
<table><thead><tr><th>Symbol</th><th>Confidence</th><th>Evidence</th><th>Paths</th><th>Why</th></tr></thead><tbody>{hint_rows}</tbody></table>
<p class="muted">Hints narrow inspection only. Doctor link still verifies repairs independently.</p></section>
<section><h2>Warnings</h2><ul>{warning_items}</ul></section>
<section><h2>Next steps</h2><ol>{step_items}</ol></section>
<section><h2>Local receipt</h2><p><code>{html.escape(result.output_dir)}</code></p>
<p class="muted">Open the solve session directory for full stdout/stderr, prompts, and verification receipts when present.</p></section>
</main></body></html>"""


def _snippet(item: dict[str, Any], *, limit: int = 500) -> str:
    text = "\n".join(
        part for part in (str(item.get("stderr") or "").strip(), str(item.get("stdout") or "").strip()) if part
    )
    if not text:
        return "No output captured."
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _plain_summary(status: str) -> str:
    return {
        "blocked": "Doctor link could not safely continue.",
        "not_reproduced": "The available checks pass, so the reported problem was not reproduced.",
        "proposed": "Candidate checks were generated but not executed.",
        "reproduced": "The reported problem was reproduced.",
        "approval_required": "The problem was reproduced. Review the plan before authorizing repair.",
        "setup_failed": "Candidate checks failed during environment or collection setup.",
    }.get(status, "The guided session completed.")
