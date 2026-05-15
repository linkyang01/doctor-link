from __future__ import annotations

from pathlib import Path

from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view
from doctor_link.core.web_review_summary import build_evidence_reference_summaries, verification_status_reasons


def test_p2plus_sample_fixture_renders_workbench() -> None:
    package_dir = Path("tests/fixtures/p2plus_sample_package")
    view = read_package_view(package_dir)

    html = render_package_detail_html(view)

    assert "P2+ Sample Diagnostic Package" in html
    assert "User Assertions" in html
    assert "Verification Workbench" in html
    assert "Before / After Comparison" in html
    assert "Redaction" in html
    assert "AI Handoff Blocks" in html
    assert "assertion-1" in html
    assert "test-1" in html


def test_p2plus_sample_fixture_has_review_summary() -> None:
    package_dir = Path("tests/fixtures/p2plus_sample_package")
    view = read_package_view(package_dir)

    summaries = build_evidence_reference_summaries(view)
    reasons = verification_status_reasons(view)

    assert "evidence/logs/app.log" in summaries
    assert summaries["evidence/logs/app.log"].timeline_refs
    assert summaries["evidence/logs/app.log"].test_record_refs
    assert reasons
