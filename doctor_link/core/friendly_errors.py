from __future__ import annotations

import sys
from pathlib import Path

import click

MIN_PYTHON = (3, 10)


def check_python_version() -> None:
    """Exit with a friendly message when Python is too old."""
    if sys.version_info < MIN_PYTHON:
        version = ".".join(str(part) for part in sys.version_info[:3])
        required = ".".join(str(part) for part in MIN_PYTHON)
        raise click.ClickException(
            f"Doctor link requires Python {required} or newer (found {version}).\n"
            f"Next step: install Python {required}+ and recreate your virtual environment."
        )


def friendly_path_error(path: Path, *, kind: str = "path") -> click.ClickException:
    resolved = path.expanduser()
    if kind == "folder":
        message = f"Folder not found: {resolved}"
        hint = "Check the path, then run the command again with the correct project folder."
    elif kind == "package":
        message = f"Diagnostic package not found: {resolved}"
        hint = "Run `doctor-link report <project_folder>` first to create a diagnostic package."
    else:
        message = f"Path not found: {resolved}"
        hint = "Check the path and try again."
    return click.ClickException(f"{message}\nNext step: {hint}")


def friendly_permission_error(path: Path) -> click.ClickException:
    return click.ClickException(
        f"Permission denied: {path}\n"
        "Next step: check file permissions or choose a folder you can write to."
    )


def friendly_command_not_found(command: str) -> click.ClickException:
    return click.ClickException(
        f"Command not found: {command}\n"
        "Next step: install Doctor link (`pip install -e .`) and ensure your shell can find `doctor-link`."
    )


def friendly_no_packages(reports_root: Path) -> click.ClickException:
    return click.ClickException(
        f"No diagnostic packages found under {reports_root}\n"
        "Next step: run `doctor-link report <project_folder>` or `doctor-link diagnose-now <project_folder>`."
    )


def wrap_io_error(exc: OSError, path: Path) -> click.ClickException:
    if exc.errno in {13, 1}:
        return friendly_permission_error(path)
    return click.ClickException(str(exc))
