from __future__ import annotations

from pathlib import Path


REQUIRED_P5_FINAL_FILES = [
    "docs/p5-final-audit.md",
    "docs/release-notes/0.1.0-draft.md",
    "docs/release-notes/github-release-0.1.0-draft.md",
]


def test_p5_final_release_readiness_files_exist() -> None:
    for path in REQUIRED_P5_FINAL_FILES:
        text = Path(path).read_text(encoding="utf-8")
        assert text.startswith("# "), path
        assert "Draft" in text or "P5" in text


def test_p5_release_drafts_do_not_authorize_publishing() -> None:
    combined = "\n".join(Path(path).read_text(encoding="utf-8").lower() for path in REQUIRED_P5_FINAL_FILES)

    assert "draft only" in combined
    assert "do not publish" in combined or "without explicit authorization" in combined
    assert "no github release was created" in combined
    assert "no pypi package was published" in combined


def test_p5_tracking_files_are_marked_complete() -> None:
    todo = Path("TODO.md").read_text(encoding="utf-8")
    p3p5 = Path("TODO-P3-P5.md").read_text(encoding="utf-8")
    p5 = Path("TODO-P5.md").read_text(encoding="utf-8")

    assert "- [x] P5: Productization and Release Readiness" in todo
    assert "Status: complete." in p3p5
    assert "- [x] P5 final audit: `docs/p5-final-audit.md`" in todo
    assert "- [x] Prepare draft release notes" in p5
    assert "- [x] Stop before publishing unless explicit release authorization is given" in p5


def test_readmes_include_p5_status_and_p6_boundary() -> None:
    english = Path("README.en.md").read_text(encoding="utf-8")
    chinese = Path("README.zh-CN.md").read_text(encoding="utf-8")

    assert "P5: Productization and Release Readiness" in english
    assert "P5：Productization and Release Readiness" in chinese
    assert "P6 implementation requires separate explicit authorization" in english
    assert "P6 实现开发需要单独明确授权" in chinese
