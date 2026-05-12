from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectContext:
    name: str
    root: Path
    kind: str = "generic"


class ProjectAdapter:
    """Base class for project-specific diagnostic adapters."""

    name = "generic"

    def detect(self, root: Path) -> bool:
        return True

    def describe(self, root: Path) -> ProjectContext:
        return ProjectContext(name=root.name, root=root, kind=self.name)
