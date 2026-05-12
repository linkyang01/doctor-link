from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    """Return a stable UTC timestamp for reports and JSON payloads."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    """Create a compact unique identifier with a readable prefix."""
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class LibraryFile:
    path: Path
    root: Path
    size_bytes: int

    @property
    def relative_path(self) -> str:
        return str(self.path.relative_to(self.root))

    @property
    def extension(self) -> str:
        return self.path.suffix.lower().lstrip(".")


@dataclass
class ScanResult:
    root: Path
    files: list[LibraryFile] = field(default_factory=list)


@dataclass
class TestPlan:
    title: str
    missing_categories: list[str]
    recommended_tests: list[str]
    detected_extensions: dict[str, int]

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        lines.append("## Detected extensions")
        if self.detected_extensions:
            for extension, count in sorted(self.detected_extensions.items()):
                lines.append(f"- `{extension}`: {count}")
        else:
            lines.append("- No files detected")
        lines.append("")
        lines.append("## Missing categories")
        for category in self.missing_categories or ["None"]:
            lines.append(f"- {category}")
        lines.append("")
        lines.append("## Recommended tests")
        for test in self.recommended_tests or ["No test generated"]:
            lines.append(f"- {test}")
        lines.append("")
        return "\n".join(lines)


@dataclass
class EvidenceItem:
    """A single piece of evidence used for diagnosis."""

    evidence_id: str = field(default_factory=lambda: new_id("evd"))
    kind: str = "note"
    title: str = "Evidence"
    source: str = "manual"
    path: str | None = None
    content: str | None = None
    related_step_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TimelineStep:
    """A user action, system event, or diagnostic step."""

    step_id: str = field(default_factory=lambda: new_id("step"))
    order: int = 0
    action: str = "observe"
    target: str | None = None
    expected_result: str | None = None
    actual_result: str | None = None
    status: str = "unknown"
    timestamp: str = field(default_factory=utc_now_iso)
    evidence_ids: list[str] = field(default_factory=list)
    is_failure_point: bool = False
    user_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UserAssertion:
    """A human-confirmed problem signal.

    This is a first-class diagnostic input. AI tasks must not dismiss it
    as normal behavior without evidence.
    """

    assertion_id: str = field(default_factory=lambda: new_id("assert"))
    report_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    severity: str = "error"
    user_statement: str = ""
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    why_user_thinks_it_is_wrong: str | None = None
    related_step_id: str | None = None
    related_evidence_ids: list[str] = field(default_factory=list)
    related_file: str | None = None
    ai_disagreed_or_missed: bool = False
    investigation_scope: list[str] = field(default_factory=list)
    locked_scope: list[str] = field(default_factory=list)
    next_ai_instruction: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProblemMap:
    """Human-readable map of a problem."""

    user_symptom: str = ""
    failure_stage: str = "unknown"
    possible_root_causes: list[str] = field(default_factory=list)
    ruled_out_causes: list[str] = field(default_factory=list)
    related_modules: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    human_confirmed_problem: str | None = None
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AITask:
    """A task package intended for AI coding tools."""

    title: str = "AI Debugging Task"
    summary: str = ""
    requested_work: list[str] = field(default_factory=list)
    investigation_boundary: list[str] = field(default_factory=list)
    do_not_change: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    user_assertion_ids: list[str] = field(default_factory=list)
    verification_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationChecklist:
    """Steps required to prove a fix worked."""

    checklist_id: str = field(default_factory=lambda: new_id("verify"))
    title: str = "Fix Verification Checklist"
    items: list[str] = field(default_factory=list)
    before_report: str | None = None
    after_report: str | None = None
    status: str = "draft"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosticEvent:
    """The core diagnostic event for one issue or failure."""

    event_id: str = field(default_factory=lambda: new_id("event"))
    project: str = "unknown"
    adapter: str = "generic"
    occurred_at: str = field(default_factory=utc_now_iso)
    severity: str = "error"
    category: str = "unknown_issue"
    summary: str = ""
    environment: dict[str, Any] = field(default_factory=dict)
    timeline: list[TimelineStep] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    reproduce_steps: list[str] = field(default_factory=list)
    user_assertions: list[UserAssertion] = field(default_factory=list)
    problem_map: ProblemMap = field(default_factory=ProblemMap)
    ai_task: AITask = field(default_factory=AITask)
    verification_checklist: VerificationChecklist = field(default_factory=VerificationChecklist)
    status: str = "draft"

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "timeline": [step.to_dict() for step in self.timeline],
            "evidence": [item.to_dict() for item in self.evidence],
            "user_assertions": [item.to_dict() for item in self.user_assertions],
            "problem_map": self.problem_map.to_dict(),
            "ai_task": self.ai_task.to_dict(),
            "verification_checklist": self.verification_checklist.to_dict(),
        }


@dataclass
class DiagnosticPackage:
    """A generated diagnostic package on disk."""

    package_id: str = field(default_factory=lambda: new_id("pkg"))
    event_id: str = ""
    root_dir: Path | None = None
    status: str = "draft"
    files: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.root_dir is not None:
            payload["root_dir"] = str(self.root_dir)
        return payload
