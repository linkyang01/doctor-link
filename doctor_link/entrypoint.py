from __future__ import annotations

from doctor_link.core.friendly_errors import check_python_version
from doctor_link.p4_cli import main

# Import CLI extensions explicitly for the packaged console entrypoint.
from doctor_link import diagnose_now_cli as _diagnose_now_cli  # noqa: F401
from doctor_link import handoff_cli as _handoff_cli  # noqa: F401
from doctor_link import home_cli as _home_cli  # noqa: F401
from doctor_link import knowledge_archive_cli as _knowledge_archive_cli  # noqa: F401
from doctor_link import solve_cli as _solve_cli  # noqa: F401
from doctor_link import wizard_cli as _wizard_cli  # noqa: F401
from doctor_link.hardening_cli import register_hardening_commands

check_python_version()
register_hardening_commands()

__all__ = ["main"]
