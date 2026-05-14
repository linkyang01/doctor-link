from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import EvidenceItem, ScanResult, TimelineStep

VLY_MEDIA_EXTENSIONS = {
    "mp4",
    "m4v",
    "mov",
    "mkv",
    "avi",
    "ts",
    "m2ts",
    "mts",
    "webm",
    "wmv",
    "flv",
    "mpg",
    "mpeg",
    "vob",
}

VLY_SUBTITLE_EXTENSIONS = {"srt", "ass", "ssa", "vtt", "sub", "idx", "sup"}
VLY_AUDIO_EXTENSIONS = {"aac", "ac3", "dts", "flac", "m4a", "mp3", "opus", "wav"}
VLY_DISC_MARKERS = {"bdmv", "video_ts"}


@dataclass
class VlyCoreProofCase:
    """One Vly Core Proof capability that should be evidenced."""

    case_id: str
    title: str
    required: bool = True
    evidence_hint: str = ""
    matched_files: list[str] = field(default_factory=list)
    status: str = "missing"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VlyCoreProofReport:
    """Vly-specific proof report built from a scanned test library."""

    library_root: str
    cases: list[VlyCoreProofCase]
    go_no_go: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "library_root": self.library_root,
            "cases": [case.to_dict() for case in self.cases],
            "go_no_go": self.go_no_go,
            "reason": self.reason,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Vly Core Proof Report",
            "",
            f"- Library root: `{self.library_root}`",
            f"- Go / No-Go: `{self.go_no_go}`",
            f"- Reason: {self.reason}",
            "",
            "## Test matrix",
            "",
        ]
        for case in self.cases:
            matched = ", ".join(case.matched_files[:5]) if case.matched_files else "None"
            lines.extend(
                [
                    f"### {case.case_id}: {case.title}",
                    "",
                    f"- Required: `{case.required}`",
                    f"- Status: `{case.status}`",
                    f"- Evidence hint: {case.evidence_hint}",
                    f"- Matched files: {matched}",
                    "",
                ]
            )
        return "\n".join(lines)


def build_vly_core_proof_matrix(scan_result: ScanResult) -> VlyCoreProofReport:
    """Build a Vly Core Proof report from a scanned test library.

    This adapter does not decide playback success. It checks whether the evidence
    library contains the minimum sample categories needed before real playback
    tests and user-confirmed results can be recorded.
    """
    cases = _default_cases()
    relative_files = [item.relative_path for item in scan_result.files]

    for case in cases:
        case.matched_files = _match_case(case.case_id, relative_files)
        case.status = "ready" if case.matched_files else "missing"

    missing_required = [case for case in cases if case.required and case.status == "missing"]
    if missing_required:
        return VlyCoreProofReport(
            library_root=str(scan_result.root),
            cases=cases,
            go_no_go="NO-GO",
            reason="Missing required Vly Core Proof sample categories: "
            + ", ".join(case.case_id for case in missing_required),
        )

    return VlyCoreProofReport(
        library_root=str(scan_result.root),
        cases=cases,
        go_no_go="GO",
        reason="All required Vly Core Proof sample categories are present for playback validation.",
    )


def write_vly_core_proof_to_package(package_dir: Path, report: VlyCoreProofReport) -> EvidenceItem:
    """Write a Vly Core Proof report into an existing diagnostic package.

    The proof report is stored as evidence and reflected in the timeline and AI
    task. It is still a readiness signal, not proof of playback success.
    """
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    evidence_dir = package_dir / "evidence" / "test-results"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / "vly-core-proof.json"
    md_path = evidence_dir / "vly-core-proof.md"
    json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")

    evidence = EvidenceItem(
        kind="vly_core_proof",
        title="Vly Core Proof readiness report",
        source="doctor-link vly-proof",
        path=str(json_path.relative_to(package_dir)),
        content=f"Go / No-Go: {report.go_no_go}\nReason: {report.reason}",
    )
    step = TimelineStep(
        order=_next_order(package_dir),
        action="vly_core_proof",
        target=report.library_root,
        expected_result="Required Vly Core Proof sample categories are present before playback validation.",
        actual_result=f"{report.go_no_go}: {report.reason}",
        status="passed" if report.go_no_go == "GO" else "failed",
        evidence_ids=[evidence.evidence_id],
        is_failure_point=report.go_no_go != "GO",
        user_note="This is a readiness check, not proof that playback succeeded.",
    )

    _update_report_json(package_dir, report, evidence, step)
    _append_evidence_markdown(package_dir, evidence, md_path.relative_to(package_dir))
    _append_timeline_markdown(package_dir, step)
    _append_ai_task(package_dir, report, evidence)
    _append_summary(package_dir, report)
    return evidence


