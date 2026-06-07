from __future__ import annotations

import json

from click.testing import CliRunner

from doctor_link.entrypoint import main


def test_command_runs(tmp_path):
    result = CliRunner().invoke(main, ["diagnose-now", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "summary.md" in result.output


def test_command_json_output(tmp_path):