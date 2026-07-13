from __future__ import annotations

import json
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


LOCK_NAME = ".doctorlink-package.lock"


@contextmanager
def package_transaction(package_dir: Path, timeout_seconds: float = 10.0) -> Iterator[None]:
    """Serialize package mutations across processes.

    Diagnostic packages are often updated by CLI processes started from
    separate terminals, CI jobs, or coding agents. An exclusive lock file keeps
    those read-modify-write sequences from silently overwriting each other.
    """
    package_dir = package_dir.resolve()
    lock_path = package_dir / LOCK_NAME
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if _stale(lock_path):
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for diagnostic package lock: {lock_path}")
            time.sleep(0.02)
            continue
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(json.dumps({"pid": os.getpid(), "created_at": time.time()}))
            yield
        finally:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
        return


def atomic_write_text(path: Path, text: str) -> None:
    """Replace a text file atomically after writing it beside the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))


def _stale(lock_path: Path, stale_after_seconds: float = 30.0) -> bool:
    try:
        age = time.time() - lock_path.stat().st_mtime
    except FileNotFoundError:
        return False
    return age > stale_after_seconds
