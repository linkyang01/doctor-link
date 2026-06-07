from doctor_link.diagnose_now import diagnose_now


def test_diagnose_now_repeat(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    diagnose_now(tmp_path)
    out = diagnose_now(tmp_path)
    text = out.read_text(encoding="utf-8")
    assert out.name == "summary.md"
    assert "Files: 1" in text
    assert "## Recommendations" in text
