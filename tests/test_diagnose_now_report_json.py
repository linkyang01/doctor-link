import json

from click.testing import CliRunner

from doctor_link.entrypoint import main


def test_report_json_output(tmp_path):
    sample = tmp_path / "a.txt"
    sample.write_text("hello", encoding="utf-8")
    out = tmp_path / "report"

    result = CliRunner().invoke(
        main,
        ["diagnose-now", str(tmp_path), "--output", str(out), "--report-json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["summary"].endswith("summary.md")
    assert payload["report"]["files"] == 1
    assert payload["report"]["extensions"] == {"txt": 1}
    assert payload["report"]["recommendations"]
    assert (out / "summary.md").exists()


def test_existing_json_output_stays_summary_only(tmp_path):
    sample = tmp_path / "a.txt"
    sample.write_text("hello", encoding="utf-8")

    result = CliRunner().invoke(main, ["diagnose-now", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.output
    assert set(json.loads(result.output)) == {"summary"}