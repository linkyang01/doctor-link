from __future__ import annotations

from pathlib import Path

from doctor_link.adapters.base import ProjectAdapter
from doctor_link.adapters.vly import VlyAdapter
from doctor_link.core.diagnosis_strategy import load_diagnosis_strategy

_BUILTIN_ADAPTERS: tuple[type[ProjectAdapter], ...] = (VlyAdapter,)


def builtin_adapters() -> list[ProjectAdapter]:
    return [adapter_cls() for adapter_cls in _BUILTIN_ADAPTERS]


def detect_adapter(root: Path) -> ProjectAdapter | None:
    """Return the first built-in adapter that recognizes the project root."""
    root = root.resolve()
    for adapter in builtin_adapters():
        if adapter.detect(root):
            return adapter
    return None


def resolve_adapter_name(root: Path) -> str:
    """Resolve adapter name from detection or diagnosis strategy."""
    adapter = detect_adapter(root)
    if adapter is not None:
        return adapter.name
    strategy = load_diagnosis_strategy(root).strategy
    if strategy is not None and strategy.project_type not in {"", "generic"}:
        return strategy.project_type
    return "generic"
