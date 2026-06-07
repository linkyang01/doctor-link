from click.testing import CliRunner

from doctor_link.diagnose_now import diagnose_now
from doctor_link.entrypoint import main


def test_command_runs(tmp_path):
    r = CliRunner().invoke(main, ["diagnose-now", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "summary.md" in r.output


def test_json(tmp_path):
    r = CliRunner().invoke(main, ["diagn