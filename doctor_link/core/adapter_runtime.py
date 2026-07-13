from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doctor_link.core.command_runner import run_command
from doctor_link.core.models import utc_now_iso

ADAPTER_SCHEMA = "doctor-link-adapter-v1"
DEFAULT_ADAPTER_DIRS = (".doctorlink/adapters", "adapters", "DoctorAdapters")
SUPPORTED_CAPABILITIES = {"evidence_collector", "verification", "handoff"}


@dataclass
class AdapterManifest:
    adapter_id: str
    name: str
    version: str
    schema: str = ADAPTER_SCHEMA
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    commands: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdapterValidationResult:
    adapter_id: str
    valid: bool
    status: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    manifest: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdapterRunResult:
    adapter_id: str
    capability: str
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
class AdapterCatalog:
    adapters: list[AdapterManifest] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapters": [adapter.to_dict() for adapter in self.adapters],
            "findings": self.findings,
        }


def discover_adapters(project_root: Path, adapters_dir: Path | None = None) -> AdapterCatalog:
    roots = _candidate_roots(project_root, adapters_dir)
    adapters: list[AdapterManifest] = []
    findings: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("adapter.yml")) + sorted(root.rglob("adapter.yaml")):
            try:
                manifest = load_adapter_manifest(path)
                adapters.append(manifest)
            except ValueError as exc:
                findings.append(_finding("blocking", "adapter-manifest-invalid", str(exc), path=str(path)))
    return AdapterCatalog(adapters=adapters, findings=findings)


def load_adapter_manifest(path: Path) -> AdapterManifest:
    payload = _read_manifest_payload(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Adapter manifest is not a mapping: {path}")
    return AdapterManifest(
        adapter_id=str(payload.get("id") or payload.get("adapter_id") or ""),
        name=str(payload.get("name") or ""),
        version=str(payload.get("version") or ""),
        schema=str(payload.get("schema") or ADAPTER_SCHEMA),
        description=str(payload.get("description") or ""),
        capabilities=_string_list(payload.get("capabilities")),
        commands=_commands(payload.get("commands")),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        source_path=str(path),
    )


def validate_adapter_manifest(manifest: AdapterManifest) -> AdapterValidationResult:
    findings: list[dict[str, Any]] = []
    if manifest.schema != ADAPTER_SCHEMA:
        findings.append(_finding("blocking", "schema-unsupported", f"Unsupported adapter schema: {manifest.schema}"))
    if not manifest.adapter_id:
        findings.append(_finding("blocking", "id-missing", "Adapter id is required."))
    if not manifest.name:
        findings.append(_finding("blocking", "name-missing", "Adapter name is required."))
    if not manifest.version:
        findings.append(_finding("blocking", "version-missing", "Adapter version is required."))
    unknown_capabilities = [item for item in manifest.capabilities if item not in SUPPORTED_CAPABILITIES]
    if unknown_capabilities:
        findings.append(
            _finding(
                "blocking",
                "capability-unsupported",
                "Unsupported capabilities: " + ", ".join(unknown_capabilities),
            )
        )
    if not manifest.capabilities:
        findings.append(_finding("blocking", "capabilities-missing", "At least one capability is required."))
    for capability in manifest.capabilities:
        if capability not in manifest.commands:
            findings.append(
                _finding(
                    "warning",
                    "command-missing",
                    f"No command configured for capability: {capability}",
                )
            )
    status = "passed" if not any(item.get("severity") == "blocking" for item in findings) else "blocked"
    return AdapterValidationResult(
        adapter_id=manifest.adapter_id,
        valid=status == "passed",
        status=status,
        findings=findings,
        manifest=manifest.to_dict(),
    )


def validate_adapter_file(path: Path) -> AdapterValidationResult:
    return validate_adapter_manifest(load_adapter_manifest(path))


def run_adapter(
    project_root: Path,
    adapter_id: str,
    capability: str,
    adapters_dir: Path | None = None,
    output_dir: Path | None = None,
    timeout_seconds: int = 60,
    allow_run: bool = False,
) -> AdapterRunResult:
    catalog = discover_adapters(project_root, adapters_dir)
    manifest = next((item for item in catalog.adapters if item.adapter_id == adapter_id), None)
    if manifest is None:
        raise ValueError(f"Adapter not found: {adapter_id}")
    validation = validate_adapter_manifest(manifest)
    if not validation.valid:
        raise ValueError(f"Adapter validation failed: {adapter_id}")
    if capability not in manifest.capabilities:
        raise ValueError(f"Adapter does not support capability: {capability}")
    command = manifest.commands.get(capability)
    if not command:
        raise ValueError(f"No command configured for capability: {capability}")
    started_at = utc_now_iso()
    if not allow_run:
        completed_at = utc_now_iso()
        status = "dry-run"
        audit = _audit_record(manifest, capability, command, status, started_at, completed_at, None, dry_run=True, explicit_user_approval=False)
        result = AdapterRunResult(
            adapter_id=manifest.adapter_id,
            capability=capability,
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
        _write_adapter_run(output_dir or project_root / "DoctorReports" / "adapters", result)
        return result
    process = run_command(command, cwd=project_root, timeout_seconds=timeout_seconds)
    completed_at = utc_now_iso()
    status = "passed" if process.returncode == 0 else "failed"
    audit = _audit_record(manifest, capability, command, status, started_at, completed_at, process.returncode, dry_run=False, explicit_user_approval=True)
    result = AdapterRunResult(
        adapter_id=manifest.adapter_id,
        capability=capability,
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
    _write_adapter_run(output_dir or project_root / "DoctorReports" / "adapters", result)
    return result


def _candidate_roots(project_root: Path, adapters_dir: Path | None) -> list[Path]:
    project_root = project_root.resolve()
    if adapters_dir is not None:
        return [adapters_dir.resolve()]
    return [(project_root / item).resolve() for item in DEFAULT_ADAPTER_DIRS]


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


def _write_adapter_run(output_dir: Path, result: AdapterRunResult) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{result.adapter_id}-{result.capability}-run.json"
    (output_dir / filename).write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "adapter-audit.jsonl").open("a", encoding="utf-8").write(
        json.dumps(result.audit_record, ensure_ascii=False) + "\n"
    )


def _audit_record(
    manifest: AdapterManifest,
    capability: str,
    command: list[str],
    status: str,
    started_at: str,
    completed_at: str,
    return_code: int | None,
    dry_run: bool,
    explicit_user_approval: bool,
) -> dict[str, Any]:
    return {
        "schema": "doctor-link-adapter-audit-v1",
        "adapter_id": manifest.adapter_id,
        "adapter_name": manifest.name,
        "adapter_version": manifest.version,
        "capability": capability,
        "command": command,
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "return_code": return_code,
        "dry_run": dry_run,
        "explicit_user_approval": explicit_user_approval,
        "local_execution_boundary": True,
        "external_network_policy": "not-managed-by-doctor-link",
    }


def _finding(severity: str, code: str, message: str, path: str | None = None) -> dict[str, Any]:
    item = {"severity": severity, "code": code, "message": message}
    if path:
        item["path"] = path
    return item
