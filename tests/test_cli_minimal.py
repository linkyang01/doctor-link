from __future__ import annotations

from click.testing import CliRunner

from doctor_link.entrypoint import main


def test_command_runs() -> None:
    result = CliRunner().invoke(main, ["diagnose-now"])
    assert result.exit_code == 0, result.output
