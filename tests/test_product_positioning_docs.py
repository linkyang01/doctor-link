from __future__ import annotations

from pathlib import Path


POSITIONING_DOCS = [
    "docs/product-overview.md",
    "docs/use-cases/non-programmer-user.md",
    "docs/use-cases/ai-coding-tool.md",
    "docs/use-cases/developer.md",
    "docs/use-cases/team-workflow.md",
    "docs/architecture-overview.md",
    "docs/roadmap.md",
    "CONTRIBUTING.md",
    "docs/issue-triage.md",
]


def test_product_positioning_docs_exist() -> None:
    for path in POSITIONING_DOCS:
        text = Path(path).read_text(encoding="utf-8")
        assert text.startswith("# "), path
        assert "Doctor link" in text, path


def test_product_overview_states_positioning_and_boundaries() -> None:
    text = Path("docs/product-overview.md").read_text(encoding="utf-8")

    assert "local-first diagnostic context layer" in text
    assert "does not replace AI Coding tools" in text
    assert "does not publish releases" in text


def test_architecture_overview_has_mermaid_source() -> None:
    text = Path("docs/architecture-overview.md").read_text(encoding="utf-8")

    assert "```mermaid" in text
    assert "Diagnostic Package" in text
    assert "Local read-only" in text


def test_roadmap_and_triage_keep_future_work_and_verification_boundaries() -> None:
    roadmap = Path("docs/roadmap.md").read_text(encoding="utf-8")
    triage = Path("docs/issue-triage.md").read_text(encoding="utf-8")

    assert "require separate design, security review, explicit authorization" in roadmap
    assert "not commitments for the next release" in roadmap
    assert "Verification evidence is required" in triage
