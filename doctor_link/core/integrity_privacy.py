from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from doctor_link.core.models import utc_now_iso

INTEGRITY_SCHEMA = "doctor-link-integrity-manifest-v1"
PRIVACY_POLICY_SCHEMA = "doctor-link-privacy-policy-v1"
DEFAULT_PRIVACY_PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "api_key": r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}",
    "private_key": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
}
DEFAULT_EXCLUDE_GLOBS = [".git/**", "__pycache__/**", ".pytest_cache/**", "dist/**", "build/**"]


@dataclass
class IntegrityManifest:
    root: str
    generated_at: str = field(default_factory=utc_now_iso)
    schema: str = INTEGRITY_SCHEMA
    signed: bool = False
    files: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IntegrityVerifyResult:
    status: str
    root: str
    checked_at: str = field(default_factory=utc_now_iso)
    checked_files: int = 0
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrivacyPolicy:
    schema: str = PRIVACY_POLICY_SCHEMA
    allow_export_with_findings: bool = False
    exclude_globs: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE_GLOBS))
    patterns: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_PRIVACY_PATTERNS))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrivacyScanResult:
    status: str
    root: str
    scanned_at: str = field(default_factory=utc_now_iso)
    scanned_files: int = 0
    findings: list[dict[str, Any]] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GateResult:
    status: str
    gate: str
    root: str
    generated_at: str = field(default_factory=utc_now_iso)
    findings: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_integrity_manifest(root: Path, include_globs: list[str] | None = None, exclude_globs: list[str] | None = None) -> IntegrityManifest:
    root = root.resolve()
    excludes = exclude_globs or DEFAULT_EXCLUDE_GLOBS
    files: list[dict[str, Any]] = []
    warnings = [_finding("warning", "unsigned-package", "Integrity manifest is unsigned by design.")]
    for path in _iter_files(root, include_globs, excludes):
        rel = _safe_relative(path, root)
        files.append(
            {
                "path": rel,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return IntegrityManifest(root=str(root), signed=False, files=files, warnings=warnings)


def write_integrity_manifest(root: Path, output: Path, include_globs: list[str] | None = None, exclude_globs: list[str] | None = None) -> IntegrityManifest:
    manifest = build_integrity_manifest(root, include_globs, exclude_globs)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def verify_integrity_manifest(root: Path, manifest_path: Path) -> IntegrityVerifyResult:
    root = root.resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    findings: list[dict[str, Any]] = []
    if payload.get("schema") != INTEGRITY_SCHEMA:
        findings.append(_finding("blocking", "schema-unsupported", "Integrity manifest schema is unsupported."))
    if not payload.get("signed"):
        findings.append(_finding("warning", "unsigned-package", "Integrity manifest is unsigned."))
    checked = 0
    manifest_files = payload.get("files") if isinstance(payload.get("files"), list) else []
    for item in manifest_files:
        rel_path = str(item.get("path") or "")
        if _unsafe_relative_path(rel_path):
            findings.append(_finding("blocking", "unsafe-path", f"Unsafe path in manifest: {rel_path}", path=rel_path))
            continue
        path = (root / rel_path).resolve()
        if not _is_relative_to(path, root):
            findings.append(_finding("blocking", "unsafe-path", f"Manifest path escapes root: {rel_path}", path=rel_path))
            continue
        if not path.exists():
            findings.append(_finding("blocking", "missing-file", f"File is missing: {rel_path}", path=rel_path))
            continue
        checked += 1
        actual = _sha256(path)
        expected = str(item.get("sha256") or "")
        if actual != expected:
            findings.append(_finding("blocking", "hash-mismatch", f"Hash mismatch: {rel_path}", path=rel_path))
    status = "passed" if not any(item["severity"] == "blocking" for item in findings) else "blocked"
    return IntegrityVerifyResult(status=status, root=str(root), checked_files=checked, findings=findings)


def load_privacy_policy(path: Path | None = None) -> PrivacyPolicy:
    if path is None or not path.exists():
        return PrivacyPolicy()
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return PrivacyPolicy()
    patterns = dict(DEFAULT_PRIVACY_PATTERNS)
    custom_patterns = payload.get("patterns")
    if isinstance(custom_patterns, dict):
        patterns.update({str(key): str(value) for key, value in custom_patterns.items()})
    exclude_globs = payload.get("exclude_globs")
    excludes = [str(item) for item in exclude_globs] if isinstance(exclude_globs, list) else list(DEFAULT_EXCLUDE_GLOBS)
    return PrivacyPolicy(
        schema=str(payload.get("schema") or PRIVACY_POLICY_SCHEMA),
        allow_export_with_findings=bool(payload.get("allow_export_with_findings", False)),
        exclude_globs=excludes,
        patterns=patterns,
    )


def scan_privacy(root: Path, policy_path: Path | None = None, include_globs: list[str] | None = None) -> PrivacyScanResult:
    root = root.resolve()
    policy = load_privacy_policy(policy_path)
    findings: list[dict[str, Any]] = []
    scanned = 0
    compiled = _compile_patterns(policy.patterns, findings)
    for path in _iter_files(root, include_globs, policy.exclude_globs):
        rel = _safe_relative(path, root)
        text = _read_text(path)
        if text is None:
            continue
        scanned += 1
        for name, pattern in compiled.items():
            for match in pattern.finditer(text):
                findings.append(
                    _finding(
                        "blocking",
                        "privacy-match",
                        f"Privacy pattern matched: {name}",
                        path=rel,
                        extra={"pattern": name, "line": _line_number(text, match.start())},
                    )
                )
    status = "passed" if not any(item["severity"] == "blocking" for item in findings) else "blocked"
    return PrivacyScanResult(status=status, root=str(root), scanned_files=scanned, findings=findings, policy=policy.to_dict())


def redaction_gate(root: Path, policy_path: Path | None = None, include_globs: list[str] | None = None) -> GateResult:
    report = scan_privacy(root, policy_path, include_globs)
    status = "passed" if report.status == "passed" else "blocked"
    return GateResult(status=status, gate="redaction", root=str(root.resolve()), findings=report.findings, report=report.to_dict())


def export_safety_gate(root: Path, policy_path: Path | None = None, manifest_path: Path | None = None) -> GateResult:
    privacy = scan_privacy(root, policy_path)
    findings = list(privacy.findings)
    if manifest_path is not None:
        integrity = verify_integrity_manifest(root, manifest_path)
        findings.extend(integrity.findings)
    policy = PrivacyPolicy(**privacy.policy) if privacy.policy else PrivacyPolicy()
    has_blockers = any(item["severity"] == "blocking" for item in findings)
    status = "passed" if not has_blockers or policy.allow_export_with_findings else "blocked"
    return GateResult(
        status=status,
        gate="export-safety",
        root=str(root.resolve()),
        findings=findings,
        report={"privacy": privacy.to_dict(), "manifest_path": str(manifest_path) if manifest_path else None},
    )


def write_gate_result(result: GateResult, output: Path) -> GateResult:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def write_privacy_scan(result: PrivacyScanResult, output: Path) -> PrivacyScanResult:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def write_integrity_verify(result: IntegrityVerifyResult, output: Path) -> IntegrityVerifyResult:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def _iter_files(root: Path, include_globs: list[str] | None, exclude_globs: list[str]) -> list[Path]:
    candidates = [path for path in root.rglob("*") if path.is_file()]
    files: list[Path] = []
    for path in candidates:
        rel = _safe_relative(path, root)
        if include_globs and not any(fnmatch.fnmatch(rel, pattern) for pattern in include_globs):
            continue
        if any(fnmatch.fnmatch(rel, pattern) for pattern in exclude_globs):
            continue
        files.append(path)
    return sorted(files)


def _compile_patterns(patterns: dict[str, str], findings: list[dict[str, Any]]) -> dict[str, re.Pattern[str]]:
    compiled: dict[str, re.Pattern[str]] = {}
    for name, pattern in patterns.items():
        try:
            compiled[name] = re.compile(pattern)
        except re.error as exc:
            findings.append(_finding("warning", "invalid-pattern", f"Invalid privacy pattern {name}: {exc}"))
    return compiled


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    except OSError:
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _unsafe_relative_path(value: str) -> bool:
    return value.startswith("/") or ".." in Path(value).parts


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _finding(
    severity: str,
    code: str,
    message: str,
    path: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if path:
        item["path"] = path
    if extra:
        item.update(extra)
    return item