def _default_cases() -> list[VlyCoreProofCase]:
    return [
        VlyCoreProofCase(
            case_id="basic_video_playback",
            title="Basic video playback sample exists",
            evidence_hint="Provide at least one common video sample such as mp4, mov, or mkv.",
        ),
        VlyCoreProofCase(
            case_id="high_complexity_container",
            title="High-complexity container sample exists",
            evidence_hint="Provide a complex container such as mkv, m2ts, ts, or vob.",
        ),
        VlyCoreProofCase(
            case_id="external_subtitle",
            title="External subtitle sample exists",
            evidence_hint="Provide external subtitle files such as srt, ass, vtt, sup, idx/sub.",
        ),
        VlyCoreProofCase(
            case_id="audio_track_sample",
            title="Audio track evidence exists",
            evidence_hint="Provide standalone or associated audio samples such as ac3, dts, flac, aac, mp3.",
        ),
        VlyCoreProofCase(
            case_id="disc_structure",
            title="Disc structure evidence exists",
            evidence_hint="Provide BDMV or VIDEO_TS structure evidence for original-disc playback testing.",
            required=False,
        ),
    ]


def _match_case(case_id: str, relative_files: list[str]) -> list[str]:
    if case_id == "basic_video_playback":
        return [path for path in relative_files if _extension(path) in VLY_MEDIA_EXTENSIONS]
    if case_id == "high_complexity_container":
        return [path for path in relative_files if _extension(path) in {"mkv", "m2ts", "ts", "vob"}]
    if case_id == "external_subtitle":
        return [path for path in relative_files if _extension(path) in VLY_SUBTITLE_EXTENSIONS]
    if case_id == "audio_track_sample":
        return [path for path in relative_files if _extension(path) in VLY_AUDIO_EXTENSIONS]
    if case_id == "disc_structure":
        return [path for path in relative_files if any(part.lower() in VLY_DISC_MARKERS for part in Path(path).parts)]
    return []


def _update_report_json(
    package_dir: Path,
    report: VlyCoreProofReport,
    evidence: EvidenceItem,
    step: TimelineStep,
) -> None:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    payload["vly_core_proof"] = report.to_dict()
    payload.setdefault("evidence", []).append(evidence.to_dict())
    payload.setdefault("timeline", []).append(step.to_dict())

    ai_task = payload.setdefault("ai_task", {})
    ai_task.setdefault("evidence_ids", []).append(evidence.evidence_id)
    if report.go_no_go != "GO":
        ai_task.setdefault("requested_work", []).append(
            "Do not start playback-fix conclusions yet. First add the missing Vly Core Proof sample categories."
        )
    ai_task.setdefault("verification_steps", []).append(
        "Run `doctor-link vly-proof` again and confirm the readiness report is GO before playback validation."
    )
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_evidence_markdown(package_dir: Path, evidence: EvidenceItem, markdown_path: Path) -> None:
    _append(
        package_dir / "evidence-list.md",
        "\n".join(
            [
                f"\n## {evidence.title}",
                "",
                f"- ID: `{evidence.evidence_id}`",
                f"- Kind: `{evidence.kind}`",
                f"- Source: `{evidence.source}`",
                f"- JSON Path: `{evidence.path}`",
                f"- Markdown Path: `{markdown_path}`",
                "",
                evidence.content or "No content preview.",
                "",
            ]
        ),
    )


def _append_timeline_markdown(package_dir: Path, step: TimelineStep) -> None:
    marker = " **Failure point**" if step.is_failure_point else ""
    _append(
        package_dir / "timeline.md",
        "\n".join(
            [
                f"\n## Step {step.order}: {step.action}{marker}",
                "",
                f"- Time: `{step.timestamp}`",
                f"- Target: `{step.target or 'N/A'}`",
                f"- Status: `{step.status}`",
                f"- Expected: {step.expected_result or 'N/A'}",
                f"- Actual: {step.actual_result or 'N/A'}",
                f"- Evidence: {', '.join(step.evidence_ids)}",
                f"- User note: {step.user_note or 'N/A'}",
                "",
            ]
        ),
    )


def _append_ai_task(package_dir: Path, report: VlyCoreProofReport, evidence: EvidenceItem) -> None:
    lines = [
        "\n## Vly Core Proof readiness evidence",
        "",
        f"- Go / No-Go: `{report.go_no_go}`",
        f"- Reason: {report.reason}",
        f"- Evidence: `{evidence.evidence_id}`",
        "- Boundary: This readiness report does not prove playback success. Playback success must be recorded separately with `doctor-link record`.",
    ]
    if report.go_no_go != "GO":
        lines.append("- Instruction: Add missing sample categories before asking AI to diagnose playback failures.")
    _append(package_dir / "ai-task.md", "\n".join(lines) + "\n")


def _append_summary(package_dir: Path, report: VlyCoreProofReport) -> None:
    _append(
        package_dir / "summary.md",
        f"\n## Vly Core Proof readiness\n\n- Go / No-Go: `{report.go_no_go}`\n- Reason: {report.reason}\n",
    )


def _next_order(package_dir: Path) -> int:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return 1
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 1
    orders = [item.get("order") for item in payload.get("timeline", []) if isinstance(item, dict)]
    numeric_orders = [item for item in orders if isinstance(item, int)]
    return max(numeric_orders, default=0) + 1


def _append(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(current.rstrip() + "\n" + text.lstrip("\n"), encoding="utf-8")


def _extension(path: str) -> str:
    return Path(path).suffix.lower().lstrip(".")
