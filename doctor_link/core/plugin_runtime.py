from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doctor_link.core.command_runner import run_command
from doctor_link.core.models import utc_now_iso

PLUGIN_SCHEMA = "doctor-link-plugin-v1"
DEFAULT_PLUGIN_DIRS = (".doctorlink/plugins", "plugins", "DoctorPlugins")
SUPPORTED_EXTENSION_POINTS = {"collector", "renderer", "handoff", "verification"}
SUPPORTED_PERMISSIONS = {"read_project", "write_reports", "run_local_command"}


@dataclass
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    schema: str = PLUGIN_SCHEMA
    description: str = ""
    extension_points: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    commands: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PluginValidationResult:
    plugin_id: str
    valid: bool
    status: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    manifest: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PluginRunResult:
    plugin_id: str
    extension_point: str
    status: str
    started_at: str
    completed_at: str
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    command: list[str] = field(default_factory=list)
    dry_run: bool = True
    explicit_user_approval: bool = False
    audit_record: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PluginCatalog:
    plugins: list[PluginManifest] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugins": [plugin.to_dict() for plugin in self.plugins],
            "findings": self.findings,
        }


def discover_plugins(project_root: Path, plugins_dir: Path | None = None) -> PluginCatalog:
    roots = _candidate_roots(project_root, plugins_dir)
    plugins: list[PluginManifest] = []
    findings: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        manifest_paths = sorted(root.rglob("plugin.yml")) + sorted(root.rglob("plugin.yaml"))
        for path in manifest_paths:
            try:
                plugins.append(load_plugin_manifest(path))
            except ValueError as exc:
                findings.append(_finding("blocking", "plugin-manifest-invalid", str(exc), path=str(path)))
    return PluginCatalog(plugins=plugins, findings=findings)


