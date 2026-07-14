"""Structured change receipts for solve sessions and branch diffs."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from doctor_link.core.command_runner import run_command


RECEIPT_SCHEMA = "doctor-link-change-receipt-v1"
DIFF_FILE_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$", re.MULTILINE)
DIFF_STAT_RE = re.compile(r"^\s*(.+?)\s*\|\s*(\d+)\s*([+-]*)\s*$", re.MULTILINE)

PRODUCTION_HINTS = ("src/", "lib/", "app/", "packages/")
CONFIG_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tsconfig.json",
    "jsconfig.json",
    "pytest.ini",
    "tox.ini",
    "noxfile.py",
    ".coveragerc",
}
TEST_HINTS = ("/tests/", "/test/", "/__tests__/", "/spec/", "test_", "_test.", ".test.", ".spec.", "conftest.py")


@dataclass
class ChangedFile:
    path: str
    category: str
    status: str
    additions: int = 0
    deletions: int = 0
    protected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChangeReceipt:
    schema: str
    project_root: str
    base_ref: str | None
    head_ref: str | None
    summary: str
    files: list[dict[str, Any]] = field(default_factory=list)
    production_files: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)
    protected_changes: list[str] = field(default_factory=list)
    other_files: list[str] = field(default_factory=list)
    raw_diff: str = ""
    hash_comparison: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_change_receipt(
    project_root: Path,
    *,
    base_ref: str | None = None,
    head_ref: str | None = "HEAD",
    protected_paths: Iterable[str] | None = None,
    verification_input_changes: list[dict[str, Any]] | None = None,
    include_raw_diff: bool = True,
) -> ChangeReceipt:
    root = project_root.expanduser().resolve()
    protected = {path.replace("\\", "/") for path in (protected_paths or [])}
    base = base_ref
    if base is None:
        base = _detect_base_ref(root)
    head = head_ref or "HEAD"

    # When head is HEAD, include uncommitted working-tree edits (Codex does not commit).
    use_worktree = head in {None, "", "HEAD"}
    name_status = _git_name_status(root, base, None if use_worktree else head)
    numstat = _git_numstat(root, base, None if use_worktree else head)
    raw_diff = ""
    if include_raw_diff:
        diff_cmd = ["git", "diff", "--no-ext-diff", base] if use_worktree else ["git", "diff", "--no-ext-diff", base, head]
        raw = run_command(diff_cmd, cwd=root, timeout_seconds=60)
        raw_diff = raw.stdout if raw.returncode == 0 else raw.stderr

    files: list[ChangedFile] = []
    for path, status in name_status.items():
        adds, deletes = numstat.get(path, (0, 0))
        category = classify_path(path)
        files.append(
            ChangedFile(
                path=path,
                category=category,
                status=status,
                additions=adds,
                deletions=deletes,
                protected=path in protected or any(
                    path == item or path.startswith(item.rstrip("*").rstrip("/"))
                    for item in protected
                    if "*" not in item
                ),
            )
        )

    files.sort(key=lambda item: (item.category, item.path))
    production = [item.path for item in files if item.category == "production"]
    tests = [item.path for item in files if item.category == "test"]
    config = [item.path for item in files if item.category == "config"]
    other = [item.path for item in files if item.category == "other"]
    protected_changes = [item.path for item in files if item.protected]
    if verification_input_changes:
        for change in verification_input_changes:
            path = str(change.get("path") or "")
            if path and path not in protected_changes:
                protected_changes.append(path)

    notes = [
        "This receipt summarizes Git changes and protected-input impact.",
        "It does not prove the problem is fixed; use independent verification for that.",
    ]
    if protected_changes:
        notes.append("Protected verification inputs changed; ordinary verified status must not be claimed without review.")
    if not files:
        summary = "No file changes were detected between the compared refs."
    else:
        summary = (
            f"{len(files)} changed file(s): "
            f"{len(production)} production, {len(tests)} test, {len(config)} config, {len(other)} other."
        )

    return ChangeReceipt(
        schema=RECEIPT_SCHEMA,
        project_root=str(root),
        base_ref=base,
        head_ref=head,
        summary=summary,
        files=[item.to_dict() for item in files],
        production_files=production,
        test_files=tests,
        config_files=config,
        protected_changes=sorted(set(protected_changes)),
        other_files=other,
        raw_diff=raw_diff,
        hash_comparison=list(verification_input_changes or []),
        notes=notes,
    )


def classify_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name
    lowered = f"/{normalized.casefold()}"
    if any(marker in lowered for marker in TEST_HINTS) or name.startswith("test_"):
        return "test"
    if name in CONFIG_NAMES or normalized.endswith((".yml", ".yaml", ".lock", ".toml", ".ini")):
        # Prefer config for root manifests; keep source configs as config too.
        if any(normalized.startswith(prefix) for prefix in PRODUCTION_HINTS) and name.endswith((".py", ".js", ".ts")):
            return "production"
        return "config"
    if any(normalized.startswith(prefix) for prefix in PRODUCTION_HINTS) or name.endswith(
        (".py", ".js", ".jsx", ".ts", ".tsx", ".cjs", ".mjs")
    ):
        return "production"
    return "other"


def receipt_to_markdown(receipt: ChangeReceipt | dict[str, Any]) -> str:
    data = receipt.to_dict() if isinstance(receipt, ChangeReceipt) else receipt
    lines = [
        "# Doctor link change receipt",
        "",
        f"Summary: {data.get('summary')}",
        f"Base: `{data.get('base_ref')}`",
        f"Head: `{data.get('head_ref')}`",
        "",
        "## Files",
        "",
    ]
    files = data.get("files") or []
    if not files:
        lines.append("- (none)")
    for item in files:
        lines.append(
            f"- `{item.get('path')}` [{item.get('category')}/{item.get('status')}] "
            f"+{item.get('additions', 0)}/-{item.get('deletions', 0)}"
            f"{' protected' if item.get('protected') else ''}"
        )
    if data.get("protected_changes"):
        lines.extend(["", "## Protected input changes", ""])
        lines.extend(f"- `{path}`" for path in data["protected_changes"])
    if data.get("hash_comparison"):
        lines.extend(["", "## Hash comparison", ""])
        for item in data["hash_comparison"]:
            lines.append(
                f"- `{item.get('path')}` {item.get('change_type')} "
                f"(detected {item.get('detected_at', 'n/a')})"
            )
    if data.get("notes"):
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in data["notes"])
    return "\n".join(lines) + "\n"


def _detect_base_ref(root: Path) -> str:
    # Prefer merge-base with main/master; fall back to HEAD^ or empty tree.
    for candidate in ("main", "master"):
        exists = run_command(["git", "rev-parse", "--verify", candidate], cwd=root, timeout_seconds=15)
        if exists.returncode == 0:
            base = run_command(["git", "merge-base", candidate, "HEAD"], cwd=root, timeout_seconds=15)
            if base.returncode == 0 and base.stdout.strip():
                return base.stdout.strip()
    parent = run_command(["git", "rev-parse", "HEAD^"], cwd=root, timeout_seconds=15)
    if parent.returncode == 0 and parent.stdout.strip():
        return parent.stdout.strip()
    empty = run_command(["git", "hash-object", "-t", "tree", "/dev/null"], cwd=root, timeout_seconds=15)
    if empty.returncode == 0 and empty.stdout.strip():
        return empty.stdout.strip()
    return "HEAD"


def _git_name_status(root: Path, base: str, head: str | None) -> dict[str, str]:
    cmd = ["git", "diff", "--name-status", base] if head is None else ["git", "diff", "--name-status", base, head]
    completed = run_command(cmd, cwd=root, timeout_seconds=60)
    mapping: dict[str, str] = {}
    if completed.returncode != 0:
        return mapping
    for line in completed.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = parts[-1]
        mapping[path.replace("\\", "/")] = status
    return mapping


def _git_numstat(root: Path, base: str, head: str | None) -> dict[str, tuple[int, int]]:
    cmd = ["git", "diff", "--numstat", base] if head is None else ["git", "diff", "--numstat", base, head]
    completed = run_command(cmd, cwd=root, timeout_seconds=60)
    mapping: dict[str, tuple[int, int]] = {}
    if completed.returncode != 0:
        return mapping
    for line in completed.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        adds = int(parts[0]) if parts[0].isdigit() else 0
        deletes = int(parts[1]) if parts[1].isdigit() else 0
        mapping[parts[2].replace("\\", "/")] = (adds, deletes)
    return mapping


__all__ = [
    "ChangeReceipt",
    "ChangedFile",
    "RECEIPT_SCHEMA",
    "build_change_receipt",
    "classify_path",
    "receipt_to_markdown",
]
