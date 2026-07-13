from __future__ import annotations

from pathlib import Path


REQUIRED_DOCS = [
    "docs/quick-start.md",
    "docs/cli-reference.md",
    "docs/automatic-solve.md",
    "docs/diagnostic-package-format.md",
    "docs/ai-coding-workflow.md",
    "docs/local-workbench.md",
    "docs/troubleshooting.md",
    "docs/documentation-parity.md",
]


def test_required_user_docs_exist_and_have_headings() -> None:
    for doc in REQUIRED_DOCS:
        path = Path(doc)
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# "), doc
        assert "doctor-link" in text.lower() or "Doctor link" in text


def test_cli_reference_mentions_core_command_groups() -> None:
    text = Path("docs/cli-reference.md").read_text(encoding="utf-8")

    for command in [
        "doctor-link report",
        "doctor-link collect",
        "doctor-link verify",
        "doctor-link handoff",
        "doctor-link diagnose verify",
        "doctor-link health",
        "doctor-link solve",
    ]:
        assert command in text


def test_troubleshooting_mentions_privacy_and_release_boundary() -> None:
    text = Path("docs/troubleshooting.md").read_text(encoding="utf-8").lower()

    assert "sensitive data" in text
    assert "without explicit authorization" in text
