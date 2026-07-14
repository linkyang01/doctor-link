from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from doctor_link.core.models import utc_now_iso
from doctor_link.core.package_transaction import atomic_write_json, atomic_write_text
from doctor_link.core.solve import SolveResult, solve_project


BENCHMARK_SCHEMA = "doctor-link-benchmark-v1"
BENCHMARK_RESULT_SCHEMA = "doctor-link-benchmark-result-v1"


@dataclass
class BenchmarkScenarioResult:
    scenario_id: str
    status: str
    expected_status: str | None
    matched_expectation: bool
    project_root: str
    package: str | None
    duration_seconds: float
    solve_session: str | None
    rounds: int
    reproduced: bool
    blockers: list[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    schema: str
    manifest: str
    started_at: str
    completed_at: str
    status: str
    allow_repair: bool
    total: int
    reproduced: int
    verified: int
    blocked: int
    not_reproduced: int
    failed: int
    expectation_matches: int
    reproduction_rate: float
    repair_success_rate: float | None
    mean_rounds: float
    mean_duration_seconds: float
    scenarios: list[dict[str, Any]]
    output_dir: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_benchmark(
    manifest_path: Path,
    *,
    output_dir: Path,
    allow_repair: bool = False,
    solve_runner: Callable[..., SolveResult] = solve_project,
) -> BenchmarkResult:
    manifest = manifest_path.expanduser().resolve()
    payload = _load_manifest(manifest)
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Benchmark manifest must contain at least one scenario.")
    _validate_scenarios(scenarios)
    output = output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    started_at = utc_now_iso()
    records: list[BenchmarkScenarioResult] = []
    for index, scenario in enumerate(scenarios, start=1):
        assert isinstance(scenario, dict)
        scenario_id = str(scenario.get("id") or f"scenario-{index}")
        raw_root = scenario.get("project_root")
        problem = str(scenario.get("problem") or "").strip()
        project_root = Path(str(raw_root)).expanduser()
        if not project_root.is_absolute():
            project_root = (manifest.parent / project_root).resolve()
        scenario_output = output / "sessions" / scenario_id
        started = time.monotonic()
        try:
            max_rounds = int(scenario.get("max_rounds", 3))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Benchmark scenario {scenario_id!r} has an invalid max_rounds value.") from exc
        if not 1 <= max_rounds <= 3:
            raise ValueError(f"Benchmark scenario {scenario_id!r} max_rounds must be between 1 and 3.")
        result = solve_runner(
            project_root,
            problem=problem,
            reproduce_command=_optional_text(scenario.get("reproduce_command")),
            test_command=_optional_text(scenario.get("test_command")),
            package=_optional_text(scenario.get("package")),
            output_root=scenario_output,
            allow_repair=allow_repair,
            max_rounds=max_rounds,
        )
        expected = _optional_text(scenario.get("expected_status"))
        records.append(
            BenchmarkScenarioResult(
                scenario_id=scenario_id,
                status=result.status,
                expected_status=expected,
                matched_expectation=expected is None or result.status == expected,
                project_root=str(project_root),
                package=_optional_text(scenario.get("package")),
                duration_seconds=round(time.monotonic() - started, 6),
                solve_session=result.output_dir,
                rounds=len(result.rounds),
                reproduced=_was_reproduced(result),
                blockers=list(result.blockers),
            )
        )
    benchmark = _summarize(manifest, output, started_at, allow_repair, records)
    atomic_write_json(output / "benchmark-result.json", benchmark.to_dict())
    atomic_write_text(output / "benchmark-result.md", _benchmark_markdown(benchmark))
    return benchmark


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Benchmark manifest could not be read: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != BENCHMARK_SCHEMA:
        raise ValueError(f"Benchmark manifest schema must be {BENCHMARK_SCHEMA!r}.")
    return payload


def _validate_scenarios(scenarios: list[object]) -> None:
    scenario_ids: set[str] = set()
    for index, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, dict):
            raise ValueError(f"Benchmark scenario {index} must be an object.")
        scenario_id = str(scenario.get("id") or f"scenario-{index}")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", scenario_id):
            raise ValueError(
                f"Benchmark scenario id {scenario_id!r} must use 1-80 letters, numbers, dots, underscores, or hyphens."
            )
        if scenario_id in scenario_ids:
            raise ValueError(f"Benchmark scenario id {scenario_id!r} is duplicated.")
        scenario_ids.add(scenario_id)
        if not scenario.get("project_root") or not str(scenario.get("problem") or "").strip():
            raise ValueError(f"Benchmark scenario {scenario_id!r} requires project_root and problem.")
        try:
            max_rounds = int(scenario.get("max_rounds", 3))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Benchmark scenario {scenario_id!r} has an invalid max_rounds value.") from exc
        if not 1 <= max_rounds <= 3:
            raise ValueError(f"Benchmark scenario {scenario_id!r} max_rounds must be between 1 and 3.")


def _summarize(
    manifest: Path,
    output: Path,
    started_at: str,
    allow_repair: bool,
    records: list[BenchmarkScenarioResult],
) -> BenchmarkResult:
    total = len(records)
    reproduced = sum(item.reproduced for item in records)
    verified = sum(item.status == "verified" for item in records)
    attempted = sum(item.rounds > 0 for item in records)
    expectation_matches = sum(item.matched_expectation for item in records)
    return BenchmarkResult(
        schema=BENCHMARK_RESULT_SCHEMA,
        manifest=str(manifest),
        started_at=started_at,
        completed_at=utc_now_iso(),
        status="passed" if expectation_matches == total else "failed",
        allow_repair=allow_repair,
        total=total,
        reproduced=reproduced,
        verified=verified,
        blocked=sum(item.status == "blocked" for item in records),
        not_reproduced=sum(item.status == "not_reproduced" for item in records),
        failed=sum(item.status == "failed" for item in records),
        expectation_matches=expectation_matches,
        reproduction_rate=round(reproduced / total, 4),
        repair_success_rate=round(verified / attempted, 4) if attempted else None,
        mean_rounds=round(sum(item.rounds for item in records) / total, 4),
        mean_duration_seconds=round(sum(item.duration_seconds for item in records) / total, 4),
        scenarios=[asdict(item) for item in records],
        output_dir=str(output),
    )


def _benchmark_markdown(result: BenchmarkResult) -> str:
    repair_rate = "N/A" if result.repair_success_rate is None else f"{result.repair_success_rate:.2%}"
    lines = [
        "# Doctor link Benchmark Result",
        "",
        f"- Status: `{result.status}`",
        f"- Scenarios: `{result.total}`",
        f"- Reproduction rate: `{result.reproduction_rate:.2%}`",
        f"- Repair success rate: `{repair_rate}`",
        f"- Mean rounds: `{result.mean_rounds}`",
        f"- Mean duration: `{result.mean_duration_seconds}s`",
        "",
        "## Scenarios",
        "",
    ]
    lines.extend(
        f"- `{item['scenario_id']}`: `{item['status']}`; expected "
        f"`{item['expected_status'] or 'any'}`; matched `{str(item['matched_expectation']).lower()}`"
        for item in result.scenarios
    )
    return "\n".join(lines) + "\n"


def _optional_text(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _was_reproduced(result: SolveResult) -> bool:
    required_ids = {str(item.get("command_id")) for item in result.commands if item.get("required", True)}
    return any(
        str(item.get("command_id")) in required_ids and item.get("status") not in {"passed", "skipped"}
        for item in result.baseline
    )
