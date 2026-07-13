from __future__ import annotations

import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.config_loader import load_config
from doctor_link.core.diagnosis_strategy import load_diagnosis_strategy
from doctor_link.core.models import utc_now_iso
from doctor_link.core.reproduction import load_reproduction_catalog
from doctor_link.core.safe_command_runner import validate_safe_command_sequence
from doctor_link.core.test_matrix_runner import load_test_matrix


@dataclass
class PreflightCheck:
    check_id: str
    status: str
    message: str
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PreflightReport:
    project_root: str
    status: str
    generated_at: str = field(default_factory=utc_now_iso)
    checks: list[PreflightCheck] = field(default_factory=list)

    @property
    def blocking_count(self) -> int:
        return sum(check.status == "blocked" for check in self.checks)

    @property
    def warning_count(self) -> int:
        return sum(check.status == "warning" for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_root": self.project_root,
            "status": self.status,
            "generated_at": self.generated_at,
            "blocking_count": self.blocking_count,
            "warning_count": self.warning_count,
            "checks": [check.to_dict() for check in self.checks],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link Preflight",
            "",
            f"- Project root: `{self.project_root}`",
            f"- Status: `{self.status}`",
            f"- Blocking checks: `{self.blocking_count}`",
            f"- Warnings: `{self.warning_count}`",
            "",
            "## Checks",
            "",
        ]
        for check in self.checks:
            lines.append(f"- `{check.status}` `{check.check_id}`: {check.message}")
            lines.extend(f"  - {detail}" for detail in check.details)
        lines.append("")
        return "\n".join(lines)


def run_preflight(project_root: Path) -> PreflightReport:
    """Inspect local readiness without executing project-defined commands."""
    root = project_root.expanduser().resolve()
    checks: list[PreflightCheck] = []
    if not root.is_dir():
        checks.append(PreflightCheck("project-root", "blocked", "Project root does not exist."))
        return _report(root, checks)
    checks.append(PreflightCheck("project-root", "passed", "Project root is readable."))

    python_ok = sys.version_info >= (3, 10)
    checks.append(
        PreflightCheck(
            "python-version",
            "passed" if python_ok else "blocked",
            f"Python {sys.version.split()[0]} detected; Doctor link requires Python 3.10+.",
        )
    )

    config = load_config(root)
    checks.append(
        PreflightCheck(
            "configuration",
            "blocked" if config.errors else ("warning" if config.warnings else "passed"),
            "Doctor link configuration inspected.",
            [*config.errors, *config.warnings],
        )
    )

    strategy = load_diagnosis_strategy(root)
    checks.append(
        PreflightCheck(
            "diagnosis-strategy",
            "blocked" if not strategy.is_valid else ("warning" if strategy.warnings else "passed"),
            "Diagnosis strategy inspected.",
            [*strategy.errors, *strategy.warnings],
        )
    )

    reproduction = load_reproduction_catalog(root)
    matrix = load_test_matrix(root)
    configured_commands = [*config.collect.commands]
    configured_commands.extend(entry.command for entry in reproduction.entries if entry.command)
    configured_commands.extend(job.command for job in matrix.jobs if job.command)
    command_errors = [
        f"{command}: {error}"
        for command in configured_commands
        if (error := validate_safe_command_sequence(command)) is not None
    ]
    checks.append(
        PreflightCheck(
            "configured-commands",
            "blocked" if command_errors else "passed",
            f"Reviewed {len(configured_commands)} configured command(s) without executing them.",
            command_errors,
        )
    )

    catalog_warnings = [*reproduction.warnings, *matrix.warnings]
    checks.append(
        PreflightCheck(
            "runtime-catalogs",
            "warning" if catalog_warnings else "passed",
            "Reproduction and test-matrix catalogs inspected.",
            catalog_warnings,
        )
    )

    required_tools = ["git"]
    optional_tools = ["ffprobe"]
    missing_required = [tool for tool in required_tools if shutil.which(tool) is None]
    missing_optional = [tool for tool in optional_tools if shutil.which(tool) is None]
    checks.append(
        PreflightCheck(
            "local-tools",
            "blocked" if missing_required else ("warning" if missing_optional else "passed"),
            "Local diagnostic tools inspected.",
            [
                *[f"Required tool not found: {tool}" for tool in missing_required],
                *[f"Optional tool not found: {tool}" for tool in missing_optional],
            ],
        )
    )
    return _report(root, checks)


def _report(root: Path, checks: list[PreflightCheck]) -> PreflightReport:
    if any(check.status == "blocked" for check in checks):
        status = "blocked"
    elif any(check.status == "warning" for check in checks):
        status = "warning"
    else:
        status = "passed"
    return PreflightReport(project_root=str(root), status=status, checks=checks)
