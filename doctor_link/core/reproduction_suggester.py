from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.command_runner import run_command
from doctor_link.core.reproduction import load_reproduction_catalog
from doctor_link.core.safe_command_runner import run_safe_command_sequence
from doctor_link.core.test_matrix_runner import load_test_matrix


SUGGESTION_SCHEMA = "doctor-link-reproduction-suggestions-v1"
TEST_SUFFIXES = {".cjs", ".js", ".mjs", ".py", ".ts", ".tsx"}
TOKEN_ALIASES = {
    "auth": {"auth", "authorization", "login", "permission", "session"},
    "cache": {"cache", "redis", "stale"},
    "checkout": {"billing", "charge", "checkout", "order", "payment"},
    "concurrency": {"concurrent", "concurrency", "lock", "race", "thread"},
    "data": {"database", "db", "persist", "storage", "transaction"},
    "unicode": {"encoding", "i18n", "text", "unicode", "utf"},
}
STOP_WORDS = {
    "a", "an", "and", "are", "does", "for", "from", "in", "is", "it", "of", "on", "or", "the", "this", "to", "when", "with",
}


@dataclass
class ReproductionSuggestion:
    suggestion_id: str
    command: str
    scope: str
    rationale: str
    confidence: float
    matched_terms: list[str] = field(default_factory=list)
    status: str = "proposed"
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReproductionSuggestionResult:
    schema: str
    project_root: str
    problem: str
    project_type: str
    status: str
    selected_command: str | None
    suggestions: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def suggest_reproductions(
    project_root: Path,
    problem: str,
    *,
    validate: bool = False,
    timeout_seconds: int = 120,
    max_candidates: int = 5,
) -> ReproductionSuggestionResult:
    root = project_root.expanduser().resolve()
    clean_problem = problem.strip()
    if not root.is_dir():
        return _result(root, clean_problem, "unsupported", "blocked", [], ["Project root does not exist."])
    if not clean_problem:
        return _result(root, clean_problem, "unsupported", "blocked", [], ["A problem description is required."])
    project_type = _project_type(root)
    if project_type == "unsupported":
        return _result(root, clean_problem, project_type, "blocked", [], ["No supported Python or JavaScript project was detected."])

    terms = _problem_terms(clean_problem)
    suggestions = _candidate_commands(root, project_type, terms)[: max(1, min(max_candidates, 10))]
    if not suggestions:
        return _result(root, clean_problem, project_type, "blocked", [], ["No safe test entrypoint was discovered."])
    if validate:
        original_git_status = _git_status(root)
        for item in suggestions:
            completed = run_safe_command_sequence(item.command, cwd=root, timeout_seconds=timeout_seconds)
            item.return_code = completed.returncode
            item.stdout = completed.stdout
            item.stderr = completed.stderr
            if completed.timed_out:
                item.status = "timed_out"
            elif completed.returncode == 0:
                item.status = "passed"
            elif completed.returncode == 127:
                item.status = "unavailable"
            else:
                item.status = "reproduced"
            current_git_status = _git_status(root)
            if original_git_status is not None and current_git_status != original_git_status:
                item.status = "modified_worktree"
                item.stderr = (item.stderr + "\nCandidate check changed the Git working tree.").strip()
                break
    selected = next((item.command for item in suggestions if item.status == "reproduced"), None)
    if not validate:
        status = "proposed"
    elif selected:
        status = "reproduced"
    elif any(item.status == "passed" for item in suggestions):
        status = "not_reproduced"
    else:
        status = "blocked"
    return _result(root, clean_problem, project_type, status, suggestions, [], selected)


def _candidate_commands(root: Path, project_type: str, terms: set[str]) -> list[ReproductionSuggestion]:
    candidates = _configured_candidates(root, terms)
    ranked_files = _rank_test_files(root, terms)
    for index, (score, path, matches) in enumerate(ranked_files[:3], start=1):
        if not matches:
            continue
        relative = path.relative_to(root).as_posix()
        if project_type == "python" and path.suffix == ".py":
            command = f"PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider {relative} -q"
        elif path.suffix in {".cjs", ".js", ".mjs"}:
            command = f"node --test {relative}"
        else:
            continue
        candidates.append(
            ReproductionSuggestion(
                suggestion_id=f"focused-{index}",
                command=command,
                scope=relative,
                rationale="Test path matches terms from the reported problem.",
                confidence=round(min(0.95, 0.55 + score * 0.08), 2),
                matched_terms=matches,
            )
        )
    broad = _broad_test_command(root, project_type)
    if broad and all(item.command != broad for item in candidates):
        candidates.append(
            ReproductionSuggestion(
                suggestion_id="project-test-suite",
                command=broad,
                scope="project",
                rationale="Project metadata declares a safe test entrypoint.",
                confidence=0.6,
            )
        )
    return candidates


