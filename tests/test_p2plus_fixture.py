from __future__ import annotations

from pathlib import Path

from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.web_review_summary import build_evidence_reference_summaries, verification_status_reasons


FIXTURE = Path("tests/fixtures/p2plus_sample_package")


def test_p2plus_fixture_can_be_read_and_rendered() -> None:
    view = read_package_view(FIXTURE)
    html = render_package_detail_html(view)

    assert "P2+ Sample Diagnostic Package" in html
    assert "The sample behavior is not acceptable" in html
    assert "Report Comparison" in html
    assert "not_verified" in html
    assert "AI Handoff Blocks" in html
    assert "Referenced by:" in html
    assert "Back to index" in html


def test_p2plus_fixture_review_summaries() -> None:
    view = read_package_view(FIXTURE)
    summaries = build_evidence_reference_summaries(view)
    reasons = verification_status_reasons(view)

    summary = summaries["evidence/logs/app.log"]
    assert summary.timeline_refs
    assert summary.test_record_refs
    assert summary.verification_refs
    assert any("missing evidence" in reason for reason in reasons)
    assert any("Report comparison" in reason for reason in reasons)
