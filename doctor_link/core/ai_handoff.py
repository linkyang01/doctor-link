from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_TOOLS = {"codex", "cursor", "continue", "aider", "openhands", "generic"}
HANDOFF_FILES = [
    "ai-task.md",
    "ai-context.json",
    "evidence-list.md",
    "user-assertions.json",
    "investigation-boundary.md",
    "fix-verification-checklist.md",
]


@dataclass
class HandoffProfile:
    tool: str
    display_name: str
    instruction_file: str
    notes: list[str] = field(default_factory=list)


@dataclass
class HandoffPackage:
    tool: str
    output_dir: str
    manifest_path: str
    instruction_path: str
    included_files: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PROFILES: dict[str, HandoffProfile] = {
    "codex": HandoffProfile("codex", "Codex", "CODEX_TASK.md", ["Paste the task into Codex and keep verification explicit."]),
    "cursor": HandoffProfile("cursor", "Cursor", "CURSOR_TASK.md", ["Attach or reference the copied package files in Cursor chat."]),
    "continue": HandoffProfile("continue", "Continue", "CONTINUE_TASK.md", ["Use the task with Continue and cite package evidence."]),
    "aider": HandoffProfile("aider", "Aider", "AIDER_TASK.md", ["Use the task as repair context before editing files."]),
    "openhands": HandoffProfile("openhands", "OpenHands", "OPENHANDS_TASK.md", ["Use the task as the agent objective and keep boundaries explicit."]),
    "generic": HandoffProfile("generic", "Generic Markdown/JSON", "AI_HANDOFF_TASK.md", ["Use this package with any AI Coding tool."]),
}


def build_handoff_package(package_dir: Path, tool: str = "generic", output_dir: Path | None = None) -> HandoffPackage:
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")
    tool_key = tool.lower().strip()
    if tool_key not in SUPPORTED_TOOLS:
        raise ValueError(f"Unsupported handoff tool: {tool}. Supported tools: {', '.join(sorted(SUPPORTED_TOOLS))}")
    profile = PROFILES[tool_key]
    out = output_dir or package_dir / "ai-handoff" / tool_key
    out.mkdir(parents=True, exist_ok=True)

    included: list[str] = []
    missing: list[str] = []
    for relative in HANDOFF_FILES:
        source = package_dir / relative
        target = out / relative
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            included.append(relative)
        else:
            missing.append(relative)

    instruction = _render_instruction(package_dir, profile, included, missing)
    instruction_path = out / profile.instruction_file
    instruction_path.write_text(instruction, encoding="utf-8")
    manifest = {
        "tool": tool_key,
        "display_name": profile.display_name,
        "source_package": str(package_dir),
        "instruction_file": profile.instruction_file,
        "included_files": included,
        "missing_files": missing,
        "notes": profile.notes,
        "human_assertion_rule": "Do not dismiss user-confirmed problems as normal behavior without evidence.",
    }
    manifest_path = out / "handoff-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return HandoffPackage(tool_key, str(out), str(manifest_path), str(instruction_path), included, missing)


def add_ai_result(package_dir: Path, summary: str, claimed_fix: str = "", files_changed: list[str] | None = None, evidence_used: list[str] | None = None, related_assertion_ids: list[str] | None = None, verification_steps: list[str] | None = None, risks: list[str] | None = None, assumptions: list[str] | None = None) -> dict[str, Any]:
    items = _load_list(package_dir / "ai-repair-result.json")
    record = {
        "result_id": f"ai_result_{len(items) + 1:03d}",
        "summary": summary,
        "claimed_fix": claimed_fix,
        "files_changed": files_changed or [],
        "evidence_used": evidence_used or [],
        "related_assertion_ids": related_assertion_ids or [],
        "verification_steps": verification_steps or [],
        "risks": risks or [],
        "assumptions": assumptions or [],
        "verified": False,
        "notice": "Run verification before closing.",
    }
    items.append(record)
    (package_dir / "ai-repair-result.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    (package_dir / "ai-repair-result.md").write_text(_md("AI Repair Results", items), encoding="utf-8")
    return record


def _render_instruction(package_dir: Path, profile: HandoffProfile, included: list[str], missing: list[str]) -> str:
    ai_task = _read(package_dir / "ai-task.md", "Missing ai-task.md")
    boundary = _read(package_dir / "investigation-boundary.md", "Missing investigation-boundary.md")
    checklist = _read(package_dir / "fix-verification-checklist.md", "Missing fix-verification-checklist.md")
    evidence = _read(package_dir / "evidence-list.md", "Missing evidence-list.md")
    assertions = _read(package_dir / "user-assertions.json", "Missing user-assertions.json")
    included_lines = [f"- {item}" for item in included] if included else ["- None"]
    missing_lines = [f"- {item}" for item in missing] if missing else ["- None"]
    note_lines = [f"- {note}" for note in profile.notes]
    lines = [f"# Doctor link Handoff for {profile.display_name}", "", "## Required rule", "The human user has confirmed one or more issues. Do not dismiss user-confirmed problems as normal behavior without evidence.", "", "## How to use", *note_lines, "- Use the copied package files as diagnostic context.", "- Do not claim the fix is complete until verification evidence supports it.", "", "## Included files", *included_lines, "", "## Missing files", *missing_lines, "", "## AI task", ai_task, "", "## Investigation boundary", boundary, "", "## Verification checklist", checklist, "", "## Evidence list", evidence, "", "## User assertions", assertions, ""]
    return "\n".join(lines)


def _load_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return [data] if isinstance(data, dict) else []


def _md(title: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# {title}", ""]
    for item in items:
        lines.append(f"## {item.get('result_id', 'record')}")
        for key, value in item.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines)


def _read(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")
