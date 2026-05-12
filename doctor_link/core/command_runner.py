from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from typing import Sequence

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

    def to_dict(self) -> dict:
        return asdict(self)


def run_command(command: Sequence[str], timeout_seconds: int = 30) -> CommandResult:
    """Run a command and capture stdout, stderr, return code, and timing.

    Commands are executed without a shell by default for safer diagnostics.
    """
    started_at = utc_now_iso()
    try:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return CommandResult(
            command=list(command),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            started_at=started_at,
            completed_at=utc_now_iso(),
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            command=list(command),
            returncode=-1,
            stdout=exc.stdout or "",
            stderr=exc.stderr or f"Command timed out after {timeout_seconds} seconds.",
            started_at=started_at,
            completed_at=utc_now_iso(),
            timed_out=True,
        )
    except FileNotFoundError as exc:
        return CommandResult(
            command=list(command),
            returncode=127,
            stdout="",
            stderr=str(exc),
            started_at=started_at,
            completed_at=utc_now_iso(),
        )
