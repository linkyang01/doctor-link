from __future__ import annotations

from pathlib import Path

from doctor_link.core.redactor import REDACTION_TEXT, RedactionOptions, redact_text


SECURITY_DOCS = [
    "docs/privacy-model.md",
    "docs/sensitive-data-handling.md",
    "docs/export-security-checklist.md",
    "docs/diagnostic-package-data.md",
]


def test_security_privacy_docs_exist_and_cover_boundaries() -> None:
    combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in SECURITY_DOCS).lower()

    for path in SECURITY_DOCS:
        assert Path(path).exists(), path
    assert "local-first" in combined
    assert "diagnostic package" in combined
    assert "redaction" in combined
    assert "review" in combined
    assert "do not" in combined or "does not" in combined


def test_redaction_covers_common_sensitive_values() -> None:
    text = "password=secret123 api_key=abc123456789 access_token=token123456789 user@example.com +1 415 555 1212"

    result = redact_text(text, RedactionOptions(redact_email=True, redact_phone=True))

    assert result.changed
    assert "secret123" not in result.redacted_text
    assert "abc123456789" not in result.redacted_text
    assert "token123456789" not in result.redacted_text
    assert "user@example.com" not in result.redacted_text
    assert "415 555 1212" not in result.redacted_text
    assert REDACTION_TEXT in result.redacted_text


def test_custom_redaction_pattern() -> None:
    result = redact_text("internal id TOKEN_ABC123 should hide", RedactionOptions(custom_patterns=[r"TOKEN_[A-Z0-9]+"]))

    assert result.changed
    assert "TOKEN_ABC123" not in result.redacted_text
    assert REDACTION_TEXT in result.redacted_text
