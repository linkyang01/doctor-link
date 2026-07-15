"""Advisory root-cause hints derived from failing check output.

Hints are heuristic and never authoritative. They narrow inspection for humans
and repair tools without changing the independent verification contract.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from doctor_link.core.command_runner import run_command


EXPLAIN_SCHEMA = "doctor-link-root-cause-hints-v2"
TRACEBACK_FRAME = re.compile(
    r'File "(?P<path>[^"]+)", line (?P<line>\d+)(?:, in (?P<function>[\w.<>-]+))?'
)
PYTEST_NODE = re.compile(r"(?P<path>[\w./\\-]+\.py)::(?P<node>[\w\[\]-]+)")
SYMBOL_TOKEN = re.compile(r"\b([A-Z][A-Za-z0-9_]{2,}|[a-z_][a-z0-9_]{2,}\.[A-Za-z_][A-Za-z0-9_]*)\b")
ASSERT_LINE = re.compile(r"(?m)^E\s+assert\s+.+$|^>\s+assert\s+.+$|AssertionError:.*$")
JS_FRAME = re.compile(
    r"(?:file://)?(?P<path>[\w./\\-]+\.(?:cjs|js|jsx|mjs|ts|tsx)):(?P<line>\d+)(?::(?P<column>\d+))?"
)
JS_NAMED_FRAME = re.compile(
    r"at\s+(?P<function>[\w.$<>-]+)\s+\((?:file://)?(?P<path>[^():\s]+\.(?:cjs|js|jsx|mjs|ts|tsx)):(?P<line>\d+)(?::(?P<column>\d+))?\)"
)
PYTEST_VALUE = re.compile(r"(?m)^E\s+assert\s+(?P<actual>.+?)\s+==\s+(?P<expected>.+?)\s*$")
EXPECTED_ACTUAL = (
    re.compile(r"(?i)expected\s*[:=]?\s*(?P<expected>.+?)\s*(?:,|\n|\s+)\s*(?:but\s+)?(?:got|received|actual)\s*[:=]?\s*(?P<actual>.+?)(?:\n|$)"),
    re.compile(r"(?is)Expected:\s*(?P<expected>.+?)\n(?:Received|Actual):\s*(?P<actual>.+?)(?:\n\n|\Z)"),
)
IGNORED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
}
STOP_SYMBOLS = {
    "AssertionError",
    "Error",
    "Exception",
    "Failed",
    "None",
    "Path",
    "True",
    "TypeError",
    "ValueError",
    "Difference",
    "TODO",
    "Unexpected",
    "assert",
    "false",
    "self",
    "true",
    "undefined",
}


@dataclass
class TraceFrame:
    path: str
    line: int | None = None
    function: str | None = None
    in_tests: bool = False
    project_code: bool = False
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RootCauseHint:
    symbol: str
    confidence: float
    evidence_count: int
    candidate_paths: list[str] = field(default_factory=list)
    locations: list[dict[str, Any]] = field(default_factory=list)
    score: int = 0
    evidence: list[str] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RootCauseAnalysis:
    schema: str
    project_root: str
    problem: str
    status: str
    summary: str
    advisory: bool = True
    failure_count: int = 0
    shared_symbols: list[str] = field(default_factory=list)
    failure_patterns: list[str] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    frames: list[dict[str, Any]] = field(default_factory=list)
    hints: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def prompt_section(self) -> str:
        """Render an advisory section for repair prompts."""
        if self.status not in {"explained", "partial"} or not self.hints:
            return ""
        lines = [
            "## Suspected root cause (advisory only)",
            "",
            f"{self.summary}",
            "",
            "These hints are heuristic. Verify against the failing evidence before editing.",
            "",
        ]
        for index, hint in enumerate(self.hints[:5], start=1):
            paths = ", ".join(f"`{path}`" for path in hint.get("candidate_paths", [])[:4]) or "no local path mapped"
            lines.append(
                f"{index}. **{hint.get('symbol', 'unknown')}** "
                f"(confidence {hint.get('confidence', 0):.2f}, evidence {hint.get('evidence_count', 0)}): "
                f"{hint.get('rationale', '')} Inspect: {paths}."
            )
            for location in hint.get("locations", [])[:2]:
                lines.append(
                    f"   - Location: `{location.get('path')}:{location.get('line') or '?'}` "
                    f"in `{location.get('function') or 'unknown'}`."
                )
            for evidence in hint.get("evidence", [])[:4]:
                lines.append(f"   - Evidence: {evidence}")
        if self.failure_patterns:
            lines.extend(["", "Observed failure patterns:", *[f"- {item}" for item in self.failure_patterns[:5]]])
        lines.append("")
        return "\n".join(lines)


def analyze_root_cause(
    project_root: Path,
    *,
    problem: str,
    checks: Sequence[Mapping[str, Any]] | None = None,
    outputs: Sequence[tuple[str, str]] | None = None,
) -> RootCauseAnalysis:
    """Build advisory root-cause hints from failing check outputs."""
    root = project_root.expanduser().resolve()
    clean_problem = problem.strip()
    failing_outputs = _collect_failing_outputs(checks=checks, outputs=outputs)
    if not failing_outputs:
        return RootCauseAnalysis(
            schema=EXPLAIN_SCHEMA,
            project_root=str(root),
            problem=clean_problem,
            status="no_failures",
            summary="No failing check output was available for root-cause analysis.",
            failure_count=0,
        )

    frames: list[TraceFrame] = []
    failures: list[dict[str, Any]] = []
    symbols: Counter[str] = Counter()
    patterns: Counter[str] = Counter()
    for stdout, stderr in failing_outputs:
        text = f"{stdout}\n{stderr}"
        output_frames = _extract_frames(text, root)
        frames.extend(output_frames)
        failures.append(_extract_failure_detail(text, output_frames))
        for symbol in _extract_symbols(text):
            symbols[symbol] += 1
        for pattern in _extract_patterns(text):
            patterns[pattern] += 1

    # Prefer symbols that appear across multiple failures.
    shared = [name for name, count in symbols.most_common() if count >= min(2, len(failing_outputs))]
    if not shared:
        shared = [name for name, _ in symbols.most_common(8)]

    production_frames = [frame for frame in frames if not frame.in_tests]
    test_frames = [frame for frame in frames if frame.in_tests]
    path_hits = Counter(frame.path for frame in production_frames if frame.path)
    hints: list[RootCauseHint] = []

    changed_source_paths = _git_changed_source_paths(root)
    for path in changed_source_paths[:5]:
        locations = _locations_for_path(root, path, frames)
        evidence = ["production file differs from Git HEAD"]
        score = 40
        if locations:
            evidence.append("failure stack references this production file")
            score += 35
        hints.append(
            RootCauseHint(
                symbol=Path(path).stem,
                confidence=0.9,
                evidence_count=1,
                candidate_paths=[path],
                locations=locations,
                score=score,
                evidence=evidence,
                rationale=(
                    "This production file differs from the current Git base and is a strong inspection candidate; "
                    "the change may still be unrelated."
                ),
            )
        )

    for symbol in shared[:8]:
        mapped = _map_symbol_to_sources(root, symbol)
        evidence = symbols[symbol]
        confidence = min(0.95, 0.35 + 0.12 * evidence + (0.15 if mapped else 0.0))
        if mapped:
            rationale = f"Appears in {evidence} failing output(s) and maps to project source."
        else:
            rationale = f"Appears in {evidence} failing output(s); inspect call sites referencing this symbol."
        hints.append(
            RootCauseHint(
                symbol=symbol,
                confidence=round(confidence, 2),
                evidence_count=evidence,
                candidate_paths=mapped[:5],
                locations=_locations_for_paths(root, mapped[:5], frames),
                score=min(100, 15 * evidence + (20 if mapped else 0)),
                evidence=[
                    f"symbol appears in {evidence} failing output(s)",
                    *(["symbol maps to project source"] if mapped else []),
                ],
                rationale=rationale,
            )
        )

    # Path-centric hints when frames point at production files repeatedly.
    for path, count in path_hits.most_common(3):
        if any(path in hint.candidate_paths for hint in hints):
            continue
        relative = path
        try:
            relative = Path(path).resolve().relative_to(root).as_posix()
        except ValueError:
            pass
        hints.append(
            RootCauseHint(
                symbol=Path(relative).stem,
                confidence=round(min(0.9, 0.4 + 0.1 * count), 2),
                evidence_count=count,
                candidate_paths=[relative],
                locations=_locations_for_path(root, relative, frames),
                score=min(100, 35 + 10 * count),
                evidence=[f"failure stack references this production path {count} time(s)"],
                rationale=f"Traceback frames hit this production path in {count} failure(s).",
            )
        )

    hints = sorted(
        hints,
        key=lambda item: (
            0 if item.rationale.startswith("This production file differs") else 1,
            0 if item.candidate_paths else 1,
            -item.confidence,
            -item.score,
            -item.evidence_count,
            item.symbol,
        ),
    )[:8]
    if not hints and (production_frames or test_frames):
        top = (production_frames or test_frames)[0]
        relative = top.path
        try:
            relative = Path(top.path).resolve().relative_to(root).as_posix()
        except ValueError:
            pass
        hints.append(
            RootCauseHint(
                symbol=top.function or Path(relative).stem,
                confidence=0.4,
                evidence_count=1,
                candidate_paths=[relative],
                locations=_locations_for_path(root, relative, frames),
                score=30,
                evidence=["only one relevant stack frame was available"],
                rationale="Only a single traceback frame was available; treat as a weak starting point.",
            )
        )

    if hints:
        status = "explained" if any(item.candidate_paths for item in hints) else "partial"
        top = hints[0]
        summary = (
            f"Suspected root cause centers on `{top.symbol}` "
            f"({top.confidence:.0%} confidence across {len(failing_outputs)} failing check(s))."
        )
    else:
        status = "insufficient_evidence"
        summary = "Failing output was present, but no stable symbol or source path could be clustered."

    warnings: list[str] = []
    if all(frame.in_tests for frame in frames) and frames:
        warnings.append("Tracebacks only listed test files; production mapping may be incomplete.")
    warnings.append("Hints are advisory and must not be treated as verified root cause.")

    return RootCauseAnalysis(
        schema=EXPLAIN_SCHEMA,
        project_root=str(root),
        problem=clean_problem,
        status=status,
        summary=summary,
        failure_count=len(failing_outputs),
        shared_symbols=shared[:12],
        failure_patterns=[item for item, _ in patterns.most_common(8)],
        failures=failures,
        frames=[frame.to_dict() for frame in frames[:40]],
        hints=[item.to_dict() for item in hints],
        warnings=warnings,
    )


def _collect_failing_outputs(
    *,
    checks: Sequence[Mapping[str, Any]] | None,
    outputs: Sequence[tuple[str, str]] | None,
) -> list[tuple[str, str]]:
    collected: list[tuple[str, str]] = []
    if outputs:
        for stdout, stderr in outputs:
            if (stdout or "").strip() or (stderr or "").strip():
                collected.append((stdout or "", stderr or ""))
    if checks:
        for check in checks:
            status = str(check.get("status") or "")
            return_code = check.get("return_code")
            if status in {"passed", "timed_out", "unavailable", "proposed"}:
                continue
            if isinstance(return_code, int) and return_code == 0:
                continue
            failed_status = status in {"failed", "reproduced", "setup_failed", "blocked", "modified_worktree"}
            failed_code = isinstance(return_code, int) and return_code not in (0,)
            if not failed_status and not failed_code:
                continue
            stdout = str(check.get("stdout") or "")
            stderr = str(check.get("stderr") or "")
            if stdout.strip() or stderr.strip():
                collected.append((stdout, stderr))
    return collected


def _extract_frames(text: str, root: Path) -> list[TraceFrame]:
    frames: list[TraceFrame] = []
    for match in TRACEBACK_FRAME.finditer(text):
        path = match.group("path")
        function = match.group("function")
        line = int(match.group("line")) if match.group("line") else None
        frames.append(
            TraceFrame(
                path=path,
                line=line,
                function=None if function in {None, "<module>"} else function,
                in_tests=_looks_like_test_path(path),
            )
        )
    named_spans: set[tuple[str, int]] = set()
    for match in JS_NAMED_FRAME.finditer(text):
        path = match.group("path")
        line = int(match.group("line"))
        named_spans.add((path, line))
        frames.append(
            TraceFrame(path=path, line=line, function=match.group("function"), in_tests=_looks_like_test_path(path))
        )
    for match in JS_FRAME.finditer(text):
        path = match.group("path")
        line = int(match.group("line"))
        if (path, line) in named_spans:
            continue
        frames.append(
            TraceFrame(
                path=path,
                line=line,
                function=None,
                in_tests=_looks_like_test_path(path),
            )
        )
    for match in PYTEST_NODE.finditer(text):
        path = match.group("path")
        frames.append(
            TraceFrame(
                path=path,
                line=None,
                function=match.group("node"),
                in_tests=True,
            )
        )
    # Normalize absolute paths under the project root to relative when possible.
    normalized: list[TraceFrame] = []
    for frame in frames:
        path = frame.path
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                path = candidate.resolve().relative_to(root).as_posix()
            except ValueError:
                path = candidate.as_posix()
        else:
            path = path.replace("\\", "/")
            if path.startswith("file://"):
                path = path.removeprefix("file://")
        project_code = not Path(path).is_absolute() and not any(part in IGNORED_PARTS for part in Path(path).parts)
        normalized.append(TraceFrame(
            path=path,
            line=frame.line,
            function=frame.function,
            in_tests=_looks_like_test_path(path),
            project_code=project_code,
            source=_source_line(root, path, frame.line),
        ))
    return normalized


def _extract_failure_detail(text: str, frames: Sequence[TraceFrame]) -> dict[str, Any]:
    expected: str | None = None
    actual: str | None = None
    match = PYTEST_VALUE.search(text)
    if match:
        actual, expected = match.group("actual"), match.group("expected")
    else:
        for pattern in EXPECTED_ACTUAL:
            match = pattern.search(text)
            if match:
                expected, actual = match.group("expected"), match.group("actual")
                break
    exception = None
    for pattern in (r"(?m)^E\s+(?P<kind>[A-Za-z_][\w.]*Error)\b", r"(?m)^(?P<kind>[A-Za-z_][\w.]*Error):"):
        if match := re.search(pattern, text):
            exception = match.group("kind")
            break
    test = None
    if match := PYTEST_NODE.search(text):
        test = f"{match.group('path')}::{match.group('node')}"
    relevant = [frame.to_dict() for frame in frames if frame.project_code]
    return {
        "test": test,
        "exception": exception,
        "expected": _compact_value(expected),
        "actual": _compact_value(actual),
        "frames": relevant[:20],
    }


def _compact_value(value: str | None) -> str | None:
    if value is None:
        return None
    compact = re.sub(r"\s+", " ", value).strip()
    return compact[:500] + ("…" if len(compact) > 500 else "")


def _source_line(root: Path, relative: str, line: int | None) -> str | None:
    if line is None or Path(relative).is_absolute():
        return None
    try:
        lines = (root / relative).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    return lines[line - 1].strip()[:300] if 0 < line <= len(lines) else None


def _locations_for_paths(root: Path, paths: Sequence[str], frames: Sequence[TraceFrame]) -> list[dict[str, Any]]:
    locations: list[dict[str, Any]] = []
    for path in paths:
        locations.extend(_locations_for_path(root, path, frames))
    return locations[:8]


def _locations_for_path(root: Path, path: str, frames: Sequence[TraceFrame]) -> list[dict[str, Any]]:
    matched = [frame.to_dict() for frame in frames if frame.path == path]
    function, line = _changed_function_location(root, path)
    candidates = []
    if line is not None:
        candidates.append({"path": path, "line": line, "function": function, "in_tests": False,
                           "project_code": True, "source": _source_line(root, path, line)})
    candidates.extend(matched)
    if not candidates:
        candidates.append({"path": path, "line": None, "function": None, "in_tests": False,
                           "project_code": True, "source": None})
    unique: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for item in candidates:
        key = (item.get("path"), item.get("line"), item.get("function"))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:5]


def _changed_function_location(root: Path, path: str) -> tuple[str | None, int | None]:
    diff = run_command(["git", "diff", "--unified=0", "HEAD", "--", path], cwd=root, timeout_seconds=15)
    if diff.returncode != 0:
        return None, None
    line = None
    for raw in diff.stdout.splitlines():
        if raw.startswith("@@") and (match := re.search(r"\+(?P<line>\d+)", raw)):
            line = int(match.group("line"))
            break
    if line is None:
        return None, None
    try:
        lines = (root / path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None, line
    function = None
    definitions = re.compile(
        r"^\s*(?:async\s+)?(?:def|class|function)\s+([\w$]+)"
        r"|^\s*(?:const|let|var)\s+([\w$]+)\s*=.*(?:=>|function\b)"
    )
    for raw in reversed(lines[:line]):
        if match := definitions.search(raw):
            function = match.group(1) or match.group(2)
            break
    return function, line


def _extract_symbols(text: str) -> list[str]:
    found: list[str] = []
    for match in SYMBOL_TOKEN.finditer(text):
        token = match.group(1)
        if token in STOP_SYMBOLS or len(token) < 3:
            continue
        if token.islower() and "." not in token and "_" not in token and len(token) < 5:
            continue
        # Prefer the leaf of dotted names for mapping (Choice from click.types.Choice).
        leaf = token.rsplit(".", 1)[-1]
        if leaf in STOP_SYMBOLS:
            continue
        found.append(leaf if leaf[0].isupper() or "_" in leaf else token)
    return found


def _extract_patterns(text: str) -> list[str]:
    patterns: list[str] = []
    for match in ASSERT_LINE.finditer(text):
        compact = re.sub(r"\s+", " ", match.group(0)).strip()
        if len(compact) > 180:
            compact = compact[:179] + "…"
        patterns.append(compact)
    # Inverted / wrong-value style clues
    if re.search(r"assert .+ == .+", text) and re.search(r"'[^']+'\s*==\s*'[^']+'", text):
        patterns.append("string equality assertion mismatch")
    if " != " in text and "assert" in text.casefold():
        patterns.append("inequality assertion mismatch")
    return patterns


def _map_symbol_to_sources(root: Path, symbol: str) -> list[str]:
    if not root.is_dir() or not symbol:
        return []
    patterns = (
        re.compile(rf"\bclass\s+{re.escape(symbol)}\b"),
        re.compile(rf"\bdef\s+{re.escape(symbol)}\b"),
        re.compile(rf"\b{re.escape(symbol)}\s*="),
        re.compile(rf"\bfunction\s+{re.escape(symbol)}\b"),
        re.compile(rf"\b(?:const|let|var)\s+{re.escape(symbol)}\b"),
        re.compile(rf"\bexport\s+(?:class|function|const)\s+{re.escape(symbol)}\b"),
    )
    hits: list[tuple[int, str]] = []
    for path in _iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        score = sum(1 for pattern in patterns if pattern.search(text))
        if score:
            relative = path.relative_to(root).as_posix()
            # Prefer production paths over tests.
            score += 0 if _looks_like_test_path(relative) else 3
            hits.append((score, relative))
    hits.sort(key=lambda item: (-item[0], item[1]))
    return [path for _, path in hits[:8]]


def _iter_source_files(root: Path) -> Iterable[Path]:
    suffixes = {".cjs", ".js", ".jsx", ".mjs", ".py", ".ts", ".tsx"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        # Skip very large files
        try:
            if path.stat().st_size > 400_000:
                continue
        except OSError:
            continue
        yield path


def _git_changed_source_paths(root: Path) -> list[str]:
    inside = run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, timeout_seconds=15)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return []
    changed = run_command(["git", "diff", "--name-only", "HEAD"], cwd=root, timeout_seconds=15)
    if changed.returncode != 0:
        return []
    suffixes = {".cjs", ".js", ".jsx", ".mjs", ".py", ".ts", ".tsx"}
    paths: list[str] = []
    for raw in changed.stdout.splitlines():
        normalized = raw.strip().replace("\\", "/")
        if not normalized or Path(normalized).suffix.lower() not in suffixes:
            continue
        if _looks_like_test_path(normalized) or any(part in IGNORED_PARTS for part in Path(normalized).parts):
            continue
        paths.append(normalized)
    return sorted(set(paths))


def _looks_like_test_path(path: str) -> bool:
    lowered = path.replace("\\", "/").casefold()
    return any(
        marker in lowered
        for marker in (
            "/test/",
            "/tests/",
            "/__tests__/",
            "test_",
            "_test.",
            ".test.",
            ".spec.",
            "conftest.py",
        )
    )


__all__ = [
    "EXPLAIN_SCHEMA",
    "RootCauseAnalysis",
    "RootCauseHint",
    "analyze_root_cause",
]
