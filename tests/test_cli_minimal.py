from click.testing import CliRunner

from doctor_link.entrypoint import main


def test_command_runs(tmp_path):
    r = CliRunner().invoke(main, ["diagnose-now", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "summary.md" in r.output


def test_json(tmp_path):
    r = CliRunner().invoke(main, ["diagnose-now", "--json", str(tmp_path)])
    assert r.exit_code == 0


def test_output(tmp_path):
    out = tmp_path / "r"
    r = Cli