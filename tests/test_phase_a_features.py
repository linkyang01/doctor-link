from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.diagnosis_strategy import project_context_from_library
from doctor_link.core.package_builder import event_from_scan, finalize_event
from doctor_link.core.problem_map_builder import build_problem_map
from doctor_link.core.reproduction import load_reproduction_catalog
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.verification_builder import build_verification_checklist
from doctor_link.diagnose_report import build_report
from doctor_link.entrypoint import main


def test_cli_version_flag() -> None:
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.3" in result.output


def test_report_uses_diagnosis_project_name(tmp_path: Path) -> None:
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "diagnosis.yml").write_text("project: my-service\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")

    result = CliRunner().invoke(main, ["report", str(tmp_path), "--out", str(tmp_path / "DoctorReports")])
    assert result.exit_code == 0, result.output
    assert "my-service" in result.output


def test_verify_lists_missing_evidence_and_next_commands(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "summary.md").write_text("# Summary\n", encoding="utf-8")
    (package / "timeline.md").write_text("# Timeline\n", encoding="utf-8")
    (package / "evidence-list.md").write_text("# Evidence\n", encoding="utf-8")
    (package / "ai-task.md").write_text("# AI Task\n", encoding="utf-8")
    (package / "user-assertions.json").write_text("[]\n", encoding="utf-8")
    (package / "doctor-report.json").write_text(
        json.dumps(
            {
                "event_id": "evt_test",
                "project": "demo",
                "timeline": [],
                "evidence": [],
                "user_assertions": [],
                "problem_map": {},
                "ai_task": {},
                "verification_checklist": {},
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, ["verify", str(package)])
    assert result.exit_code == 1, result.output
    assert "Missing evidence:" in result.output
    assert "Next commands:" in result.output


def test_assertion_check_json_output(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "user-assertions.json").write_text("[]\n", encoding="utf-8")
    (package / "doctor-report.json").write_text(
        json.dumps({"user_assertions": [], "ai_results": []}),
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, ["assertion-check", str(package), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "status" in payload


def test_problem_and_verification_builders_wire_up(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text("x = 1\n", encoding="utf-8")
    scan = scan_library(tmp_path)
    plan = generate_test_plan(scan)
    event = finalize_event(event_from_scan(scan, plan, project="demo"))
    assert build_problem_map(event).failure_stage
    checklist = build_verification_checklist(event)
    assert checklist.items


def test_reproduce_accepts_command_list(tmp_path: Path) -> None:
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "reproduce.yml").write_text(
        """
reproductions:
  - id: chained
    title: chained command
    kind: command
    command:
      - python -c "print('a')"
      - python -c "print('b')"
""".strip(),
        encoding="utf-8",
    )
    catalog = load_reproduction_catalog(tmp_path)
    assert catalog.entries[0].command == "python -c \"print('a')\" && python -c \"print('b')\""


def test_wizard_handoff_tool_flag(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        [
            "wizard",
            "--folder",
            str(tmp_path),
            "--summary",
            "startup issue",
            "--tool",
            "codex",
            "--handoff",
            "--no-collect-evidence",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["handoff_dir"] is not None
    handoff_dir = Path(payload["handoff_dir"])
    manifest = json.loads((handoff_dir / "handoff-manifest.json").read_text(encoding="utf-8"))
    assert manifest["tool"] == "codex"


def test_wizard_accepts_grok_tool_flag(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        [
            "wizard",
            "--folder",
            str(tmp_path),
            "--summary",
            "startup issue",
            "--tool",
            "grok",
            "--handoff",
            "--no-collect-evidence",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["handoff_dir"] is not None
    manifest = json.loads((Path(payload["handoff_dir"]) / "handoff-manifest.json").read_text(encoding="utf-8"))
    assert manifest["tool"] == "grok"


def test_wizard_rejects_unknown_tool(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        ["wizard", "--folder", str(tmp_path), "--tool", "unknown"],
    )
    assert result.exit_code != 0
    assert "unknown" in result.output.lower() or "invalid" in result.output.lower()


def test_diagnose_now_full_workflow(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        ["diagnose-now", str(tmp_path), "--full", "--reports", str(tmp_path / "DoctorReports"), "--summary", "startup issue"],
    )
    assert result.exit_code == 0, result.output
    assert "Diagnostic workflow complete." in result.output
    assert "Open the HTML report:" in result.output


def test_diagnose_now_handoff_tool_flag(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    result = CliRunner().invoke(
        main,
        [
            "diagnose-now",
            str(tmp_path),
            "--handoff",
            "--tool",
            "grok",
            "--no-collect",
            "--reports",
            str(tmp_path / "DoctorReports"),
            "--summary",
            "startup issue",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["handoff_dir"] is not None
    manifest = json.loads((Path(payload["handoff_dir"]) / "handoff-manifest.json").read_text(encoding="utf-8"))
    assert manifest["tool"] == "grok"


def test_home_command_builds_static_page(tmp_path: Path) -> None:
    reports = tmp_path / "DoctorReports"
    package = reports / "2026_demo_issue"
    package.mkdir(parents=True)
    (package / "summary.md").write_text("# Summary\n", encoding="utf-8")
    (package / "doctor-report.json").write_text(json.dumps({"project": "demo", "summary": "demo issue"}), encoding="utf-8")

    result = CliRunner().invoke(main, ["home", "--reports", str(reports), "--output", str(tmp_path / "home")])
    assert result.exit_code == 0, result.output
    index = tmp_path / "home" / "index.html"
    assert index.exists()
    assert "Doctor link" in index.read_text(encoding="utf-8")


def test_build_report_recommendations_are_dynamic() -> None:
    files = [Path("app.py"), Path("logs/app.log")]
    report = build_report(files)
    assert any("doctor-link report" in item for item in report["recommendations"])
    assert any("logs" in item for item in report["recommendations"])


def test_project_context_from_library_reads_project_field(tmp_path: Path) -> None:
    config_dir = tmp_path / ".doctorlink"
    config_dir.mkdir()
    (config_dir / "diagnosis.yml").write_text("project: shop-service\n", encoding="utf-8")
    project, _strategy = project_context_from_library(tmp_path)
    assert project == "shop-service"
