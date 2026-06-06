from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.ai_handoff import build_handoff_package
from doctor_link.core.collector import collect_into_package
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.user_assertion_manager import add_user_assertion
from doctor_link.core.verification_runner import run_verification
from doctor_link.core.web_server import build_web_view


@dataclass(slots=True)
class NoCodeOptions:
    project_folder: Path
    summary: str
    out_dir: Path = Path("DoctorReports")
    tool: str = "generic"
    create_handoff: bool = True
    build_view: bool = True


@dataclass(slots=True)
class NoCodeResult:
    package_dir: Path
    report_path: Path
    workbench_path: Path | None = None
    handoff_dir: Path | None = None
    assertion_id: str | None = None
    verification_path: Path | None = None
    next_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_dir": str(self.package_dir),
            "report_path": str(self.report_path),
            "workbench_path": str(self.workbench_path) if self.workbench_path else None,
            "handoff_dir": str(self.handoff_dir) if self.handoff_dir else None,
            "assertion_id": self.assertion_id,
            "verification_path": str(self.verification_path) if self.verification_path else None,
            "next_steps": self.next_steps,
        }


def run_no_code_diagnosis(options: NoCodeOptions) -> NoCodeResult:
    project_folder = options.project_folder.expanduser().resolve()
    if not project_folder.exists():
        raise ValueError(f"Project folder not found: {project_folder}")
    if not project_folder.is_dir():
        raise ValueError(f"Project path is not a folder: {project_folder}")
    if not options.summary.strip():
        raise ValueError("Problem summary is required.")

    out_dir = options.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    scan_result = scan_library(project_folder)
    test_plan = generate_test_plan(scan_result)
    event = event_from_scan(scan_result, test_plan, project=project_folder.name or "guided-project")
    event.summary = options.summary.strip()
    package = build_diagnostic_package(event, out_dir)
    package_dir = package.root_dir

    collect_into_package(package_dir, project_root=project_folder, commands=["python --version"], note="Guided diagnosis evidence")
    assertion = add_user_assertion(package_dir, user_statement=options.summary.strip())
    run_verification(package_dir, write_back=True)
    verification_path = package_dir / "verification-result.json"

    workbench_path = None
    if options.build_view:
        view = build_web_view(package_dir)
        workbench_path = Path(view.index_path)

    handoff_dir = None
    if options.create_handoff:
        handoff = build_handoff_package(package_dir, tool=options.tool, output_dir=out_dir / "handoff" / package_dir.name / options.tool)
        handoff_dir = Path(handoff.output_dir)

    next_steps = [f"Open report: {workbench_path or package_dir}"]
    if handoff_dir:
        next_steps.append(f"Use handoff folder: {handoff_dir}")

    return NoCodeResult(package_dir, package_dir / "doctor-report.json", workbench_path, handoff_dir, assertion.assertion_id, verification_path, next_steps)


def build_no_code_home(output_dir: Path = Path(".doctorlink-home")) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = output_dir / "index.html"
    index.write_text("<h1>Doctor link Home</h1><p>Run doctor-link wizard to start.</p>", encoding="utf-8")
    return index


def format_no_code_result(result: NoCodeResult) -> str:
    lines = ["Doctor link guided diagnosis completed.", f"Diagnostic package: {result.package_dir}", f"Report JSON: {result.report_path}"]
    if result.workbench_path:
        lines.append(f"Local HTML report: {result.workbench_path}")
    if result.handoff_dir:
        lines.append(f"Handoff folder: {result.handoff_dir}")
    lines.extend(result.next_steps)
    return "\n".join(lines)


def no_code_result_to_json(result: NoCodeResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
