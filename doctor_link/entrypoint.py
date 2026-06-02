from __future__ import annotations

from doctor_link.p4_cli import main

# Import CLI extensions explicitly for the packaged console entrypoint.
from doctor_link import knowledge_archive_cli as _knowledge_archive_cli  # noqa: F401

__all__ = ["main"]
