from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml


CONFIG_DIR_NAME = ".doctorlink"


@dataclass
class CollectConfig:
    project_root: str | None = None
    logs: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    probes: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    redact: bool = True
    redact_email: bool = False
    redact_phone: bool = False
    redact_patterns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PackageConfig:
    output_dir: str = "DoctorReports"
    exclude_attachments: bool = False
    exclude_logs: bool = False
    exclude_screenshots: bool = False
    max_file_size: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationConfig:
    write_back: bool = False
    required_signals: list[str] = field(default_factory=lambda: ["test_records", "report_comparison"])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DoctorLinkConfig:
    root_dir: str
    collect: CollectConfig = field(default_factory=CollectConfig)
    package: PackageConfig = field(default_factory=PackageConfig)
    verification: VerificationConfig = field(default_factory=VerificationConfig)
    raw: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_dir": self.root_dir,
            "collect": self.collect.to_dict(),
            "package": self.package.to_dict(),
            "verification": self.verification.to_dict(),
            "raw": self.raw,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def load_config(start_dir: Path | None = None) -> DoctorLinkConfig:
    """Load .doctorlink configuration from a project directory.

    The loader searches upward from start_dir for a .doctorlink directory. Missing
    files are allowed; defaults are returned with warnings.
    """
    root_dir = _find_root(start_dir or Path.cwd())
    config_dir = root_dir / CONFIG_DIR_NAME
    raw: dict[str, Any] = {}
    warnings: list[str] = []
    errors: list[str] = []

    for name in ["doctorlink.yml", "collect.yml", "package.yml", "verification.yml"]:
        path = config_dir / name
        if path.exists():
            try:
                raw[name] = _read_yaml(path)
            except (OSError, yaml.YAMLError) as exc:
                errors.append(f"Invalid config file {path}: {exc}")
        else:
            warnings.append(f"Missing config file: {path}")

    config = DoctorLinkConfig(
        root_dir=str(root_dir),
        collect=_collect_config(raw),
        package=_package_config(raw),
        verification=_verification_config(raw),
        raw=raw,
        warnings=warnings,
        errors=errors,
    )
    config.warnings.extend(validate_config(config))
    return config


def merge_collect_cli(
    config: CollectConfig,
    project_root: Path | None = None,
    log_patterns: Iterable[str] | None = None,
    commands: Iterable[str] | None = None,
    probes: Iterable[Path] | None = None,
    attachments: Iterable[Path] | None = None,
    no_redact: bool = False,
    redact: bool | None = None,
    redact_email: bool = False,
    redact_phone: bool = False,
    custom_patterns: Iterable[str] | None = None,
) -> CollectConfig:
    return CollectConfig(
        project_root=str(project_root) if project_root is not None else config.project_root,
        logs=_prefer_list(log_patterns, config.logs),
        commands=_prefer_list(commands, config.commands),
        probes=[str(item) for item in probes] if probes else list(config.probes),
        attachments=[str(item) for item in attachments] if attachments else list(config.attachments),
        redact=False if no_redact else (redact if redact is not None else config.redact),
        redact_email=redact_email or config.redact_email,
        redact_phone=redact_phone or config.redact_phone,
        redact_patterns=_prefer_list(custom_patterns, config.redact_patterns),
    )


def merge_package_cli(
    config: PackageConfig,
    output: Path | None = None,
    exclude_attachments: bool = False,
    exclude_logs: bool = False,
    exclude_screenshots: bool = False,
    max_file_size: int | None = None,
) -> PackageConfig:
    return PackageConfig(
        output_dir=str(output.parent) if output is not None and output.parent else config.output_dir,
        exclude_attachments=exclude_attachments or config.exclude_attachments,
        exclude_logs=exclude_logs or config.exclude_logs,
        exclude_screenshots=exclude_screenshots or config.exclude_screenshots,
        max_file_size=max_file_size if max_file_size is not None else config.max_file_size,
    )


def merge_verify_cli(config: VerificationConfig, write_back: bool = False) -> VerificationConfig:
    return VerificationConfig(write_back=write_back or config.write_back, required_signals=list(config.required_signals))


def validate_config(config: DoctorLinkConfig) -> list[str]:
    warnings: list[str] = []
    if config.package.max_file_size is not None and config.package.max_file_size < 0:
        warnings.append("package.max_file_size must be non-negative.")
    if not isinstance(config.collect.logs, list):
        warnings.append("collect.logs must be a list.")
    if not isinstance(config.collect.commands, list):
        warnings.append("collect.commands must be a list.")
    return warnings


def _find_root(start_dir: Path) -> Path:
    current = start_dir.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / CONFIG_DIR_NAME).is_dir():
            return candidate
    return current


def _read_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _collect_config(raw: dict[str, Any]) -> CollectConfig:
    doctorlink_collect = raw.get("doctorlink.yml", {}).get("collect", {})
    collect = raw.get("collect.yml", {}).get("collect", raw.get("collect.yml", {}))
    redaction = collect.get("redaction", {}) if isinstance(collect, dict) else {}
    return CollectConfig(
        project_root=_first_str(collect.get("project_root"), doctorlink_collect.get("project_root")),
        logs=_list(collect.get("logs", doctorlink_collect.get("logs", []))),
        commands=_list(collect.get("commands", doctorlink_collect.get("commands", []))),
        probes=_list(collect.get("probes", doctorlink_collect.get("probes", []))),
        attachments=_list(collect.get("attachments", doctorlink_collect.get("attachments", []))),
        redact=bool(redaction.get("enabled", True)),
        redact_email=bool(redaction.get("email", False)),
        redact_phone=bool(redaction.get("phone", False)),
        redact_patterns=_list(redaction.get("patterns", [])),
    )


def _package_config(raw: dict[str, Any]) -> PackageConfig:
    package = raw.get("package.yml", {}).get("package", raw.get("package.yml", {}))
    return PackageConfig(
        output_dir=str(package.get("output_dir", "DoctorReports")),
        exclude_attachments=bool(package.get("exclude_attachments", False)),
        exclude_logs=bool(package.get("exclude_logs", False)),
        exclude_screenshots=bool(package.get("exclude_screenshots", False)),
        max_file_size=package.get("max_file_size"),
    )


def _verification_config(raw: dict[str, Any]) -> VerificationConfig:
    verification = raw.get("verification.yml", {}).get("verification", raw.get("verification.yml", {}))
    if isinstance(verification, list):
        return VerificationConfig(write_back=False, required_signals=["test_records", "report_comparison"])
    return VerificationConfig(
        write_back=bool(verification.get("write_back", False)),
        required_signals=_list(verification.get("required_signals", ["test_records", "report_comparison"])),
    )


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _prefer_list(cli_values: Iterable[Any] | None, config_values: list[str]) -> list[str]:
    values = list(cli_values or [])
    return [str(item) for item in values] if values else list(config_values)


def _first_str(*values: Any) -> str | None:
    for value in values:
        if value is not None:
            return str(value)
    return None
