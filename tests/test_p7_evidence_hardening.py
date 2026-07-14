from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

from doctor_link.core.collector import collect_into_package
from doctor_link.core.command_runner import resolve_command, run_command
from doctor_link.core.environment_collector import collect_environment
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package


def test_command_runner_records_runtime_metadata(tmp_path: Path) -> None:
    result = run_command([sys.executable, "-c", "print('hello')"], timeout_seconds=10, cwd=tmp_path)
    payload = result.to_dict()

    assert payload["returncode"] == 0
    assert payload["stdout"].strip() == "hello"
    assert payload["cwd"] == str(tmp_path.resolve())
    assert payload["timeout_seconds"] == 10
    assert payload["duration_seconds"] >= 0
    assert payload["stdout_bytes"] > 0
    assert payload["executable_found"] is True


def test_command_runner_resolves_python_alias_without_path(tmp_path: Path) -> None:
    result = run_command(
        ["python", "-c", "print('portable-python')"],
        timeout_seconds=10,
        cwd=tmp_path,
        env={"PATH": ""},
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "portable-python"
    assert result.executable == sys.executable


def test_command_runner_resolves_windows_package_manager_launcher(monkeypatch) -> None:
    launcher = r"C:\Program Files\nodejs\npm.CMD"

    monkeypatch.setattr("doctor_link.core.command_runner.shutil.which", lambda executable, path=None: launcher)

    assert resolve_command(["npm", "test"], env={"PATH": r"C:\Program Files\nodejs"}) == [launcher, "test"]


def test_command_runner_does_not_rewrite_unknown_commands(monkeypatch) -> None:
    monkeypatch.setattr("doctor_link.core.command_runner.shutil.which", lambda executable, path=None: "/tools/custom")

    assert resolve_command(["custom", "check"]) == ["custom", "check"]


def test_command_runner_preserves_invalid_utf8_as_safe_evidence(tmp_path: Path) -> None:
    result = run_command(
        [sys.executable, "-c", "import os; os.write(1, b'valid\\xfftail\\n'); os.write(2, b'warn\\xfeend\\n')"],
        timeout_seconds=10,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert result.stdout == "valid\ufffdtail\n"
    assert result.stderr == "warn\ufffdend\n"
    assert result.stdout_bytes == 11
    assert result.stderr_bytes == 9


def test_command_runner_returns_structured_empty_command_error() -> None:
    result = run_command([])

    assert result.returncode == 127
    assert result.error == "empty_command"
    assert result.stderr == "Command is empty."


def test_command_runner_returns_structured_permission_error(monkeypatch) -> None:
    def deny_execution(*args, **kwargs):
        raise PermissionError(13, "Permission denied", "protected-tool")

    monkeypatch.setattr("doctor_link.core.command_runner.subprocess.run", deny_execution)
    result = run_command(["protected-tool"])

    assert result.returncode == 126
    assert result.error == "permission_denied"
    assert "Permission denied" in result.stderr


def test_command_runner_returns_structured_operating_system_error(monkeypatch) -> None:
    def fail_to_launch(*args, **kwargs):
        raise OSError(5, "Input/output error", "unstable-tool")

    monkeypatch.setattr("doctor_link.core.command_runner.subprocess.run", fail_to_launch)
    result = run_command(["unstable-tool"])

    assert result.returncode == 1
    assert result.error == "os_error"
    assert "Input/output error" in result.stderr


def test_environment_collector_includes_tools_and_project_markers(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    payload = collect_environment(tmp_path)

    assert "tools" in payload
    assert "python" in payload["tools"]
    assert payload["project"]["markers"]["pyproject.toml"] is True
    assert any(item["name"] == "pyproject.toml" for item in payload["project"]["top_level_entries"])


def test_collect_into_package_writes_p7_hardened_evidence(tmp_path: Path) -> None:
    package = build_diagnostic_package(DiagnosticEvent(project="P7 Demo", summary="p7 evidence hardening"), tmp_path / "reports")
    assert package.root_dir is not None
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    log_file = tmp_path / "demo.log"
    log_file.write_text("prefix\n" + "x" * 600_000 + "\nsecret=abc123456789\n", encoding="utf-8")
    binary_log = tmp_path / "binary.log"
    binary_log.write_bytes(b"abc\x00def")
    command = " ".join([shlex.quote(sys.executable), "-c", shlex.quote("print('token=abc123456789')")])

    result = collect_into_package(
        package.root_dir,
        project_root=project_root,
        log_patterns=[str(log_file), str(binary_log)],
        commands=[command],
        command_timeout_seconds=10,
    )

    assert result.integrity_report is not None
    assert result.integrity_report["file_count"] > 0
    assert (package.root_dir / "evidence" / "evidence-integrity-index.json").exists()

    command_payload = json.loads((package.root_dir / "evidence" / "command-output" / "command-1.json").read_text(encoding="utf-8"))
    assert "duration_seconds" in command_payload
    assert command_payload["timeout_seconds"] == 10
    assert "stdout_path" in command_payload
    assert "[REDACTED]" in (package.root_dir / command_payload["stdout_path"]).read_text(encoding="utf-8")

    log_manifest = json.loads((package.root_dir / "evidence" / "test-results" / "log-collection-manifest.json").read_text(encoding="utf-8"))
    assert any(item["truncated"] for item in log_manifest["files"])
    assert any(item["skipped"] and item["reason"] == "binary_file" for item in log_manifest["files"])

    report = json.loads((package.root_dir / "doctor-report.json").read_text(encoding="utf-8"))
    assert "evidence_integrity" in report
    assert report["evidence_integrity"]["hash_algorithm"] == "sha256"
