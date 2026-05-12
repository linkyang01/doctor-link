from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from doctor_link.core.models import utc_now_iso


def collect_environment(project_root: Path | None = None) -> dict[str, Any]:
    """Collect basic local environment information for a diagnostic package."""
    payload: dict[str, Any] = {
        "collected_at": utc_now_iso(),
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "implementation": platform.python_implementation(),
        },
        "process": {
            "cwd": os.getcwd(),
            "pid": os.getpid(),
        },
    }

    if project_root is not None:
        root = project_root.resolve()
        payload["project"] = {
            "root": str(root),
            "exists": root.exists(),
            "is_git_repo": (root / ".git").exists(),
        }

    return payload