def load_plugin_manifest(path: Path) -> PluginManifest:
    payload = _read_manifest_payload(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Plugin manifest is not a mapping: {path}")
    return PluginManifest(
        plugin_id=str(payload.get("id") or payload.get("plugin_id") or ""),
        name=str(payload.get("name") or ""),
        version=str(payload.get("version") or ""),
        schema=str(payload.get("schema") or PLUGIN_SCHEMA),
        description=str(payload.get("description") or ""),
        extension_points=_string_list(payload.get("extension_points")),
        permissions=_string_list(payload.get("permissions")),
        commands=_commands(payload.get("commands")),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        source_path=str(path),
    )


def validate_plugin_manifest(manifest: PluginManifest) -> PluginValidationResult:
    findings: list[dict[str, Any]] = []
    if manifest.schema != PLUGIN_SCHEMA:
        findings.append(_finding("blocking", "schema-unsupported", f"Unsupported plugin schema: {manifest.schema}"))
    if not manifest.plugin_id:
        findings.append(_finding("blocking", "id-missing", "Plugin id is required."))
    if not manifest.name:
        findings.append(_finding("blocking", "name-missing", "Plugin name is required."))
    if not manifest.version:
        findings.append(_finding("blocking", "version-missing", "Plugin version is required."))
    if not manifest.extension_points:
        findings.append(_finding("blocking", "extension-points-missing", "At least one extension point is required."))
    unknown_extension_points = [item for item in manifest.extension_points if item not in SUPPORTED_EXTENSION_POINTS]
    if unknown_extension_points:
        findings.append(
            _finding(
                "blocking",
                "extension-point-unsupported",
                "Unsupported extension points: " + ", ".join(unknown_extension_points),
            )
        )
    unknown_permissions = [item for item in manifest.permissions if item not in SUPPORTED_PERMISSIONS]
    if unknown_permissions:
        findings.append(
            _finding(
                "blocking",
                "permission-unsupported",
                "Unsupported permissions: " + ", ".join(unknown_permissions),
            )
        )
    if "run_local_command" in manifest.permissions and not manifest.commands:
        findings.append(_finding("blocking", "commands-missing", "run_local_command permission requires commands."))
    for extension_point in manifest.extension_points:
        if extension_point not in manifest.commands:
            findings.append(
                _finding(
                    "warning",
                    "command-missing",
                    f"No command configured for extension point: {extension_point}",
                )
            )
    status = "passed" if not any(item.get("severity") == "blocking" for item in findings) else "blocked"
    return PluginValidationResult(
        plugin_id=manifest.plugin_id,
        valid=status == "passed",
        status=status,
        findings=findings,
        manifest=manifest.to_dict(),
    )


def validate_plugin_file(path: Path) -> PluginValidationResult:
    return validate_plugin_manifest(load_plugin_manifest(path))


def run_plugin(
    project_root: Path,
    plugin_id: str,
    extension_point: str,
    plugins_dir: Path | None = None,
    output_dir: Path | None = None,
    timeout_seconds: int = 60,
    allow_run: bool = False,
) -> PluginRunResult:
    catalog = discover_plugins(project_root, plugins_dir)
    manifest = next((item for item in catalog.plugins if item.plugin_id == plugin_id), None)
    if manifest is None:
        raise ValueError(f"Plugin not found: {plugin_id}")
    validation = validate_plugin_manifest(manifest)
    if not validation.valid:
        raise ValueError(f"Plugin validation failed: {plugin_id}")
    if extension_point not in manifest.extension_points:
        raise ValueError(f"Plugin does not support extension point: {extension_point}")
    if "run_local_command" not in manifest.permissions:
        raise ValueError("Plugin does not have run_local_command permission.")
    command = manifest.commands.get(extension_point)
    if not command:
        raise ValueError(f"No command configured for extension point: {extension_point}")
    started_at = utc_now_iso()
    if not allow_run:
        completed_at = utc_now_iso()
        status = "dry-run"
        audit = _audit_record(manifest, extension_point, command, status, started_at, completed_at, None, dry_run=True, explicit_user_approval=False)
        result = PluginRunResult(
            plugin_id=manifest.plugin_id,
            extension_point=extension_point,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            return_code=None,
            stdout="",
            stderr="",
            command=command,
            dry_run=True,
            explicit_user_approval=False,
            audit_record=audit,
        )
        _write_plugin_run(output_dir or project_root / "DoctorReports" / "plugins", result)
        return result
    process = run_command(command, cwd=project_root, timeout_seconds=timeout_seconds)
    completed_at = utc_now_iso()
    status = "passed" if process.returncode == 0 else "failed"
    audit = _audit_record(manifest, extension_point, command, status, started_at, completed_at, process.returncode, dry_run=False, explicit_user_approval=True)
    result = PluginRunResult(
        plugin_id=manifest.plugin_id,
        extension_point=extension_point,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        return_code=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
        command=command,
        dry_run=False,
        explicit_user_approval=True,
        audit_record=audit,
    )
    _write_plugin_run(output_dir or project_root / "DoctorReports" / "plugins", result)
    return result


def _candidate_roots(project_root: Path, plugins_dir: Path | None) -> list[Path]:
    project_root = project_root.resolve()
    if plugins_dir is not None:
        return [plugins_dir.resolve()]
    return [(project_root / item).resolve() for item in DEFAULT_PLUGIN_DIRS]


def _read_manifest_payload(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _commands(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    commands: dict[str, list[str]] = {}
    for key, command in value.items():
        if isinstance(command, list):
            commands[str(key)] = [str(part) for part in command]
        elif isinstance(command, str):
            commands[str(key)] = command.split()
    return commands


def _write_plugin_run(output_dir: Path, result: PluginRunResult) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{result.plugin_id}-{result.extension_point}-run.json"
    (output_dir / filename).write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    with (output_dir / "plugin-audit.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result.audit_record, ensure_ascii=False) + "\n")


def _audit_record(
    manifest: PluginManifest,
    extension_point: str,
    command: list[str],
    status: str,
    started_at: str,
    completed_at: str,
    return_code: int | None,
    dry_run: bool,
    explicit_user_approval: bool,
) -> dict[str, Any]:
    return {
        "schema": "doctor-link-plugin-audit-v1",
        "plugin_id": manifest.plugin_id,
        "plugin_name": manifest.name,
        "plugin_version": manifest.version,
        "extension_point": extension_point,
        "permissions": manifest.permissions,
        "command": command,
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "return_code": return_code,
        "dry_run": dry_run,
        "explicit_user_approval": explicit_user_approval,
        "local_execution_boundary": True,
        "sandbox_boundary": "local-process-boundary",
        "external_network_policy": "not-managed-by-doctor-link",
    }


def _finding(severity: str, code: str, message: str, path: str | None = None) -> dict[str, Any]:
    item = {"severity": severity, "code": code, "message": message}
    if path:
        item["path"] = path
    return item
