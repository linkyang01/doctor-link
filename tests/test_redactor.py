from __future__ import annotations

import json
from pathlib import Path

from doctor_link.core.collector import collect_into_package
from doctor_link.core.models import DiagnosticEvent
from doctor_link.core.package_builder import build_diagnostic_package
from doctor_link.core.redactor import RedactionOptions, redact_file, redact_files, redact_text


def _build_package(tmp_path: Path) -> Path:
    package = build_diagnostic_package(
        DiagnosticEvent(project="Doctor link", category="redaction", summary="Redaction test"),
        tmp_path / "DoctorReports",
    )
    assert package.root_dir is not None
    return package.root_dir


def test_redact_text_redacts_default_secret_patterns() -> None:
    text = "password=super-secret api_key=abc1234567890 Authorization: Bearer tokenvalue123456"

    result = redact_text(text)

    assert result.changed is True
    assert "super-secret" not in result.redacted_text
    assert "abc1234567890" not in result.redacted_text
    assert "tokenvalue123456" not in result.redacted_text
    assert result.redacted_text.count("[REDACTED]") >= 3


def test_redact_text_supports_optional_email_phone_and_custom_patterns() -> None:
    text = "email user@example.com phone +1 415 555 1212 custom INTERNAL-CODE-123"

    result = redact_text(
        text,
        RedactionOptions(
            redact_email=True,
            redact_phone=True,
            custom_patterns=[r"INTERNAL-CODE-\d+"],
        ),
    )

    assert "user@example.com" not in result.redacted_text
    assert "INTERNAL-CODE-123" not in result.redacted_text
    assert "[REDACTED]" in result.redacted_text


def test_redact_file_and_report(tmp_path: Path) -> None:
    file_path = tmp_path / "app.log"
    file_path.write_text("secret=should-hide", encoding="utf-8")

    result = redact_file(file_path)

    assert result.changed is True
    assert "should-hide" not in file_path.read_text(encoding="utf-8")

    report = redact_files([file_path], tmp_path / "redaction-report.md")
    assert (tmp_path / "redaction-report.md").exists()
    assert (tmp_path / "redaction-report.json").exists()
    assert report.files


def test_collect_redacts_logs_and_command_output_by_default(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    log_file = tmp_path / "app.log"
    log_file.write_text("password=log-secret", encoding="utf-8")

    result = collect_into_package(
        package_dir,
        log_patterns=[str(log_file)],
        commands=["python -c \"print('api_key=commandsecret123')\""],
    )

    copied_logs = list((package_dir / "evidence" / "logs").iterdir())
    assert copied_logs
    assert "log-secret" not in copied_logs[0].read_text(encoding="utf-8")

    command_payload = json.loads((package_dir / "evidence" / "command-output" / "command-1.json").read_text(encoding="utf-8"))
    assert "commandsecret123" not in command_payload["stdout"]
    assert (package_dir / "redaction-report.md").exists()
    assert result.redaction_report is not None
    assert result.redaction_report["total_replacements"] >= 2


def test_collect_can_disable_redaction(tmp_path: Path) -> None:
    package_dir = _build_package(tmp_path)
    log_file = tmp_path / "app.log"
    log_file.write_text("password=keep-secret", encoding="utf-8")

    result = collect_into_package(package_dir, log_patterns=[str(log_file)], redact=False)

    copied_logs = list((package_dir / "evidence" / "logs").iterdir())
    assert "keep-secret" in copied_logs[0].read_text(encoding="utf-8")
    assert result.redaction_report is None
