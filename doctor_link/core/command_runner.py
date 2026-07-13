from __future__ import annotations

import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence

from doctor_link.core.models import utc_now_iso


PORTABLE_PACKAGE_MANAGER_EXECUTABLES = frozenset({"bun", "corepack", "npm", "npx", "pnpm", "yarn"})


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    completed_at: str
    timed_out: bool = False
    duration_seconds: float = 0.0
    cwd: str | None = None
    timeout_seconds: int | None = None
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    executable: str | None = None
    executable_found: bool | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def run_command(command: Sequence[str], timeout_seconds: int = 30, cwd: Path | None = None, env: Mapping[str, str] | None = None) -> CommandResult:
    """Run a command and capture stdout, stderr, return code, and timing.

    Commands are executed without a shell by default for safer diagnostics.
    P7.1 adds richer metadata so diagnostic packages can explain how command
    evidence was produced without requiring shell history or hidden context.
    """
    command_list = list(command)
    resolved_command = resolve_command(command_list, env)
    executable = resolved_command[0] if resolved_command else None
    executable_found = shutil.which(executable, path=env.get("PATH") if env else None) is not None if executable else None
    cwd_text = str(cwd.resolve()) if cwd is not None else None
    started_at = utc_now_iso()
    started_monotonic = time.monotonic()
    try:
        completed = subprocess.run(
            resolved_command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            cwd=str(cwd) if cwd is not None else None,
            env=dict(env) if env is not None else None,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        return CommandResult(
            command=command_list,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            started_at=started_at,
            completed_at=utc_now_iso(),
            duration_seconds=round(time.monotonic() - started_monotonic, 6),
            cwd=cwd_text,
            timeout_seconds=timeout_seconds,
            stdout_bytes=len(stdout.encode("utf-8")),
            stderr_bytes=len(stderr.encode("utf-8")),
            executable=executable,
            executable_found=executable_found,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _coerce_output(exc.stdout)
        stderr = _coerce_output(exc.stderr) or f"Command timed out after {timeout_seconds} seconds."
        return CommandResult(
            command=command_list,
            returncode=-1,
            stdout=stdout,
            stderr=stderr,
            started_at=started_at,
            completed_at=utc_now_iso(),
            timed_out=True,
            duration_seconds=round(time.monotonic() - started_monotonic, 6),
            cwd=cwd_text,
            timeout_seconds=timeout_seconds,
            stdout_bytes=len(stdout.encode("utf-8")),
            stderr_bytes=len(stderr.encode("utf-8")),
            executable=executable,
            executable_found=executable_found,
            error="timeout",
        )
    except FileNotFoundError as exc:
        stderr = str(exc)
        return CommandResult(
            command=command_list,
            returncode=127,
            stdout="",
            stderr=stderr,
            started_at=started_at,
            completed_at=utc_now_iso(),
            duration_seconds=round(time.monotonic() - started_monotonic, 6),
            cwd=cwd_text,
            timeout_seconds=timeout_seconds,
            stdout_bytes=0,
            stderr_bytes=len(stderr.encode("utf-8")),
            executable=executable,
            executable_found=False,
            error="file_not_found",
        )


def resolve_command(command: Sequence[str], env: Mapping[str, str] | None = None) -> list[str]:
    """Resolve portable executable aliases without invoking a shell.

    Modern macOS installations commonly provide no ``python`` command, while
    cross-platform project configuration often uses that spelling. Bind it to
    the interpreter currently running Doctor link when the alias is absent.

    Windows package-manager launchers commonly use ``.cmd`` files. ``which``
    understands ``PATHEXT`` while ``CreateProcess`` does not resolve a bare
    launcher name the same way, so bind supported package managers to the
    concrete executable path before handing the argv list to subprocess.
    """
    resolved = list(command)
    if not resolved:
        return resolved
    search_path = env.get("PATH") if env else None
    executable = shutil.which(resolved[0], path=search_path)
    if resolved[0] == "python" and executable is None:
        resolved[0] = sys.executable
    elif resolved[0].casefold() in PORTABLE_PACKAGE_MANAGER_EXECUTABLES and executable is not None:
        resolved[0] = executable
    return resolved


def _coerce_output(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)
