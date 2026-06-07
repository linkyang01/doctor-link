from doctor_link.diagnose_now import diagnose_now


def test_output_dir(tmp_path):
    out = tmp_path / "r"
    summary = diagnose_now(tmp_path, out)
    assert summary == out / "summary.md"
    assert summary.exists()
