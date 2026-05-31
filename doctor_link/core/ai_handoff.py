from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso

SUPPORTED_TOOLS = {"codex", "cursor", "continue", "aider", "openhands", "claude-code", "generic"}
HANDOFF_FILES = [
    "ai-task.md",
    "ai-context.json",
    "evidence-list.md",
    "user-assertions.json",
    "investigation-boundary.md",
    "fix-verification-checklist.md",
]
DEFAULT_OPTIONAL_FILES = [
    "doctor-report.json",
    "verification-result.json",
    "verification-plan.md",
    "report-comparison.json",
    "report-comparison.md",
    "assertion-compliance-report.json",
    "repair-risk-review.json",
    "diagnosis-history.json",
    "ai-repair-result.json",
]
SENSITIVE_PATTERNS = [
    ("possible_secret", re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("email_address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
]


@dataclass
class HandoffProfile:
    tool: str
    display_name: str
    instruction_file: str
    notes: list[str] = field(default_factory=list)
    preferred_context: str = "markdown-json"
    supports_file_tree: bool = True
    supports_terminal_commands: bool = True
    supports_patch_workflow: bool = True
    max_recommended_files: int = 32
    required_files: list[str] = field(default_factory=lambda: list(HANDOFF_FILES))
    optional_files: list[str] = field(default_factory=lambda: list(DEFAULT_OPTIONAL_FILES))
    file_globs_allowed: list[str] = field(default_factory=lambda: ["*.md", "*.json", "evidence/**/*.txt", "evidence/**/*.log", "evidence/**/*.json", "evidence/**/*.csv", "evidence/**/*.yaml", "evidence/**/*.yml"])
    file_globs_denied: list[str] = field(default_factory=lambda: ["*.zip", "*.tar", "*.gz", "*.png", "*.jpg", "*.jpeg", "*.mp4", "*.mov", "*.bin"])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HandoffCompatibilityReport:
    tool: str
    status: str
    required_missing: list[str] = field(default_factory=list)
    optional_missing: list[str] = field(default_factory=list)
    included_files: list[str] = field(default_factory=list)
    skipped_files: list[dict[str, str]] = field(default_factory=list)
    missing_evidence_warnings: list[str] = field(default_factory=list)
    privacy_warnings: list[str] = field(default_factory=list)
    guidance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HandoffPackage:
    tool: str
    output_dir: str
    manifest_path: str
    instruction_path: str
    included_files: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    compatibility_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PROFILES: dict[str, HandoffProfile] = {
    "codex": HandoffProfile(
        "codex",
        "Codex",
        "CODEX_TASK.md",
        [
            "Use this as a coding-agent task with explicit verification before closure.",
            "Prefer small, reviewable patches and cite evidence IDs in the final repair note.",
        ],
        preferred_context="repository-task",
        max_recommended_files=40,
    ),
    "cursor": HandoffProfile(
        "cursor",
        "Cursor",
        "CURSOR_TASK.md",
        [
            "Attach or reference the copied package files in Cursor chat.",
            "Open the source files mentioned in the investigation boundary before editing.",
        ],
        preferred_context="chat-plus-workspace",
        max_recommended_files=28,
    ),
    "continue": HandoffProfile(
        "continue",
        "Continue",
        "CONTINUE_TASK.md",
        [
            "Use the task with Continue and cite package evidence.",
            "Keep the context concise if Continue is running with a smaller context window.",
        ],
        preferred_context="ide-context",
        max_recommended_files=24,
    ),
    "aider": HandoffProfile(
        "aider",
        "Aider",
        "AIDER_TASK.md",
        [
            "Use the task as repair context before editing files.",
            "Add only the source files needed for the bounded change to the Aider session.",
        ],
        preferred_context="terminal-patch",
        max_recommended_files=20,
    ),
    "openhands": HandoffProfile(
        "openhands",
        "OpenHands",
        "OPENHANDS_TASK.md",
        [
            "Use the task as the agent objective and keep boundaries explicit.",
            "Require the agent to run verification commands before marking success.",
        ],
        preferred_context="agent-objective",
        max_recommended_files=40,
    ),
    "claude-code": HandoffProfile(
        "claude-code",
        "Claude Code",
        "CLAUDE_CODE_TASK.md",
        [
            "Use this task as the Claude Code session objective.",
            "Ask Claude Code to inspect evidence first, then patch only files inside the investigation boundary.",
        ],
        preferred_context="agentic-cli",
        max_recommended_files=32,
    ),
    "generic": HandoffProfile(
        "generic",
        "Generic Markdown/JSON",
        "AI_HANDOFF_TASK.md",
        ["Use this package with any AI Coding tool."],
        preferred_context="markdown-json",
        max_recommended_files=32,
    ),
}


def get_handoff_profile(tool: str) -> HandoffProfile:
    tool_key = tool.lower().strip()
    if tool_key not in PROFILES:
        raise ValueError(f"Unsupported handoff tool: {tool}. Supported tools: {', '.join(sorted(SUPPORTED_TOOLS))}")
    return PROFILES[tool_key]


def build_handoff_package(package_dir: Path, tool: str = "generic", output_dir: Path | None = None) -> HandoffPackage:
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")
    profile = get_handoff_profile(tool)
    tool_key = profile.tool
    out = output_dir or package_dir / "ai-handoff" / tool_key
    out.mkdir(parents=True, exist_ok=True)

    compatibility = check_handoff_compatibility(package_dir, tool_key)
    included: list[str] = []
    missing: list[str] = []
    skipped: list[dict[str, str]] = []
    for relative in _candidate_handoff_files(package_dir, profile):
        source = package_dir / relative
        if not source.exists():
            if relative in profile.required_files:
                missing.append(relative)
            continue
        allowed, reason = _allowed_by_profile(relative, profile)
        if not allowed:
            skipped.append({"path": relative, "reason": reason})
            continue
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        included.append(relative)

    compatibility.included_files = included
    compatibility.skipped_files.extend(skipped)
    compatibility.required_missing = [item for item in profile.required_files if not (package_dir / item).exists()]
    compatibility.optional_missing = [item for item in profile.optional_files if not (package_dir / item).exists()]
    compatibility.status = _compatibility_status(compatibility)

    instruction = _render_instruction(package_dir, profile, included, missing or compatibility.required_missing, compatibility)
    instruction_path = out / profile.instruction_file
    instruction_path.write_text(instruction, encoding="utf-8")
    compatibility_path = out / "handoff-compatibility.json"
    compatibility_path.write_text(json.dumps(compatibility.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "tool": tool_key,
        "display_name": profile.display_name,
        "profile": profile.to_dict(),
        "source_package": str(package_dir),
        "instruction_file": profile.instruction_file,
        "included_files": included,
        "missing_files": missing or compatibility.required_missing,
        "optional_missing_files": compatibility.optional_missing,
        "skipped_files": compatibility.skipped_files,
        "compatibility_status": compatibility.status,
        "compatibility_file": "handoff-compatibility.json",
        "missing_evidence_warnings": compatibility.missing_evidence_warnings,
        "privacy_warnings": compatibility.privacy_warnings,
        "notes": profile.notes,
        "human_assertion_rule": "Do not dismiss user-confirmed problems as normal behavior without evidence.",
    }
    manifest_path = out / "handoff-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return HandoffPackage(tool_key, str(out), str(manifest_path), str(instruction_path), included, missing or compatibility.required_missing, str(compatibility_path))


def check_handoff_compatibility(package_dir: Path, tool: str = "generic") -> HandoffCompatibilityReport:
    profile = get_handoff_profile(tool)
    report = HandoffCompatibilityReport(tool=profile.tool, status="ready")
    report.required_missing = [item for item in profile.required_files if not (package_dir / item).exists()]
    report.optional_missing = [item for item in profile.optional_files if not (package_dir / item).exists()]
    report.missing_evidence_warnings = _missing_evidence_warnings(package_dir)
    report.privacy_warnings = _privacy_warnings(package_dir, profile)
    report.guidance = _profile_guidance(profile)
    report.status = _compatibility_status(report)
    return report


def add_ai_result(
    package_dir: Path,
    summary: str,
    claimed_fix: str = "",
    files_changed: list[str] | None = None,
    evidence_used: list[str] | None = None,
    related_assertion_ids: list[str] | None = None,
    verification_steps: list[str] | None = None,
    risks: list[str] | None = None,
    assumptions: list[str] | None = None,
    repair_session_id: str | None = None,
    tool: str = "generic",
) -> dict[str, Any]:
    package_dir = package_dir.resolve()
    items = _load_list(package_dir / "ai-repair-result.json")
    session_id = repair_session_id or _next_repair_session_id(package_dir)
    record = {
        "result_id": f"ai_result_{len(items) + 1:03d}",
        "repair_session_id": session_id,
        "tool": tool,
        "summary": summary,
        "claimed_fix": claimed_fix,
        "files_changed": files_changed or [],
        "evidence_used": evidence_used or [],
        "related_assertion_ids": related_assertion_ids or [],
        "verification_steps": verification_steps or [],
        "risks": risks or [],
        "assumptions": assumptions or [],
        "verified": False,
        "created_at": utc_now_iso(),
        "notice": "Run verification before closing.",
    }
    items.append(record)
    (package_dir / "ai-repair-result.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "ai-repair-result.md").write_text(_md("AI Repair Results", items), encoding="utf-8")
    _upsert_repair_session(package_dir, session_id, tool, record)
    _report_update(package_dir, "ai_repair_results", items)
    _report_update(package_dir, "ai_repair_sessions", _load_list(package_dir / "ai-repair-sessions.json"))
    return record


def add_history_round(
    package_dir: Path,
    ai_pass: str = "",
    user_correction: str = "",
    evidence_added: list[str] | None = None,
    verification_attempt: str = "",
    repair_session_id: str | None = None,
    tool: str = "generic",
) -> dict[str, Any]:
    package_dir = package_dir.resolve()
    items = _load_list(package_dir / "diagnosis-history.json")
    session_id = repair_session_id or _latest_or_next_repair_session_id(package_dir)
    record = {
        "round_id": f"round_{len(items) + 1:03d}",
        "repair_session_id": session_id,
        "tool": tool,
        "ai_pass": ai_pass,
        "user_correction": user_correction,
        "evidence_added": evidence_added or [],
        "verification_attempt": verification_attempt,
        "created_at": utc_now_iso(),
    }
    items.append(record)
    (package_dir / "diagnosis-history.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "diagnosis-history.md").write_text(_md("Diagnosis History", items), encoding="utf-8")
    _append_session_round(package_dir, session_id, tool, record)
    _report_update(package_dir, "diagnosis_history", items)
    _report_update(package_dir, "ai_repair_sessions", _load_list(package_dir / "ai-repair-sessions.json"))
    return record


def build_assertion_compliance(package_dir: Path) -> dict[str, Any]:
    assertions = _load_any(package_dir / "user-assertions.json", [])
    results = _load_list(package_dir / "ai-repair-result.json")
    ids = [_assertion_id(item, i) for i, item in enumerate(assertions if isinstance(assertions, list) else [], start=1)]
    covered = sorted({str(value) for item in results for value in (item.get("related_assertion_ids") or [])})
    missing = [value for value in ids if value not in covered]
    report = {"status": "needs_attention" if missing else "covered", "assertion_ids": ids, "covered_assertion_ids": covered, "missing_assertion_ids": missing}
    (package_dir / "assertion-compliance-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "assertion-compliance-report.md").write_text(_md("Assertion Compliance Report", [report]), encoding="utf-8")
    _report_update(package_dir, "assertion_compliance", report)
    return report


def build_risk_review(package_dir: Path, files_changed: list[str] | None = None, boundary: list[str] | None = None, risk_level: str = "unknown") -> dict[str, Any]:
    files = files_changed or []
    allowed = boundary or []
    outside = [item for item in files if allowed and not any(item.startswith(prefix) for prefix in allowed)]
    report = {"risk_level": "high" if outside else risk_level, "files_changed": files, "boundary": allowed, "outside_boundary": outside}
    (package_dir / "repair-risk-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "repair-risk-review.md").write_text(_md("Repair Risk Review", [report]), encoding="utf-8")
    _report_update(package_dir, "repair_risk_review", report)
    return report


def _render_instruction(package_dir: Path, profile: HandoffProfile, included: list[str], missing: list[str], compatibility: HandoffCompatibilityReport) -> str:
    ai_task = _read(package_dir / "ai-task.md", "Missing ai-task.md")
    boundary = _read(package_dir / "investigation-boundary.md", "Missing investigation-boundary.md")
    checklist = _read(package_dir / "fix-verification-checklist.md", "Missing fix-verification-checklist.md")
    evidence = _read(package_dir / "evidence-list.md", "Missing evidence-list.md")
    assertions = _read(package_dir / "user-assertions.json", "Missing user-assertions.json")
    included_lines = [f"- {item}" for item in included] if included else ["- None"]
    missing_lines = [f"- {item}" for item in missing] if missing else ["- None"]
    note_lines = [f"- {note}" for note in profile.notes]
    privacy_lines = [f"- {item}" for item in compatibility.privacy_warnings] if compatibility.privacy_warnings else ["- None detected in copied text candidates. Still review before external sharing."]
    missing_evidence_lines = [f"- {item}" for item in compatibility.missing_evidence_warnings] if compatibility.missing_evidence_warnings else ["- None detected."]
    guidance_lines = [f"- {item}" for item in compatibility.guidance]
    lines = [
        f"# Doctor link Handoff for {profile.display_name}",
        "",
        "## Compatibility status",
        compatibility.status,
        "",
        "## Required rule",
        "The human user has confirmed one or more issues. Do not dismiss user-confirmed problems as normal behavior without evidence.",
        "",
        "## Tool-specific guidance",
        *note_lines,
        *guidance_lines,
        "- Use the copied package files as diagnostic context.",
        "- Do not claim the fix is complete until verification evidence supports it.",
        "",
        "## File inclusion policy",
        f"- Preferred context: {profile.preferred_context}",
        f"- Maximum recommended files: {profile.max_recommended_files}",
        "- Denied large/binary file patterns are not copied into the handoff folder.",
        "",
        "## Included files",
        *included_lines,
        "",
        "## Missing files",
        *missing_lines,
        "",
        "## Missing evidence warnings",
        *missing_evidence_lines,
        "",
        "## Privacy warnings",
        *privacy_lines,
        "",
        "## AI task",
        ai_task,
        "",
        "## Investigation boundary",
        boundary,
        "",
        "## Verification checklist",
        checklist,
        "",
        "## Evidence list",
        evidence,
        "",
        "## User assertions",
        assertions,
        "",
    ]
    return "\n".join(lines)


def _candidate_handoff_files(package_dir: Path, profile: HandoffProfile) -> list[str]:
    candidates: list[str] = []
    for item in [*profile.required_files, *profile.optional_files]:
        if item not in candidates:
            candidates.append(item)
    evidence = _load_any(package_dir / "doctor-report.json", {})
    if isinstance(evidence, dict):
        for item in evidence.get("evidence", []) if isinstance(evidence.get("evidence"), list) else []:
            if isinstance(item, dict) and item.get("path"):
                path = str(item["path"]).replace("\\", "/")
                if path.startswith("evidence/") and path not in candidates:
                    candidates.append(path)
    return candidates[: profile.max_recommended_files]


def _allowed_by_profile(relative: str, profile: HandoffProfile) -> tuple[bool, str]:
    path = Path(relative)
    suffix = path.suffix.lower()
    denied_suffixes = {".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".mp4", ".mov", ".bin"}
    if suffix in denied_suffixes:
        return False, "denied_binary_or_archive"
    if relative.startswith("evidence/") and suffix not in {".txt", ".log", ".json", ".md", ".csv", ".yaml", ".yml"}:
        return False, "unsupported_evidence_type"
    return True, "allowed"


def _missing_evidence_warnings(package_dir: Path) -> list[str]:
    warnings: list[str] = []
    verification = _load_any(package_dir / "verification-result.json", {})
    if isinstance(verification, dict):
        for item in verification.get("missing_evidence", []) if isinstance(verification.get("missing_evidence"), list) else []:
            warnings.append(f"verification-result missing evidence: {item}")
        for item in verification.get("tests_to_rerun", []) if isinstance(verification.get("tests_to_rerun"), list) else []:
            warnings.append(f"verification requires rerun: {item}")
    if not (package_dir / "evidence-list.md").exists():
        warnings.append("evidence-list.md is missing")
    return warnings


def _privacy_warnings(package_dir: Path, profile: HandoffProfile) -> list[str]:
    warnings: list[str] = []
    for relative in _candidate_handoff_files(package_dir, profile):
        source = package_dir / relative
        if not source.is_file() or source.stat().st_size > 512_000:
            continue
        try:
            text = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for label, pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                warnings.append(f"{label} pattern detected in {relative}")
    return sorted(set(warnings))


def _profile_guidance(profile: HandoffProfile) -> list[str]:
    guidance = [
        f"Target profile: {profile.display_name}.",
        f"Preferred context mode: {profile.preferred_context}.",
    ]
    if profile.supports_terminal_commands:
        guidance.append("The target tool can be asked to run verification commands, but successful command output must be captured before closure.")
    if profile.supports_patch_workflow:
        guidance.append("Ask for patch-level changes and require a concise verification summary.")
    return guidance


def _compatibility_status(report: HandoffCompatibilityReport) -> str:
    if report.required_missing:
        return "blocked_missing_required_files"
    if report.missing_evidence_warnings or report.privacy_warnings:
        return "needs_review"
    return "ready"


def _next_repair_session_id(package_dir: Path) -> str:
    sessions = _load_list(package_dir / "ai-repair-sessions.json")
    return f"repair_session_{len(sessions) + 1:03d}"


def _latest_or_next_repair_session_id(package_dir: Path) -> str:
    sessions = _load_list(package_dir / "ai-repair-sessions.json")
    if sessions:
        return str(sessions[-1].get("repair_session_id") or sessions[-1].get("session_id") or _next_repair_session_id(package_dir))
    return _next_repair_session_id(package_dir)


def _upsert_repair_session(package_dir: Path, session_id: str, tool: str, ai_result: dict[str, Any]) -> None:
    sessions = _load_list(package_dir / "ai-repair-sessions.json")
    session = next((item for item in sessions if item.get("repair_session_id") == session_id), None)
    if session is None:
        session = {
            "repair_session_id": session_id,
            "tool": tool,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "ai_result_ids": [],
            "history_round_ids": [],
            "status": "open_verification_required",
        }
        sessions.append(session)
    session.setdefault("ai_result_ids", [])
    if ai_result["result_id"] not in session["ai_result_ids"]:
        session["ai_result_ids"].append(ai_result["result_id"])
    session["updated_at"] = utc_now_iso()
    session["status"] = "open_verification_required"
    (package_dir / "ai-repair-sessions.json").write_text(json.dumps(sessions, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "ai-repair-sessions.md").write_text(_md("AI Repair Sessions", sessions), encoding="utf-8")


def _append_session_round(package_dir: Path, session_id: str, tool: str, history_round: dict[str, Any]) -> None:
    sessions = _load_list(package_dir / "ai-repair-sessions.json")
    session = next((item for item in sessions if item.get("repair_session_id") == session_id), None)
    if session is None:
        session = {
            "repair_session_id": session_id,
            "tool": tool,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "ai_result_ids": [],
            "history_round_ids": [],
            "status": "open_verification_required",
        }
        sessions.append(session)
    session.setdefault("history_round_ids", [])
    if history_round["round_id"] not in session["history_round_ids"]:
        session["history_round_ids"].append(history_round["round_id"])
    session["updated_at"] = utc_now_iso()
    (package_dir / "ai-repair-sessions.json").write_text(json.dumps(sessions, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "ai-repair-sessions.md").write_text(_md("AI Repair Sessions", sessions), encoding="utf-8")


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_list(path: Path) -> list[dict[str, Any]]:
    data = _load_any(path, [])
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return [data] if isinstance(data, dict) else []


def _md(title: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# {title}", ""]
    for item in items:
        lines.append(f"## {item.get('result_id') or item.get('round_id') or item.get('repair_session_id') or 'record'}")
        for key, value in item.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines)


def _report_update(package_dir: Path, key: str, value: Any) -> None:
    path = package_dir / "doctor-report.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data[key] = value
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _assertion_id(item: Any, index: int) -> str:
    if isinstance(item, dict):
        return str(item.get("assertion_id") or item.get("id") or f"assertion-{index}")
    return f"assertion-{index}"


def _read(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")
