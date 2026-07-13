from __future__ import annotations

import shlex
import time
from dataclasses import dataclass
from pathlib import Path

from doctor_link.core.command_runner import run_command


UNSAFE_SHELL_OPERATORS = {";", "|", "||", "&", ">", ">>", "<", "<<"}


@dataclass
class SafeCommandSequenceResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


def run_safe_command_sequence(command_text: str, cwd: Path, timeout_seconds: int) -> SafeCommandSequenceResult:
    """Run one or more `&&`-chained commands without invoking a shell.

    Doctor link configuration is often stored in a repository. Treating those
    strings as shell programs would allow redirections, pipelines, and command
    injection. This parser accepts normal argv quoting and sequential `&&`, but
    rejects every other shell control operator.
    """
    try:
        commands = _parse_command_sequence(command_text)
    except ValueError as exc:
        return SafeCommandSequenceResult(returncode=2, stderr=str(exc))

    started = time.monotonic()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    for command in commands:
        elapsed = time.monotonic() - started
        remaining = max(1, int(timeout_seconds - elapsed))
        result = run_command(command, timeout_seconds=remaining, cwd=cwd)
        stdout_parts.append(result.stdout)
        stderr_parts.append(result.stderr)
        if result.returncode != 0:
            return SafeCommandSequenceResult(
                returncode=result.returncode,
                stdout="".join(stdout_parts),
                stderr="".join(stderr_parts),
                timed_out=result.timed_out,
            )
    return SafeCommandSequenceResult(
        returncode=0,
        stdout="".join(stdout_parts),
        stderr="".join(stderr_parts),
    )


def validate_safe_command_sequence(command_text: str) -> str | None:
    """Return a validation error without executing the configured command."""
    try:
        _parse_command_sequence(command_text)
    except ValueError as exc:
        return str(exc)
    return None


def _parse_command_sequence(command_text: str) -> list[list[str]]:
    lexer = shlex.shlex(command_text, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = list(lexer)
    if not tokens:
        raise ValueError("Configured command is empty.")

    commands: list[list[str]] = [[]]
    for token in tokens:
        if token == "&&":
            if not commands[-1]:
                raise ValueError("Configured command contains an empty `&&` segment.")
            commands.append([])
            continue
        if token in UNSAFE_SHELL_OPERATORS:
            raise ValueError(f"Unsupported shell operator in configured command: {token}")
        commands[-1].append(token)
    if not commands[-1]:
        raise ValueError("Configured command ends with an empty `&&` segment.")
    return commands
