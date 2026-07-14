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


def test_quick_start_prioritizes_current_user_paths() -> None:
    text = Path("docs/quick-start.md").read_text(encoding="utf-8")

    assert "doctor-link wizard" in text
    assert "doctor-link diagnose-now" in text
    assert "doctor-link solve" in text
    assert "--allow-repair" in text
    assert "npm test" in text
    assert "VlyTestLibrary" not in text


def test_troubleshooting_mentions_privacy_and_release_boundary() -> None:
    text = Path("docs/troubleshooting.md").read_text(encoding="utf-8").lower()

    assert "sensitive data" in text
    assert "without explicit authorization" in text


def test_current_release_is_consistent_across_primary_user_docs() -> None:
    version = Path("VERSION").read_text(encoding="utf-8").strip()
    release = f"v{version}"
    primary_docs = [
        "README.md",
        "docs/installation.md",
        "docs/quick-start.md",
        "docs/project-status.md",
        "docs/readme/README.en.md",
        "docs/readme/README.zh-CN.md",
        f"docs/validation/{release}-release-notes.md",
    ]

    for doc in primary_docs:
        text = Path(doc).read_text(encoding="utf-8")
        assert release in text, doc

    readme = Path("README.md").read_text(encoding="utf-8")
    installation = Path("docs/installation.md").read_text(encoding="utf-8")
    status = Path("docs/project-status.md").read_text(encoding="utf-8")
    release_notes = Path(f"docs/validation/{release}-release-notes.md").read_text(
        encoding="utf-8"
    )

    assert f"Latest published version: [`{release}`]" in readme
    assert f"doctor_link-{version}-py3-none-any.whl" in installation
    assert "Cloud validation and publication remain pending" not in status
    assert "(Draft)" not in release_notes.splitlines()[0]
