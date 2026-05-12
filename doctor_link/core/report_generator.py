from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from doctor_link.core.models import ScanResult, TestPlan


def generate_basic_report(scan_result: ScanResult, test_plan: TestPlan, output: Path) -> list[Path]:
    """Generate Markdown and JSON reports."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    report_dir = output / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = report_dir / "doctor-report.md"
    json_path = report_dir / "doctor-report.json"
    summary_path = report_dir / "summary.md"

    markdown = _build_markdown_report(scan_result, test_plan, timestamp)
    summary = _build_summary(scan_result, test_plan)

    payload = {
        "generated_at": timestamp,
        "library_root": str(scan_result.root),
        "file_count": len(scan_result.files),
        "detected_extensions": test_plan.detected_extensions,
        "missing_categories": test_plan.missing_categories,
        "recommended_tests": test_plan.recommended_tests,
        "files": [
            {
                "relative_path": item.relative_path,
                "size_bytes": item.size_bytes,
                "extension": item.extension,
            }
            for item in scan_result.files
        ],
    }

    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(summary, encoding="utf-8")

    return [summary_path, markdown_path, json_path]


def _build_markdown_report(scan_result: ScanResult, test_plan: TestPlan, timestamp: str) -> str:
    lines = [
        "# Doctor link Diagnostic Report",
        "",
        f"Generated at: `{timestamp}`",
        f"Library root: `{scan_result.root}`",
        f"Total files: `{len(scan_result.files)}`",
        "",
        test_plan.to_markdown(),
        "## Files",
    ]

    if not scan_result.files:
        lines.append("- No files detected")
    else:
        for item in scan_result.files:
            lines.append(f"- `{item.relative_path}` ({item.size_bytes} bytes)")

    lines.append("")
    lines.append("## Current diagnosis")
    lines.append("This is an initial static scan report. Playback execution and failure diagnosis are not implemented yet.")
    lines.append("")
    return "\n".join(lines)


def _build_summary(scan_result: ScanResult, test_plan: TestPlan) -> str:
    lines = [
        "# Doctor link Summary",
        "",
        f"Scanned files: **{len(scan_result.files)}**",
        f"Missing categories: **{len(test_plan.missing_categories)}**",
        f"Recommended tests: **{len(test_plan.recommended_tests)}**",
        "",
        "## Simple conclusion",
    ]

    if not scan_result.files:
        lines.append("No test files were found. Add media samples before running playback validation.")
    elif test_plan.missing_categories:
        lines.append("The test library is incomplete. Add missing sample categories before making a playback capability conclusion.")
    else:
        lines.append("The test library covers the initial required categories. Playback testing can begin.")

    lines.append("")
    return "\n".join(lines)
