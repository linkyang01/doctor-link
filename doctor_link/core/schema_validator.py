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
        path = package_dir / relative
        if not path.exists():
            result.add(relative, "error", "Required package file is missing.")
            continue
        payload = _load_json(path, result, relative)
        if payload is None:
            continue
        result.checked_files.append(relative)
        _validate_named_payload(relative, payload, result)

    for relative in OPTIONAL_PACKAGE_FILES:
        path = package_dir / relative
        if not path.exists():
            continue
        payload = _load_json(path, result, relative)
        if payload is None:
            continue
        result.checked_files.append(relative)
        _validate_named_payload(relative, payload, result)

    handoff_manifest = package_dir / "handoff-manifest.json"
    if handoff_manifest.exists():
        payload = _load_json(handoff_manifest, result, "handoff-manifest.json")
        if payload is not None:
            result.checked_files.append("handoff-manifest.json")
            _validate_handoff_manifest(payload, result)

    return result


def write_schema_validation_result(package_dir: Path, result: SchemaValidationResult) -> None:
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "schema-validation-result.json").write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (package_dir / "schema-validation-result.md").write_text(_to_markdown(result), encoding="utf-8")


def _load_json(path: Path, result: SchemaValidationResult, relative: str) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.add(relative, "error", f"Invalid JSON: {exc.msg}.")
        return None


def _validate_named_payload(relative: str, payload: Any, result: SchemaValidationResult) -> None:
    if relative == "doctor-report.json":
        _validate_object(relative, payload, result)
        if isinstance(payload, dict):
            _require_keys(relative, payload, result, ["schema_version", "event_id", "project", "timeline", "evidence", "user_assertions", "problem_map", "ai_task", "verification_checklist", "status"])
            _require_version(relative, payload, result)
            _require_list(relative, payload, result, "timeline")
            _require_list(relative, payload, result, "evidence")
            _require_list(relative, payload, result, "user_assertions")
            _require_object(relative, payload, result, "problem_map")
            _require_object(relative, payload, result, "ai_task")
            _require_object(relative, payload, result, "verification_checklist")
        return

    if relative == "ai-context.json":
        _validate_object(relative, payload, result)
        if isinstance(payload, dict):
            _require_keys(relative, payload, result, ["schema_version", "event_id", "project", "evidence", "timeline", "user_assertions", "problem_map", "ai_task", "verification_checklist"])
            _require_version(relative, payload, result)
            _require_list(relative, payload, result, "evidence")
            _require_list(relative, payload, result, "timeline")
            _require_list(relative, payload, result, "user_assertions")
        return

    if relative == "user-assertions.json":
        if not isinstance(payload, list):
            result.add(relative, "error", "Expected an array of user assertion objects.")
            return
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                result.add(relative, "error", f"User assertion at index {index} is not an object.")
                continue
            _require_keys(f"{relative}[{index}]", item, result, ["assertion_id", "user_statement", "severity"])
        return

    if relative == "verification-result.json":
        _validate_object(relative, payload, result)
        if isinstance(payload, dict):
            _require_keys(relative, payload, result, ["schema_version", "package_dir", "status", "missing_evidence", "tests_to_rerun", "next_commands", "notes"])
            _require_version(relative, payload, result)
            _require_list(relative, payload, result, "missing_evidence")
            _require_list(relative, payload, result, "tests_to_rerun")
            _require_list(relative, payload, result, "next_commands")
        return

    if relative in {"ai-repair-result.json", "diagnosis-history.json"}:
        if not isinstance(payload, list):
            result.add(relative, "error", "Expected an array of records.")
        return


def _validate_handoff_manifest(payload: Any, result: SchemaValidationResult) -> None:
    relative = "handoff-manifest.json"
    _validate_object(relative, payload, result)
    if isinstance(payload, dict):
        _require_keys(relative, payload, result, ["schema_version", "tool", "source_package", "instruction_file", "included_files", "missing_files"])
        _require_version(relative, payload, result)
        _require_list(relative, payload, result, "included_files")
        _require_list(relative, payload, result, "missing_files")


def _validate_object(relative: str, payload: Any, result: SchemaValidationResult) -> None:
    if not isinstance(payload, dict):
        result.add(relative, "error", "Expected a JSON object.")


def _require_keys(relative: str, payload: dict[str, Any], result: SchemaValidationResult, keys: list[str]) -> None:
    for key in keys:
        if key not in payload:
            result.add(relative, "error", f"Missing required field `{key}`.")


def _require_version(relative: str, payload: dict[str, Any], result: SchemaValidationResult) -> None:
    version = payload.get("schema_version")
    if version != SCHEMA_VERSION:
        result.add(relative, "error", f"Expected schema_version `{SCHEMA_VERSION}`, got `{version}`.")


def _require_list(relative: str, payload: dict[str, Any], result: SchemaValidationResult, key: str) -> None:
    if key in payload and not isinstance(payload[key], list):
        result.add(relative, "error", f"Field `{key}` must be an array.")


def _require_object(relative: str, payload: dict[str, Any], result: SchemaValidationResult, key: str) -> None:
    if key in payload and not isinstance(payload[key], dict):
        result.add(relative, "error", f"Field `{key}` must be an object.")


def _to_markdown(result: SchemaValidationResult) -> str:
    lines = [
        "# Schema Validation Result",
        "",
        f"- Package: `{result.package_dir}`",
        f"- Schema version: `{result.schema_version}`",
        f"- Status: `{result.status}`",
        f"- Valid: `{result.valid}`",
        "",
        "## Checked files",
    ]
    lines.extend([f"- `{item}`" for item in result.checked_files] or ["- None"])
    lines.extend(["", "## Findings"])
    if result.findings:
        for item in result.findings:
            lines.append(f"- `{item.level}` `{item.path}`: {item.message}")
    else:
        lines.append("- No schema validation findings.")
    lines.append("")
    return "\n".join(lines)
