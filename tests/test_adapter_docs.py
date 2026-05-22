from __future__ import annotations

from pathlib import Path


ADAPTER_DOCS = [
    "docs/adapters.md",
    "docs/collector-extension-points.md",
    "docs/handoff-profile-extension-points.md",
    "docs/project-customization.md",
    "docs/future-sdk-boundary.md",
]


def test_adapter_docs_exist_and_have_doctor_link_context() -> None:
    for path in ADAPTER_DOCS:
        text = Path(path).read_text(encoding="utf-8")
        assert text.startswith("# "), path
        assert "Doctor link" in text, path


def test_adapter_docs_keep_sdk_boundary_clear() -> None:
    combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in ADAPTER_DOCS)

    assert "P5 does not introduce a stable SDK" in combined
    assert "does not promise runtime plugin loading" in combined or "P5 only documents" in combined
    assert "configuration-first" in combined


def test_adapter_docs_preserve_safety_rules() -> None:
    combined = "\n".join(Path(path).read_text(encoding="utf-8").lower() for path in ADAPTER_DOCS)

    assert "local-first" in combined
    assert "verification" in combined
    assert "privacy" in combined
    assert "external services" in combined or "paid service" in combined
