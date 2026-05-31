from __future__ import annotations

import hashlib
import json
import shutil
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from doctor_link.core.command_runner import run_command
from doctor_link.core.environment_collector import collect_environment
from doctor_link.core.log_collector import collect_log_files_with_manifest
from doctor_link.core.media_probe import probe_media, summarize_media_probe
from doctor_link.core.models import EvidenceItem, TimelineStep, utc_now_iso
from doctor_link.core.redactor import RedactionOptions, RedactionReport, redact_files, redact_text


@dataclass
class CollectionResult:
    package_dir: str
    collected_at: str = field(default_factory=utc_now_iso)
    evidence: list[EvidenceItem] = field(default_factory=list)
    timeline_steps: list[TimelineStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    redaction_report: dict[str, Any] | None = None
    integrity_report: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_dir": self.package_dir,
            "collected_at": self.collected_at,
            "evidence": [item.to_dict() for item in self.evidence],
            "timeline_steps": [item.to_dict() for item in self.timeline_steps],
            "warnings": self.warnings,
            "redaction_report": self.redaction_report,
            "integrity_report": self.integrity_report,
        }


def collect_into_package(
    package_dir: Path,
    project_root: Path | None = None,
    log_patterns: Sequence[str] | None = None,
    commands: Sequence[str] | None = None,
    probes: Sequence[Path] | None = None,
    attachments: Sequence[Path] | None = None,
    note: str | None = None,
    ffprobe_binary: str = "ffprobe",
    command_timeout_seconds: int = 30,
    redact: bool = True,
    redaction_options: RedactionOptions | None = None,
) -> CollectionResult:
    """Collect evidence and write it into an existing diagnostic package."""
    package_dir = package_dir.resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(f"Diagnostic package not found: {package_dir}")

    result = CollectionResult(package_dir=str(package_dir))
    redaction_report = RedactionReport()
    redaction_options = redaction_options or RedactionOptions()

    if project_root is not None:
        _collect_environment(package_dir, project_root, result)
    if log_patterns:
        _collect_logs(package_dir, log_patterns, result, redact, redaction_options, redaction_report)
    if commands:
        _collect_commands(package_dir, commands, command_timeout_seconds, result, redact, redaction_options, redaction_report, project_root)
    if probes:
        _collect_probes(package_dir, probes, ffprobe_binary, result)
    if attachments:
        _collect_attachments(package_dir, attachments, result)
    if note:
        result.warnings.append(f"User note: {note}")

    if redact:
        _write_redaction_report(package_dir, redaction_report, result)
    _write_collection_result(package_dir, result)
    _write_integrity_report(package_dir, result)
    _update_package_files(package_dir, result)
    return result


def _collect_environment(package_dir: Path, project_root: Path, result: CollectionResult) -> None:
    target = package_dir / "evidence" / "environment.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = collect_environment(project_root)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    evidence = EvidenceItem(
        kind="environment",
        title="Collected local environment",
        source="doctor-link collect",
        path=str(target.relative_to(package_dir)),
        content=f"Environment collected for project root: {project_root.resolve()}",
    )
    step = _step(
        package_dir,
        action="collect_environment",
        target=str(project_root.resolve()),
        expected="Environment can be captured as structured JSON.",
        actual=f"Wrote {target.relative_to(package_dir)} with project markers and tool availability.",
        status="passed",
        evidence=evidence,
    )
    result.evidence.append(evidence)
    result.timeline_steps.append(step)


def _collect_logs(
    package_dir: Path,
    patterns: Sequence[str],
    result: CollectionResult,
    redact: bool,
    redaction_options: RedactionOptions,
    redaction_report: RedactionReport,
) -> None:
    target_dir = package_dir / "evidence" / "logs"
    log_result = collect_log_files_with_manifest(patterns, target_dir)
    collected = log_result.collected_paths
    skipped = [item for item in log_result.files if item.skipped]
    truncated = [item for item in log_result.files if item.truncated]
    if redact and collected:
        report = redact_files(collected, package_dir / "redaction-report.md", redaction_options)
        for item in report.files:
            redaction_report.files.append(item)
            redaction_report.total_replacements += int(item.get("replacements", 0))
    evidence = EvidenceItem(
        kind="logs",
        title="Collected log files",
        source="doctor-link collect",
        path=str(target_dir.relative_to(package_dir)),
        content=(
            f"Collected {len(collected)} log file(s) from {len(patterns)} pattern(s); "
            f"truncated={len(truncated)}; skipped={len(skipped)}."
        ),
    )
    step = _step(
        package_dir,
        action="collect_logs",
        target=", ".join(patterns),
        expected="Relevant logs are copied into the diagnostic package with manifest metadata.",
        actual=f"Collected {len(collected)} log file(s), truncated {len(truncated)}, skipped {len(skipped)}.",
        status="passed" if collected else "unknown",
        evidence=evidence,
    )
    if not collected:
        result.warnings.append("No log files matched the provided patterns.")
    for item in skipped:
        result.warnings.append(f"Skipped log file {item.source}: {item.reason}")
    result.evidence.append(evidence)
    result.timeline_steps.append(step)


