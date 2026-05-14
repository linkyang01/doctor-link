from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import ScanResult

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


def _extension(path: str) -> str:
    return Path(path).suffix.lower().lstrip(".")
