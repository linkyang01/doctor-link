from pathlib import Path

from doctor_link.diagnose_report import build_report


def test_build_report_counts_extensions():
    files = [Path("a.txt"), Path("b.md"), Path("c.txt"), Path("README")]
    report = build_report(files)
    assert report["files"] == 4
    assert report["extensions"] == {"md": 1, "none": 1, "txt": 2}
    assert report["recommendations"]
    assert any("doctor-link report" in item for item in report["recommendations"])