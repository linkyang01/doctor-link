from click.testing import CliRunner

from doctor_link.entrypoint import main


def test_json_output_path(tmp_path):
    out = tmp_path / "report"
    r = CliRunner().invoke(
        main,
        ["diagnose-now", str(tmp_path), "--output", str(out), "--json"],
    )
    assert r.exit_code == 0, r.output
    assert "summary" in r.output
    assert "summary.md" in r.output
    assert (out / "summary.md").exists()
