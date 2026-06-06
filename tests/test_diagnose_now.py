from doctor_link.diagnose_now import diagnose_now


def test_diagnose_now_writes_file_count(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    summary = diagnose_now(tmp_path)
    text = summary.read_text(encoding="utf-8")
    assert summary.name == "summary.md"
    assert "Files: 2" in text
    assert "## Extensions" in text
