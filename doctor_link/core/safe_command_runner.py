from __future__ import annotations

import os
import re
import shlex
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from doctor_link.core.command_runner import run_command


UNSAFE_SHELL_OPERATORS = {";", "|", "||", "&", ">", ">>", "<", "<<"}


@dataclass
class SafeCommandSequenceResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


@dataclass
class SafeCommand:
    argv: list[str]
    environment: dict[str, str]


ENVIRONMENT_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$", re.DOTALL)


def run_safe_command_sequence(
    command_text: str,
    cwd: Path,
    timeout_seconds: int,
    environment_overrides: Mapping[str, str] | None = None,
) -> SafeCommandSequenceResult:
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
        environment = dict(os.environ)
        if environment_overrides:
            environment.update(environment_overrides)
        environment.update(command.environment)
        result = run_command(command.argv, timeout_seconds=remaining, cwd=cwd, env=environment)
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


def parse_safe_command_sequence(command_text: str) -> list[SafeCommand]:
    """Parse a validated command into shell-free argv segments.

    Callers that need to inspect referenced files should use this helper so
    discovery follows exactly the same quoting and operator rules as runtime
    execution.
    """
    return _parse_command_sequence(command_text)


def _parse_command_sequence(command_text: str) -> list[SafeCommand]:
    lexer = shlex.shlex(command_text, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = list(lexer)
    if not tokens:
        raise ValueError("Configured command is empty.")

    command_tokens: list[list[str]] = [[]]
    for token in tokens:
        if token == "&&":
            if not command_tokens[-1]:
                raise ValueError("Configured command contains an empty `&&` segment.")
            command_tokens.append([])
            continue
        if token in UNSAFE_SHELL_OPERATORS:
            raise ValueError(f"Unsupported shell operator in configured command: {token}")
        command_tokens[-1].append(token)
    if not command_tokens[-1]:
        raise ValueError("Configured command ends with an empty `&&` segment.")

    commands: list[SafeCommand] = []
    for segment in command_tokens:
        environment: dict[str, str] = {}
        index = 0
        while index < len(segment) and ENVIRONMENT_ASSIGNMENT.fullmatch(segment[index]):
            name, value = segment[index].split("=", 1)
            environment[name] = os.path.expandvars(value)
            index += 1
        argv = segment[index:]
        if not argv:
            raise ValueError("Configured command segment contains environment assignments but no executable.")
        commands.append(SafeCommand(argv=argv, environment=environment))
    return commands
