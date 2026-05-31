from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence

from doctor_link.core.models import utc_now_iso


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
    executable = command_list[0] if command_list else None
    executable_found = shutil.which(executable) is not None if executable else None
    cwd_text = str(cwd.resolve()) if cwd is not None else None
    started_at = utc_now_iso()
    started_monotonic = time.monotonic()
    try:
        completed = subprocess.run(
            command_list,
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


def _coerce_output(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)
