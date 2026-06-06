from doctor_link.diagnose_now import diagnose_now


def test_diagnose_now_writes_summary(tmp_path):
    summary = diagnose_now(tmp_path)
    assert summary.name == "summary.md"
    assert summary.exists()
