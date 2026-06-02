from __future__ import annotations

import json
import zipfile
from pathlib import Path

from click.testing import CliRunner

from doctor_link.core.knowledge_archive import (
    append_archive_audit,
    build_knowledge_index,
    check_archive_policy,
    create_archive,
    export_archive,
    export_knowledge,
    inspect_archive,
    query_knowledge,
    write_knowledge_index,
)
from doctor_link.entrypoint import main


def _write_report(root: Path, name: str, payload: dict[str, object]) -> Path:
    package = root / name
    package.mkdir(parents=True)
    path = package / "doctor-report.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_knowledge_index_extracts_failures_and_outcomes(tmp_path: Path) -> None:
    _write_report(tmp_path, "pkg-a", {"project": "demo", "status": "failed", "summary": "missing evidence error"})
    _write_report(tmp_path, "pkg-b", {"project": "demo", "status": "failed", "summary": "missing evidence error"})
    _write_report(tmp_path, "pkg-c", {"project": "demo", "status": "passed", "summary": "fixed"})

    index = build_knowledge_index(tmp_path)

    assert len(index.records) == 3
    assert any(item["signature"] == "missing" for item in index.recurring_failures)
    assert index.repair_outcomes["passed"] == 1
    assert index.repair_outcomes["blocked"] == 2
    assert index.health_trend["average_score"] >= 0


def test_write_query_and_export_knowledge(tmp_path: Path) -> None:
    _write_report(tmp_path, "pkg-a", {"project": "alpha", "status": "failed", "summary": "database error"})
    index_path = tmp_path / "knowledge-index.json"
    export_path = tmp_path / "knowledge-export.json"

    write_knowledge_index(tmp_path, index_path)
    result = query_knowledge(index_path, "database")
    exported = export_knowledge(index_path, export_path)

    assert result.matched_count == 1
    assert result.records[0]["project"] == "alpha"
    assert export_path.exists()
    assert exported.records


def test_create_inspect_policy_and_export_archive(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    (source / "b.txt").write_text("b", encoding="utf-8")
    archive = tmp_path / "archive"

    record = create_archive(source, archive, {"owner": "test"})
    inspected = inspect_archive(archive)
    policy_ok = check_archive_policy(archive, max_files=5)
    policy_blocked = check_archive_policy(archive, max_files=1)
    exported = export_archive(archive, tmp_path / "archive.zip")

    assert record.schema == "doctor-link-archive-v1"
    assert len(inspected.files) == 2
    assert policy_ok.status == "passed"
    assert policy_blocked.status == "blocked"
    assert exported.exists()
    with zipfile.ZipFile(exported) as archive_zip:
        assert "archive-record.json" in archive_zip.namelist()


def test_create_archive_blocks_archive_inside_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")

    try:
        create_archive(source, source / "archive")
    except ValueError as exc:
        assert "archive_root" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected archive_root inside source_root to be blocked")


def test_create_archive_blocks_archive_equal_to_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")

    try:
        create_archive(source, source)
    except ValueError as exc:
        assert "archive_root" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected archive_root equal to source_root to be blocked")


def test_append_archive_audit(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()

    audit = append_archive_audit(archive, "manual-event", {"x": 1})

    assert audit["event"] == "manual-event"
    audit_file = archive / "archive-audit.jsonl"
    assert audit_file.exists()
    assert "manual-event" in audit_file.read_text(encoding="utf-8")


def test_knowledge_and_archive_cli_commands(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    _write_report(reports, "pkg-a", {"project": "cli", "status": "failed", "summary": "missing cli evidence"})
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    runner = CliRunner()
    index_path = tmp_path / "knowledge-index.json"
    archive_root = tmp_path / "archive"

    build_result = runner.invoke(main, ["knowledge", "build", str(reports), "--out", str(index_path), "--json"])
    query_result = runner.invoke(main, ["knowledge", "query", str(index_path), "missing", "--json"])
    export_result = runner.invoke(main, ["knowledge", "export", str(index_path), str(tmp_path / "knowledge-export.json"), "--json"])
    archive_create = runner.invoke(main, ["archive", "create", str(source), str(archive_root), "--json"])
    archive_inspect = runner.invoke(main, ["archive", "inspect", str(archive_root), "--json"])
    archive_policy = runner.invoke(main, ["archive", "policy-check", str(archive_root), "--max-files", "5", "--json"])

    assert build_result.exit_code == 0
    assert query_result.exit_code == 0
    assert export_result.exit_code == 0
    assert archive_create.exit_code == 0
    assert archive_inspect.exit_code == 0
    assert archive_policy.exit_code == 0
    assert '"matched_count": 1' in query_result.output
    assert '"status": "passed"' in archive_policy.output


def test_archive_create_cli_blocks_archive_inside_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(main, ["archive", "create", str(source), str(source / "archive"), "--json"])

    assert result.exit_code != 0
    assert "archive_root" in result.output
