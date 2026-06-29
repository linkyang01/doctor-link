from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DiagnosisStrategy:
    project: str | None = None
    project_type: str = "generic"
    symptom: str | None = None
    failure_stage: str | None = None
    investigation_boundary: list[str] = field(default_factory=list)
    do_not_change: list[str] = field(default_factory=list)
    default_commands: list[str] = field(default_factory=list)
    evidence_rules: list[str] = field(default_factory=list)
    verification_rules: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyValidationResult:
    path: str
    is_valid: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    strategy: DiagnosisStrategy | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "is_valid": self.is_valid,
            "warnings": self.warnings,
            "errors": self.errors,
            "strategy": self.strategy.to_dict() if self.strategy is not None else None,
        }

    def to_markdown(self) -> str:
        lines = ["# Diagnosis Strategy Validation", "", f"- Path: `{self.path}`", f"- Valid: `{self.is_valid}`", ""]
        if self.strategy is not None:
            lines.extend([
                "## Strategy",
                f"- Project type: `{self.strategy.project_type}`",
                f"- Default commands: {len(self.strategy.default_commands)}",
                f"- Evidence rules: {len(self.strategy.evidence_rules)}",
                f"- Verification rules: {len(self.strategy.verification_rules)}",
                f"- Excluded paths: {len(self.strategy.excluded_paths)}",
                "",
            ])
        lines.extend(_section("Errors", self.errors))
        lines.extend(_section("Warnings", self.warnings))
        return "\n".join(lines)


def project_context_from_library(library: Path) -> tuple[str, DiagnosisStrategy]:
    """Resolve display project name and strategy from a library directory."""
    result = load_diagnosis_strategy(library)
    strategy = result.strategy or DiagnosisStrategy()
    project = strategy.project or library.name or "Doctor link"
    return project, strategy


def load_diagnosis_strategy(start_dir: Path | None = None) -> StrategyValidationResult:
    root = _find_root(start_dir or Path.cwd())
    path = root / ".doctorlink" / "diagnosis.yml"
    if not path.exists():
        strategy = DiagnosisStrategy()
        return StrategyValidationResult(path=str(path), is_valid=True, warnings=["Missing .doctorlink/diagnosis.yml; using defaults."], strategy=strategy)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return StrategyValidationResult(path=str(path), is_valid=False, errors=[f"Invalid YAML: {exc}"])
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        return StrategyValidationResult(path=str(path), is_valid=False, errors=["diagnosis.yml must contain a mapping."])
    strategy = _strategy_from_raw(raw)
    errors, warnings = validate_diagnosis_strategy(strategy)
    return StrategyValidationResult(path=str(path), is_valid=not errors, errors=errors, warnings=warnings, strategy=strategy)


def validate_diagnosis_strategy(strategy: DiagnosisStrategy | dict[str, Any]) -> StrategyValidationResult | tuple[list[str], list[str]]:
    if isinstance(strategy, dict):
        parsed = _strategy_from_raw(strategy)
        errors, warnings = _validate_strategy(parsed)
        return StrategyValidationResult(path="diagnosis.yml", is_valid=not errors, errors=errors, warnings=warnings, strategy=parsed)
    return _validate_strategy(strategy)


def _validate_strategy(strategy: DiagnosisStrategy) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not strategy.project_type:
        errors.append("project_type must not be empty.")
    for field_name in ["default_commands", "evidence_rules", "verification_rules", "excluded_paths"]:
        value = getattr(strategy, field_name)
        if not isinstance(value, list):
            errors.append(f"{field_name} must be a list.")
    if not strategy.default_commands:
        warnings.append("No default_commands configured")
    if not strategy.verification_rules:
        warnings.append("No verification_rules configured")
    return errors, warnings


def _strategy_from_raw(raw: dict[str, Any]) -> DiagnosisStrategy:
    diagnosis = raw.get("diagnosis", raw)
    if not isinstance(diagnosis, dict):
        diagnosis = {}
    return DiagnosisStrategy(
        project=_optional_str(diagnosis.get("project")),
        project_type=str(diagnosis.get("project_type", "generic")),
        symptom=_optional_str(diagnosis.get("symptom")),
        failure_stage=_optional_str(diagnosis.get("failure_stage")),
        investigation_boundary=_list(diagnosis.get("investigation_boundary", [])),
        do_not_change=_list(diagnosis.get("do_not_change", [])),
        default_commands=_list(diagnosis.get("default_commands", [])),
        evidence_rules=_list(diagnosis.get("evidence_rules", [])),
        verification_rules=_list(diagnosis.get("verification_rules", [])),
        excluded_paths=_list(diagnosis.get("excluded_paths", [])),
        raw=raw,
    )


def _find_root(start_dir: Path) -> Path:
    current = start_dir.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".doctorlink").is_dir():
            return candidate
    return current


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _section(title: str, values: list[str]) -> list[str]:
    lines = [f"## {title}"]
    lines.extend([f"- {item}" for item in values] if values else ["- None"])
    lines.append("")
    return lines
