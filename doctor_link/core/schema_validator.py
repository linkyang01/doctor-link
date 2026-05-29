from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.schema_policy import CORE_PACKAGE_FILES, OPTIONAL_PACKAGE_FILES, SCHEMA_VERSION


@dataclass
class SchemaFinding:
    path: str
    level: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class SchemaValidationResult:
    package_dir: str
    schema_version: str = SCHEMA_VERSION
    status: str = "valid"
    checked_files: list[str] = field(default_factory=list)
    findings: list[SchemaFinding] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(item.level == "error" for item in self.findings)

    def add(self, path: str, level: str, message: str) -> None:
        self.findings.append(SchemaFinding(path=path, level=level, message=message))
        if level == "error":
            self.status = "invalid"

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_dir": self.package_dir,
            "schema_version": self.schema_version,
            "status": self.status,
            "valid": self.valid,
            "checked_files": self.checked_files,
            "findings": [item.to_dict() for item in self.findings],
        }


def validate_diagnostic_package(package_dir: Path) -> SchemaValidationResult:
    package_dir = package_dir.resolve()
    result = SchemaValidationResult(package_dir=str(package_dir))
    if not package_dir.is_dir():
        result.add(str(package_dir), "error", "Diagnostic package directory does not exist.")
        return result

    for relative in CORE_PACKAGE_FILES:
        _validate_required_file(package_dir, relative, result)
    for relative in OPTIONAL_PACKAGE_FILES:
        path = package_dir / relative
        if path.exists():
            _validate_file(path, relative, result)

    for manifest_name in ["handoff-manifest.json", "manifest.json"]:
        path = package_dir / manifest_name
        if path.exists():
            _validate_file(path, manifest_name, result)
    return result


def write_schema_validation_result(package_dir: Path, result: SchemaValidationResult) -> None:
    (package_dir / "schema-validation-result.json").write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (package_dir / "schema-validation-result.md").write_text(_to_markdown(result), encoding="utf-8")


def _validate_required_file(package_dir: Path, relative: str, result: SchemaValidationResult) -> None:
    path = package_dir / relative
    if not path.exists():
        result.add(relative, "error", "Required package file is missing.")
        return
    _validate_file(path, relative, result)


def _validate_file(path: Path, relative: str, result: SchemaValidationResult) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.add(relative, "error", f"Invalid JSON: {exc.msg}.")
        return
    result.checked_files.append(relative)
    _validate_named_payload(relative, payload, result)


def _validate_named_payload(relative: str, payload: Any, result: SchemaValidationResult) -> None:
    if relative == "doctor-report.json":
        if _object(relative, payload, result):
            _required(relative, payload, result, ["event_id", "project", "timeline", "evidence", "user_assertions", "problem_map", "ai_task", "verification_checklist", "status"])
            _schema_version(relative, payload, result)
            _list(relative, payload, result, "timeline")
            _list(relative, payload, result, "evidence")
            _list(relative, payload, result, "user_assertions")
            _dict(relative, payload, result, "problem_map")
            _dict(relative, payload, result, "ai_task")
            _dict(relative, payload, result, "verification_checklist")
        return
    if relative == "ai-context.json":
        if _object(relative, payload, result):
            _required(relative, payload, result, ["event_id", "project", "evidence", "timeline", "user_assertions", "problem_map", "ai_task", "verification_checklist"])
            _schema_version(relative, payload, result)
            _list(relative, payload, result, "evidence")
            _list(relative, payload, result, "timeline")
            _list(relative, payload, result, "user_assertions")
        return
    if relative == "user-assertions.json":
        if not isinstance(payload, list):
            result.add(relative, "error", "Expected an array of user assertion objects.")
            return
        for index, item in enumerate(payload):
            if isinstance(item, dict):
                _required(f"{relative}[{index}]", item, result, ["assertion_id", "user_statement", "severity"])
            else:
                result.add(relative, "error", f"User assertion at index {index} is not an object.")
        return
    if relative == "verification-result.json":
        if _object(relative, payload, result):
            _required(relative, payload, result, ["package_dir", "status", "missing_evidence", "tests_to_rerun", "next_commands", "notes"])
            _schema_version(relative, payload, result)
            _list(relative, payload, result, "missing_evidence")
            _list(relative, payload, result, "tests_to_rerun")
            _list(relative, payload, result, "next_commands")
        return
    if relative in {"ai-repair-result.json", "diagnosis-history.json"}:
        if not isinstance(payload, list):
            result.add(relative, "error", "Expected an array of records.")
        return
    if relative in {"handoff-manifest.json", "manifest.json"}:
        if _object(relative, payload, result):
            _required(relative, payload, result, ["tool", "source_package", "instruction_file", "included_files", "missing_files"])
            _schema_version(relative, payload, result)
            _list(relative, payload, result, "included_files")
            _list(relative, payload, result, "missing_files")


def _object(relative: str, payload: Any, result: SchemaValidationResult) -> bool:
    if not isinstance(payload, dict):
        result.add(relative, "error", "Expected a JSON object.")
        return False
    return True


def _required(relative: str, payload: dict[str, Any], result: SchemaValidationResult, keys: list[str]) -> None:
    for key in keys:
        if key not in payload:
            result.add(relative, "error", f"Missing required field `{key}`.")


def _schema_version(relative: str, payload: dict[str, Any], result: SchemaValidationResult) -> None:
    version = payload.get("schema_version")
    if version is None:
        result.add(relative, "warning", f"Missing schema_version; treating as pre-v{SCHEMA_VERSION} compatible payload.")
    elif version != SCHEMA_VERSION:
        result.add(relative, "error", f"Expected schema_version `{SCHEMA_VERSION}`, got `{version}`.")


def _list(relative: str, payload: dict[str, Any], result: SchemaValidationResult, key: str) -> None:
    if key in payload and not isinstance(payload[key], list):
        result.add(relative, "error", f"Field `{key}` must be an array.")


def _dict(relative: str, payload: dict[str, Any], result: SchemaValidationResult, key: str) -> None:
    if key in payload and not isinstance(payload[key], dict):
        result.add(relative, "error", f"Field `{key}` must be an object.")


def _to_markdown(result: SchemaValidationResult) -> str:
    lines = [
        "# Schema Validation Result", "", f"- Package: `{result.package_dir}`", f"- Schema version: `{result.schema_version}`", f"- Status: `{result.status}`", f"- Valid: `{result.valid}`", "", "## Checked files",
    ]
    lines.extend([f"- `{item}`" for item in result.checked_files] or ["- None"])
    lines.extend(["", "## Findings"])
    if result.findings:
        lines.extend([f"- `{item.level}` `{item.path}`: {item.message}" for item in result.findings])
    else:
        lines.append("- No schema validation findings.")
    lines.append("")
    return "\n".join(lines)