def _collect_commands(
    package_dir: Path,
    commands: Sequence[str],
    timeout_seconds: int,
    result: CollectionResult,
    redact: bool,
    redaction_options: RedactionOptions,
    redaction_report: RedactionReport,
    project_root: Path | None = None,
) -> None:
    output_dir = package_dir / "evidence" / "command-output"
    output_dir.mkdir(parents=True, exist_ok=True)
    cwd = project_root.resolve() if project_root is not None else None
    for index, command_text in enumerate(commands, start=1):
        command = shlex.split(command_text)
        command_result = run_command(command, timeout_seconds=timeout_seconds, cwd=cwd)
        payload = command_result.to_dict()
        if redact:
            for field_name in ["stdout", "stderr"]:
                if payload.get(field_name):
                    redacted = redact_text(str(payload[field_name]), redaction_options)
                    payload[field_name] = redacted.redacted_text
                    redaction_report.add_file(f"command-output/command-{index}.json:{field_name}", redacted)
        stdout_path = output_dir / f"command-{index}.stdout.txt"
        stderr_path = output_dir / f"command-{index}.stderr.txt"
        if payload.get("stdout"):
            stdout_path.write_text(str(payload["stdout"]), encoding="utf-8")
            payload["stdout_path"] = str(stdout_path.relative_to(package_dir))
        if payload.get("stderr"):
            stderr_path.write_text(str(payload["stderr"]), encoding="utf-8")
            payload["stderr_path"] = str(stderr_path.relative_to(package_dir))
        target = output_dir / f"command-{index}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        evidence = EvidenceItem(
            kind="command_output",
            title=f"Command output: {command_text}",
            source="doctor-link collect",
            path=str(target.relative_to(package_dir)),
            content=(
                f"Command returned {command_result.returncode}; timed_out={command_result.timed_out}; "
                f"duration_seconds={command_result.duration_seconds}."
            ),
        )
        step = _step(
            package_dir,
            action="collect_command_output",
            target=command_text,
            expected="Command output is captured without shell execution and with runtime metadata.",
            actual=f"Return code: {command_result.returncode}; duration_seconds={command_result.duration_seconds}.",
            status="passed" if command_result.returncode == 0 else "failed",
            evidence=evidence,
            failure=command_result.returncode != 0,
        )
        result.evidence.append(evidence)
        result.timeline_steps.append(step)


def _collect_probes(package_dir: Path, probes: Sequence[Path], ffprobe_binary: str, result: CollectionResult) -> None:
    output_dir = package_dir / "evidence" / "test-results"
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, media_file in enumerate(probes, start=1):
        payload = probe_media(media_file, ffprobe_binary=ffprobe_binary)
        summary = summarize_media_probe(payload)
        target = output_dir / f"media-probe-{index}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        evidence = EvidenceItem(
            kind="media_probe",
            title=f"Media probe: {media_file}",
            source="doctor-link collect",
            path=str(target.relative_to(package_dir)),
            content=json.dumps(summary, ensure_ascii=False),
        )
        step = _step(
            package_dir,
            action="collect_media_probe",
            target=str(media_file),
            expected="Media metadata is captured or failure is preserved as evidence.",
            actual="Probe succeeded." if payload.get("ok") else f"Probe failed: {payload.get('error')}",
            status="passed" if payload.get("ok") else "failed",
            evidence=evidence,
            failure=not bool(payload.get("ok")),
        )
        result.evidence.append(evidence)
        result.timeline_steps.append(step)


def _collect_attachments(package_dir: Path, attachments: Sequence[Path], result: CollectionResult) -> None:
    target_dir = package_dir / "evidence" / "attachments"
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for attachment in attachments:
        source = attachment.expanduser().resolve()
        if not source.is_file():
            result.warnings.append(f"Attachment not found or not a file: {attachment}")
            continue
        target = target_dir / _safe_filename(source)
        shutil.copy2(source, target)
        copied.append(target)
    evidence = EvidenceItem(
        kind="attachment",
        title="Collected attachments",
        source="doctor-link collect",
        path=str(target_dir.relative_to(package_dir)),
        content=f"Collected {len(copied)} attachment file(s).",
    )
    step = _step(
        package_dir,
        action="collect_attachments",
        target=", ".join(str(item) for item in attachments),
        expected="Attachment files are copied into the diagnostic package.",
        actual=f"Collected {len(copied)} attachment file(s).",
        status="passed" if copied else "unknown",
        evidence=evidence,
    )
    result.evidence.append(evidence)
    result.timeline_steps.append(step)


def _step(
    package_dir: Path,
    action: str,
    target: str,
    expected: str,
    actual: str,
    status: str,
    evidence: EvidenceItem,
    failure: bool = False,
) -> TimelineStep:
    return TimelineStep(
        order=_next_order(package_dir),
        action=action,
        target=target,
        expected_result=expected,
        actual_result=actual,
        status=status,
        evidence_ids=[evidence.evidence_id],
        is_failure_point=failure,
    )


