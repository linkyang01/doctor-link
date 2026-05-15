from __future__ import annotations

from pathlib import Path

from doctor_link.core.web_detail_renderer import render_package_detail_html
from doctor_link.core.web_package_reader import read_package_view


FIXTURE = Path("tests/fixtures/p2plus_sample_package")


def test_p2plus_workbench_has_basic_accessibility_structure() -> None:
    html = render_package_detail_html(read_package_view(FIXTURE))

    assert "<!doctype html>" in html
    assert '<html lang="en">' in html
    assert 'name="viewport"' in html
    assert "<nav>" in html
    assert 'href="#overview"' in html
    assert 'href="#evidence"' in html
    assert 'href="#verification"' in html
    assert "Back to index" in html
    assert "<h1>Doctor link Diagnostic Package Workbench</h1>" in html
