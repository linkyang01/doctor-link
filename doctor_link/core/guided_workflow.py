from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.ai_handoff import build_handoff_package
from doctor_link.core.evidence import collect_evidence
from doctor_link.core.report import create_report
from doctor_link.core.user_assertions import add_user_assertion
from doctor_link.core.verify import verify_package
from doctor_link.web import build_static_view


@dataclass(slots=True)
class GuidedWorkflowOptions:
    project_folder: Path
    summary: str
    out_dir: Path = Path("DoctorReports")
    tool: str = "generic"
    create_handoff: bool = True
    build_view: bool = True
    include_python_version: bool = True
    note: str = "Guided no-code diagnosis evidence"


@dataclass(slots=True)
class GuidedWorkflowResult:
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


def run_guided_diagnosis(options: GuidedWorkflowOptions) -> GuidedWorkflowResult:
    """Run the common no-code diagnosis workflow.

    The workflow is intentionally conservative and local-first. It creates a
    diagnostic package, collects minimal evidence, records the user's problem
    statement, writes verification metadata, optionally builds the local
    workbench, and optionally creates an AI handoff package.
    """
    project_folder = options.project_folder.expanduser().resolve()
    if not project_folder.exists():
        raise ValueError(f"Project folder not found: {project_folder}")
    if not project_folder.is_dir():
        raise ValueError(f"Project path is not a folder: {project_folder}")
    if not options.summary.strip():
        raise ValueError("Problem summary is required.")

    out_dir = options.out_dir.expanduser().resolve()
    report = create_report(project_folder, out_dir=out_dir)
    package_dir = report.package_dir

    commands: list[str] = []
    if options.include_python_version:
        commands.append("python --version")

    if commands or options.note:
        collect_evidence(
            package_dir,
            project_root=project_folder,
            commands=commands,
            note=options.note,
        )

    assertion = add_user_assertion(
        package_dir,
        statement=options.summary.strip(),
        expected="The issue should be investigated and fixed with evidence.",
        actual="The user reported this issue through the guided workflow.",
        next_ai="Use the generated diagnostic package and evidence before proposing a fix.",
    )

    verification = verify_package(package_dir, write_back=True)

    workbench_path: Path | None = None
    if options.build_view:
        build_static_view(package_dir)
        workbench_path = package_dir / ".doctorlink-web" / "index.html"

    handoff_dir: Path | None = None
    if options.create_handoff:
        handoff_root = out_dir / "handoff"
        handoff = build_handoff_package(package_dir, tool=options.tool, out_dir=handoff_root)
        handoff_dir = handoff.output_dir

    next_steps = _build_next_steps(workbench_path, handoff_dir, package_dir)

    return GuidedWorkflowResult(
        package_dir=package_dir,
        report_path=package_dir / "doctor-report.json",
        workbench_path=workbench_path,
        handoff_dir=handoff_dir,
        assertion_id=assertion.assertion_id,
        verification_path=verification.output_path,
        next_steps=next_steps,
    )


def build_home_page(reports_root: Path, output_dir: Path = Path(".doctorlink-home")) -> Path:
    reports_root = reports_root.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    index = output_dir / "index.html"

    packages: list[Path] = []
    if reports_root.exists():
        packages = sorted(
            [path for path in reports_root.iterdir() if path.is_dir() and (path / "doctor-report.json").exists()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

    rows = []
    for package in packages[:20]:
        workbench = package / ".doctorlink-web" / "index.html"
        report = package / "doctor-report.json"
        link_target = workbench if workbench.exists() else report
        rows.append(
            "<li>"
            f"<a href='{html.escape(str(link_target))}'>{html.escape(package.name)}</a>"
            f" <small>{html.escape(str(package))}</small>"
            "</li>"
        )

    rows_html = "\n".join(rows) if rows else "<li>No diagnostic packages found yet.</li>"
    content = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>Doctor link Home</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 2rem; line-height: 1.5; }}
    code {{ background: #f3f4f6; padding: 0.15rem 0.3rem; border-radius: 4px; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 12px; padding: 1rem; margin: 1rem 0; }}
  </style>
</head>
<body>
  <h1>Doctor link Home</h1>
  <p>Local-first diagnostic workspace for no-code and AI coding workflows.</p>
  <div class='card'>
    <h2>Recent diagnostic packages</h2>
    <ul>{rows_html}</ul>
  </div>
  <div class='card'>
    <h2>Start a guided diagnosis</h2>
    <p>Run:</p>
    <pre><code>doctor-link wizard</code></pre>
    <p>Or:</p>
    <pre><code>doctor-link diagnose-now &lt;project_folder&gt; --summary "Describe the problem"</code></pre>
  </div>
  <div class='card'>
    <h2>Useful docs</h2>
    <ul>
      <li><a href='docs/guides/no-code-quick-start.en.md'>No-code quick start</a></li>
      <li><a href='docs/guides/no-code-quick-start.zh-CN.md'>中文小白快速开始</a></li>
      <li><a href='docs/troubleshooting.md'>Troubleshooting</a></li>
    </ul>
  </div>
</body>
</html>
"""
    index.write_text(content, encoding="utf-8")
    return index


def format_guided_result(result: GuidedWorkflowResult) -> str:
    lines = [
        "Doctor link guided diagnosis completed.",
        "",
        f"Diagnostic package: {result.package_dir}",
        f"Report JSON: {result.report_path}",
    ]
    if result.workbench_path:
        lines.append(f"Local HTML report: {result.workbench_path}")
    if result.handoff_dir:
        lines.append(f"AI handoff folder: {result.handoff_dir}")
    if result.verification_path:
        lines.append(f"Verification result: {result.verification_path}")
    if result.next_steps:
        lines.extend(["", "Next steps:"])
        lines.extend(f"- {step}" for step in result.next_steps)
    return "\n".join(lines)


def _build_next_steps(workbench_path: Path | None, handoff_dir: Path | None, package_dir: Path) -> list[str]:
    steps = []
    if workbench_path:
        steps.append(f"Open the local HTML report: {workbench_path}")
    else:
        steps.append(f"Review the diagnostic package: {package_dir}")
    if handoff_dir:
        steps.append(f"Give the AI handoff folder to your AI coding tool: {handoff_dir}")
    steps.append("Do not publish releases, tags, or PyPI packages as part of diagnosis.")
    return steps


def result_to_json(result: GuidedWorkflowResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