def _write_redaction_report(package_dir: Path, report: RedactionReport, result: CollectionResult) -> None:
    report_path = package_dir / "redaction-report.md"
    report_path.write_text(report.to_markdown(), encoding="utf-8")
    json_path = package_dir / "redaction-report.json"
    json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    result.redaction_report = report.to_dict()


def _write_collection_result(package_dir: Path, result: CollectionResult) -> None:
    target = package_dir / "evidence" / "test-results" / "collection-result.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def _write_integrity_report(package_dir: Path, result: CollectionResult) -> None:
    evidence_dir = package_dir / "evidence"
    files: list[dict[str, Any]] = []
    if evidence_dir.exists():
        for path in sorted(item for item in evidence_dir.rglob("*") if item.is_file()):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files.append({
                "path": str(path.relative_to(package_dir)),
                "size_bytes": path.stat().st_size,
                "sha256": digest,
            })
    report = {
        "generated_at": utc_now_iso(),
        "hash_algorithm": "sha256",
        "file_count": len(files),
        "files": files,
    }
    target = package_dir / "evidence" / "evidence-integrity-index.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    result.integrity_report = report


def _update_package_files(package_dir: Path, result: CollectionResult) -> None:
    _update_report_json(package_dir, result)
    _append_evidence_list(package_dir, result.evidence)
    _append_timeline(package_dir, result.timeline_steps)
    _append_summary(package_dir, result)
    _append_ai_task(package_dir, result)


def _update_report_json(package_dir: Path, result: CollectionResult) -> None:
    path = package_dir / "doctor-report.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    payload.setdefault("evidence", []).extend(item.to_dict() for item in result.evidence)
    payload.setdefault("timeline", []).extend(step.to_dict() for step in result.timeline_steps)
    payload.setdefault("collections", []).append(result.to_dict())
    if result.redaction_report is not None:
        payload["redaction_report"] = result.redaction_report
    if result.integrity_report is not None:
        payload["evidence_integrity"] = result.integrity_report
    ai_task = payload.setdefault("ai_task", {})
    ai_task.setdefault("evidence_ids", []).extend(item.evidence_id for item in result.evidence)
    ai_task.setdefault("requested_work", []).append("Review newly collected evidence before proposing code changes.")
    ai_task.setdefault("verification_steps", []).append("Confirm collected evidence is sufficient before marking a fix as verified.")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_evidence_list(package_dir: Path, evidence_items: list[EvidenceItem]) -> None:
    lines: list[str] = []
    for item in evidence_items:
        lines.extend([
            f"\n## {item.title}",
            "",
            f"- ID: `{item.evidence_id}`",
            f"- Kind: `{item.kind}`",
            f"- Source: `{item.source}`",
            f"- Path: `{item.path or 'N/A'}`",
            "",
            item.content or "No content preview.",
            "",
        ])
    _append(package_dir / "evidence-list.md", "\n".join(lines))


def _append_timeline(package_dir: Path, steps: list[TimelineStep]) -> None:
    lines: list[str] = []
    for step in steps:
        marker = " **Failure point**" if step.is_failure_point else ""
        lines.extend([
            f"\n## Step {step.order}: {step.action}{marker}",
            "",
            f"- Time: `{step.timestamp}`",
            f"- Target: `{step.target or 'N/A'}`",
            f"- Status: `{step.status}`",
            f"- Expected: {step.expected_result or 'N/A'}",
            f"- Actual: {step.actual_result or 'N/A'}",
            f"- Evidence: {', '.join(step.evidence_ids) if step.evidence_ids else 'None'}",
            "",
        ])
    _append(package_dir / "timeline.md", "\n".join(lines))


def _append_summary(package_dir: Path, result: CollectionResult) -> None:
    redactions = result.redaction_report.get("total_replacements", 0) if result.redaction_report else 0
    integrity_files = result.integrity_report.get("file_count", 0) if result.integrity_report else 0
    _append(
        package_dir / "summary.md",
        "\n".join([
            "\n## Evidence collection",
            "",
            f"- Collected at: `{result.collected_at}`",
            f"- Evidence items: `{len(result.evidence)}`",
            f"- Timeline steps: `{len(result.timeline_steps)}`",
            f"- Warnings: `{len(result.warnings)}`",
            f"- Redactions: `{redactions}`",
            f"- Integrity indexed files: `{integrity_files}`",
            "",
        ]),
    )


def _append_ai_task(package_dir: Path, result: CollectionResult) -> None:
    lines = [
        "\n## Newly collected evidence",
        "",
        "Review these evidence items before proposing or validating fixes:",
    ]
    lines.extend(f"- `{item.evidence_id}`: {item.title}" for item in result.evidence)
    if result.redaction_report is not None:
        lines.extend(["", f"Redaction replacements: `{result.redaction_report.get('total_replacements', 0)}`"])
    if result.integrity_report is not None:
        lines.extend(["", f"Evidence integrity indexed files: `{result.integrity_report.get('file_count', 0)}`"])
    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    _append(package_dir / "ai-task.md", "\n".join(lines) + "\n")


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


def _safe_filename(path: Path) -> str:
    return "__".join(part for part in path.parts if part not in {path.anchor, "/"}).replace(" ", "_")
