"""Doctor link package."""

__version__ = "0.1.0"

# Import side-effect CLI extensions so commands are available from doctor_link.p4_cli.main.
try:  # pragma: no cover - defensive registration guard.
    from doctor_link import knowledge_archive_cli as _knowledge_archive_cli  # noqa: F401
except Exception:  # pragma: no cover - importing the package should never fail because of CLI extensions.
    _knowledge_archive_cli = None
