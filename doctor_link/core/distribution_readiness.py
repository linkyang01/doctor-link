from __future__ import annotations

import csv
import hashlib
import json
import sys
import tarfile
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso

REQUIRED_PYPROJECT_FIELDS = ["name", "version", "description", "readme", "requires-python"]
SUPPORTED_ARTIFACT_SUFFIXES = (".whl", ".tar.gz", ".zip")


@dataclass
class DistributionArtifact:
    path: str
    name: str
    kind: str
    size_bytes: int
    sha256: str
    metadata: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DistributionReadinessReport:
    project_root: str
    dist_dir: str
    output_dir: str
    generated_at: str = field(default_factory=utc_now_iso)
    status: str = "unknown"
    blocking_count: int = 0
    warning_count: int = 0
    artifacts: list[DistributionArtifact] = field(default_factory=list)
    checklist: list[dict[str, Any]] = field(default_factory=list)
    target_environment: dict[str, Any] = field(default_factory=dict)
    manifest: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link Distribution Readiness Report",
            "",
            f"- Generated at: `{self.generated_at}`",
            f"- Status: `{self.status}`",
            f"- Project root: `{self.project_root}`",
            f"- Dist dir: `{self.dist_dir}`",
            f"- Blocking findings: `{self.blocking_count}`",
            f"- Warning findings: `{self.warning_count}`",
            f"- Artifacts: `{len(self.artifacts)}`",
            "",
            "## Blocking checklist",
            "",
        ]
        for item in self.checklist:
            marker = "x" if item.get("passed") else " "
            severity = item.get("severity", "info")
            lines.append(f"- [{marker}] `{item.get('id')}` ({severity}) — {item.get('message')}")
        lines.extend(["", "## Artifacts", ""])
        if not self.artifacts:
            lines.append("- None")
        for artifact in self.artifacts:
            lines.append(
                f"- `{artifact.name}` — kind=`{artifact.kind}`, "
                f"size=`{artifact.size_bytes}`, sha256=`{artifact.sha256}`"
            )
            for finding in artifact.findings:
                lines.append(
                    f"  - {finding.get('severity')}: "
                    f"{finding.get('code')} — {finding.get('message')}"
                )
        lines.extend(
            [
                "",
                "## Target environment",
                "",
                _json_block(self.target_environment),
                "",
                "## Manifest",
                "",
                _json_block(self.manifest),
                "",
            ]
        )
        return "\n".join(lines)


def build_distribution_readiness_report(
    project_root: Path,
    dist_dir: Path | None = None,
    output_dir: Path | None = None,
) -> DistributionReadinessReport:
    project_root = project_root.resolve()
    dist = (dist_dir or project_root / "dist").resolve()
    output = (output_dir or project_root / "DoctorReports" / "distribution").resolve()
    artifacts = _build_artifacts(dist)
    target = _build_target_environment(project_root, dist)
    checklist = _build_checklist(project_root, dist, artifacts, target)
    blocking_count = _count_findings(artifacts, checklist, "blocking")
    warning_count = _count_findings(artifacts, checklist, "warning")
    status = "passed" if blocking_count == 0 else "blocked"
    manifest = _build_manifest(project_root, dist, output, status, artifacts, checklist, target)
    return DistributionReadinessReport(
        project_root=str(project_root),
        dist_dir=str(dist),
        output_dir=str(output),
        status=status,
        blocking_count=blocking_count,
        warning_count=warning_count,
        artifacts=artifacts,
        checklist=checklist,
        target_environment=target,
        manifest=manifest,
    )


