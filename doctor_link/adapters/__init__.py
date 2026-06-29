"""Project adapters for Doctor link."""

from doctor_link.adapters.base import ProjectAdapter, ProjectContext
from doctor_link.adapters.registry import builtin_adapters, detect_adapter, resolve_adapter_name
from doctor_link.adapters.vly import VlyAdapter

__all__ = [
    "ProjectAdapter",
    "ProjectContext",
    "VlyAdapter",
    "builtin_adapters",
    "detect_adapter",
    "resolve_adapter_name",
]