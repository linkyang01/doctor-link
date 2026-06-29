from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.report_generator import generate_basic_report
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan


def test_generate_basic_report_writes_markdown_and_json(tmp_path: Path) -> None:
    (tmp_path / "sample.mp4").write_text("video", encoding="utf-8")
    output = tmp_path / "legacy-reports"
    scan = scan_library(tmp_path)
    plan = generate_test_plan(scan)
    paths = generate_basic_report(scan, plan, output)

    assert len(paths) == 3
    json_path = next(path for path in paths if path.name == "doctor-report.json")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["file_count"] == 1
    assert (json_path.parent / "summary.md").exists()