def _configured_candidates(root: Path, terms: set[str]) -> list[ReproductionSuggestion]:
    entries: list[tuple[str, str, str]] = []
    catalog = load_reproduction_catalog(root)
    for item in catalog.entries:
        if item.kind != "manual" and item.command:
            searchable = " ".join(
                [item.reproduction_id, item.title, item.description, *item.related_assertion_statements]
            ).casefold()
            entries.append((f"catalog-{item.reproduction_id}", item.command, searchable))
    matrix = load_test_matrix(root)
    for item in matrix.jobs:
        searchable = " ".join([item.job_id, item.title, *item.related_assertion_statements]).casefold()
        entries.append((f"matrix-{item.job_id}", item.command, searchable))
    ranked: list[tuple[int, ReproductionSuggestion]] = []
    for suggestion_id, command, searchable in entries:
        if re.search(r"(^|\s)python(?:3(?:\.\d+)?)?(?:\s|$)", command) and "PYTHONDONTWRITEBYTECODE=" not in command:
            command = f"PYTHONDONTWRITEBYTECODE=1 {command}"
        matches = sorted(term for term in terms if term in searchable)
        score = len(matches)
        ranked.append(
            (
                score,
                ReproductionSuggestion(
                    suggestion_id=suggestion_id,
                    command=command,
                    scope="configured",
                    rationale="A project-owned reproduction or test entry matches the reported problem."
                    if matches
                    else "A project-owned reproduction or test entry is available.",
                    confidence=round(0.55 + min(score, 4) * 0.1, 2),
                    matched_terms=matches,
                ),
            )
        )
    return [item for _, item in sorted(ranked, key=lambda pair: (-pair[0], pair[1].suggestion_id))]


def _rank_test_files(root: Path, terms: set[str]) -> list[tuple[int, Path, list[str]]]:
    ranked: list[tuple[int, Path, list[str]]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEST_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if any(part in {".git", ".venv", "dist", "node_modules", "vendor"} for part in relative.parts):
            continue
        name = relative.as_posix().casefold()
        if not _looks_like_test(name):
            continue
        matches = sorted(term for term in terms if term in name)
        score = len(matches) * 3 + (2 if "test" in path.name.casefold() else 0)
        ranked.append((score, path, matches))
    return sorted(ranked, key=lambda item: (-item[0], len(item[1].parts), item[1].as_posix()))


def _problem_terms(problem: str) -> set[str]:
    raw = {token for token in re.findall(r"[a-z0-9]+", problem.casefold()) if len(token) >= 3 and token not in STOP_WORDS}
    expanded = set(raw)
    for aliases in TOKEN_ALIASES.values():
        if raw & aliases:
            expanded.update(aliases)
    return expanded


def _looks_like_test(path: str) -> bool:
    return any(marker in path for marker in ("/test/", "/tests/", ".spec.", ".test.", "test_"))


def _project_type(root: Path) -> str:
    if any((root / name).is_file() for name in ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt")):
        return "python"
    if (root / "package.json").is_file():
        return "javascript"
    if any(root.glob("*.py")) or any(
        directory.is_dir() and next(directory.rglob("*.py"), None) is not None
        for directory in (root / "src", root / "app", root / "tests")
    ):
        return "python"
    if any(
        path.suffix.lower() in {".cjs", ".js", ".jsx", ".mjs", ".ts", ".tsx"}
        for directory in (root, root / "src", root / "app", root / "lib")
        if directory.is_dir()
        for path in directory.rglob("*")
        if path.is_file() and "node_modules" not in path.parts
    ):
        return "javascript"
    return "unsupported"


def _broad_test_command(root: Path, project_type: str) -> str | None:
    if project_type == "python" and (root / "tests").is_dir():
        return "PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q"
    package_path = root / "package.json"
    if project_type == "javascript" and package_path.is_file():
        try:
            payload = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        scripts = payload.get("scripts") if isinstance(payload, dict) else None
        test_script = scripts.get("test") if isinstance(scripts, dict) else None
        if isinstance(test_script, str) and test_script.strip() and "no test specified" not in test_script.casefold():
            manager = str(payload.get("packageManager") or "npm").partition("@")[0]
            if manager not in {"bun", "npm", "pnpm", "yarn"}:
                manager = "npm"
            return {"bun": "bun run test", "npm": "npm test", "pnpm": "pnpm test", "yarn": "yarn test"}[manager]
    return None


def _result(
    root: Path,
    problem: str,
    project_type: str,
    status: str,
    suggestions: list[ReproductionSuggestion],
    warnings: list[str],
    selected: str | None = None,
) -> ReproductionSuggestionResult:
    return ReproductionSuggestionResult(
        schema=SUGGESTION_SCHEMA,
        project_root=str(root),
        problem=problem,
        project_type=project_type,
        status=status,
        selected_command=selected,
        suggestions=[item.to_dict() for item in suggestions],
        warnings=warnings,
    )


def _git_status(root: Path) -> str | None:
    completed = run_command(["git", "status", "--porcelain"], cwd=root, timeout_seconds=15)
    return completed.stdout if completed.returncode == 0 else None