def write_distribution_readiness_report(
    project_root: Path,
    dist_dir: Path | None = None,
    output_dir: Path | None = None,
) -> DistributionReadinessReport:
    report = build_distribution_readiness_report(project_root, dist_dir, output_dir)
    out = Path(report.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "distribution-report.json").write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "distribution-report.md").write_text(report.to_markdown(), encoding="utf-8")
    (out / "distribution-manifest.json").write_text(
        json.dumps(report.manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "target-environment.json").write_text(
        json.dumps(report.target_environment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "checksums.sha256").write_text(_checksums_text(report.artifacts), encoding="utf-8")
    return report


def _build_artifacts(dist_dir: Path) -> list[DistributionArtifact]:
    if not dist_dir.exists():
        return []
    artifacts: list[DistributionArtifact] = []
    for path in sorted(item for item in dist_dir.iterdir() if item.is_file()):
        if not _is_supported_artifact(path):
            continue
        kind = _artifact_kind(path)
        metadata, findings = _artifact_metadata(path, kind)
        artifacts.append(
            DistributionArtifact(
                path=str(path),
                name=path.name,
                kind=kind,
                size_bytes=path.stat().st_size,
                sha256=_sha256(path),
                metadata=metadata,
                findings=findings,
            )
        )
    return artifacts


def _artifact_metadata(path: Path, kind: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if kind == "wheel":
        return _wheel_metadata(path)
    if kind == "sdist":
        return _sdist_metadata(path)
    return {}, []


def _wheel_metadata(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            metadata["file_count"] = len(names)
            metadata_path = _first_matching(names, ".dist-info/METADATA")
            wheel_path = _first_matching(names, ".dist-info/WHEEL")
            record_path = _first_matching(names, ".dist-info/RECORD")
            metadata["metadata_file"] = metadata_path
            metadata["wheel_file"] = wheel_path
            metadata["record_file"] = record_path
            if not metadata_path:
                findings.append(_finding("blocking", "wheel-metadata-missing", "Wheel METADATA file is missing."))
            if not wheel_path:
                findings.append(_finding("blocking", "wheel-file-missing", "Wheel WHEEL file is missing."))
            if not record_path:
                findings.append(_finding("blocking", "wheel-record-missing", "Wheel RECORD file is missing."))
            if metadata_path:
                metadata.update(_parse_metadata_text(archive.read(metadata_path).decode("utf-8", errors="replace")))
            if record_path:
                metadata["record_entries"] = _count_record_entries(
                    archive.read(record_path).decode("utf-8", errors="replace")
                )
    except zipfile.BadZipFile:
        findings.append(_finding("blocking", "wheel-invalid-zip", "Wheel is not a valid zip archive."))
    return metadata, findings


def _sdist_metadata(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    try:
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getnames()
            metadata["file_count"] = len(members)
            pyproject_path = _first_name_ending(members, "pyproject.toml")
            pkg_info_path = _first_name_ending(members, "PKG-INFO")
            metadata["pyproject_file"] = pyproject_path
            metadata["pkg_info_file"] = pkg_info_path
            if not pyproject_path:
                findings.append(_finding("warning", "sdist-pyproject-missing", "sdist pyproject.toml was not found."))
            if not pkg_info_path:
                findings.append(_finding("blocking", "sdist-pkg-info-missing", "sdist PKG-INFO was not found."))
            if pkg_info_path:
                member = archive.extractfile(pkg_info_path)
                if member is not None:
                    metadata.update(_parse_metadata_text(member.read().decode("utf-8", errors="replace")))
    except (tarfile.TarError, OSError):
        findings.append(_finding("blocking", "sdist-invalid-tar", "sdist is not a valid gzipped tar archive."))
    return metadata, findings


def _build_target_environment(project_root: Path, dist_dir: Path) -> dict[str, Any]:
    pyproject = _read_pyproject(project_root / "pyproject.toml")
    project = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    return {
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": sys.platform,
        "project_name": project.get("name"),
        "project_version": project.get("version"),
        "requires_python": project.get("requires-python"),
        "dist_dir_exists": dist_dir.exists(),
        "dist_dir": str(dist_dir),
    }


def _build_checklist(
    project_root: Path,
    dist_dir: Path,
    artifacts: list[DistributionArtifact],
    target_environment: dict[str, Any],
) -> list[dict[str, Any]]:
    pyproject = _read_pyproject(project_root / "pyproject.toml")
    project = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    wheel_count = sum(1 for artifact in artifacts if artifact.kind == "wheel")
    sdist_count = sum(1 for artifact in artifacts if artifact.kind == "sdist")
    artifact_blockers = sum(
        1
        for artifact in artifacts
        for finding in artifact.findings
        if finding.get("severity") == "blocking"
    )
    return [
        _check("pyproject-present", (project_root / "pyproject.toml").exists(), "blocking", "pyproject.toml is present."),
        _check(
            "pyproject-required-fields",
            all(project.get(field_name) for field_name in REQUIRED_PYPROJECT_FIELDS),
            "blocking",
            "Required project metadata fields are present.",
        ),
        _check("dist-dir-present", dist_dir.exists(), "blocking", "Distribution directory exists."),
        _check("wheel-present", wheel_count > 0, "blocking", "At least one wheel artifact is present."),
        _check("sdist-present", sdist_count > 0, "blocking", "At least one source distribution artifact is present."),
        _check("artifact-checksums", bool(artifacts), "blocking", "Checksums can be generated for artifacts."),
        _check("artifact-metadata-valid", artifact_blockers == 0, "blocking", "Artifact metadata is readable."),
        _check(
            "target-python-known",
            bool(target_environment.get("python_version")),
            "warning",
            "Target Python version can be detected.",
        ),
    ]


def _build_manifest(
    project_root: Path,
    dist_dir: Path,
    output_dir: Path,
    status: str,
    artifacts: list[DistributionArtifact],
    checklist: list[dict[str, Any]],
    target_environment: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "doctor-link-distribution-manifest-v1",
        "generated_at": utc_now_iso(),
        "project_root": str(project_root),
        "dist_dir": str(dist_dir),
        "output_dir": str(output_dir),
        "status": status,
        "artifacts": [artifact.to_dict() for artifact in artifacts],
        "checklist": checklist,
        "target_environment": target_environment,
        "publish_blocked_by_design": True,
        "notes": [
            "This manifest is a local readiness artifact only.",
            "It does not publish packages, create tags, or upload artifacts.",
        ],
    }


def _count_findings(
    artifacts: list[DistributionArtifact],
    checklist: list[dict[str, Any]],
    severity: str,
) -> int:
    artifact_count = sum(
        1
        for artifact in artifacts
        for finding in artifact.findings
        if finding.get("severity") == severity
    )
    checklist_count = sum(
        1
        for item in checklist
        if not item.get("passed") and item.get("severity") == severity
    )
    return artifact_count + checklist_count


def _checksums_text(artifacts: list[DistributionArtifact]) -> str:
    return "".join(f"{artifact.sha256}  {artifact.name}\n" for artifact in artifacts)


def _is_supported_artifact(path: Path) -> bool:
    name = path.name
    return name.endswith(SUPPORTED_ARTIFACT_SUFFIXES)


def _artifact_kind(path: Path) -> str:
    name = path.name
    if name.endswith(".whl"):
        return "wheel"
    if name.endswith(".tar.gz"):
        return "sdist"
    if name.endswith(".zip"):
        return "archive"
    return "file"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _first_matching(names: list[str], suffix: str) -> str | None:
    return next((name for name in names if name.endswith(suffix)), None)


def _first_name_ending(names: list[str], suffix: str) -> str | None:
    return next((name for name in names if name.endswith(suffix)), None)


def _count_record_entries(text: str) -> int:
    return sum(1 for _ in csv.reader(text.splitlines()))


def _parse_metadata_text(text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for line in text.splitlines():
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized = key.strip().lower().replace("-", "_")
        if normalized in {"name", "version", "summary", "requires_python"}:
            metadata[normalized] = value.strip()
    return metadata


def _read_pyproject(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback is not needed in CI.
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _check(check_id: str, passed: bool, severity: str, message: str) -> dict[str, Any]:
    return {"id": check_id, "passed": passed, "severity": severity, "message": message}


def _finding(severity: str, code: str, message: str) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message}


def _json_block(payload: dict[str, Any]) -> str:
    return "```json\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n```"
