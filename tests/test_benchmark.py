from __future__ import annotations

import json
from pathlib import Path

import pytest

from doctor_link.core.benchmark import run_benchmark
from doctor_link.core.solve import SOLVE_SCHEMA, SolveResult


def _manifest(tmp_path: Path, scenarios: list[dict[str, object]]) -> Path:
    path = tmp_path / "benchmark.yml"
    path.write_text(
        "schema: doctor-link-benchmark-v1\nscenarios:\n" + "".join(
            f"  - id: {item['id']}\n"
            f"    project_root: {item.get('project_root', '.')}\n"
            f"    problem: {item.get('problem', 'broken')}\n"
            f"    expected_status: {item.get('expected_status', 'approval_required')}\n"
            for item in scenarios
        ),
        encoding="utf-8",
    )
    return path


def _result(status: str, project_root: Path) -> SolveResult:
    return SolveResult(
        schema=SOLVE_SCHEMA,
        session_id="fixture",
        project_root=str(project_root),
        workspace_root=str(project_root),
        package_path=None,
        problem="broken",
        project_type="python",
        tool="codex",
        status=status,
        commands=[{"command_id": "test", "required": True}],
        baseline=[{"command_id": "test", "status": "failed"}],
        rounds=[{"round_number": 1}] if status == "verified" else [],
        output_dir=str(project_root / "session"),
    )


def test_benchmark_reports_reproduction_repair_and_expectation_metrics(tmp_path: Path) -> None:
    manifest = _manifest(
        tmp_path,
        [
            {"id": "preview", "expected_status": "approval_required"},
            {"id": "repaired", "expected_status": "verified"},
        ],
    )

    def runner(project_root: Path, **kwargs) -> SolveResult:
        return _result("verified" if Path(kwargs["output_root"]).name == "repaired" else "approval_required", project_root)

    result = run_benchmark(manifest, output_dir=tmp_path / "out", solve_runner=runner)

    assert result.status == "passed"
    assert result.reproduction_rate == 1.0
    assert result.repair_success_rate == 1.0
    assert result.expectation_matches == 2
    assert result.scenarios[0]["reproduction_command"] is None
    assert json.loads((tmp_path / "out" / "benchmark-result.json").read_text())["total"] == 2
    assert (tmp_path / "out" / "benchmark-result.md").is_file()


def test_benchmark_fails_when_observed_status_differs(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, [{"id": "mismatch", "expected_status": "verified"}])

    result = run_benchmark(
        manifest,
        output_dir=tmp_path / "out",
        solve_runner=lambda project_root, **kwargs: _result("approval_required", project_root),
    )

    assert result.status == "failed"
    assert result.expectation_matches == 0


def test_benchmark_rejects_unsafe_scenario_id(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, [{"id": "../escape"}])

    with pytest.raises(ValueError, match="scenario id"):
        run_benchmark(manifest, output_dir=tmp_path / "out", solve_runner=lambda *args, **kwargs: None)


def test_benchmark_rejects_duplicate_scenario_ids(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path, [{"id": "same"}, {"id": "same"}])

    with pytest.raises(ValueError, match="duplicated"):
        run_benchmark(
            manifest,
            output_dir=tmp_path / "out",
            solve_runner=lambda project_root, **kwargs: _result("approval_required", project_root),
        )
