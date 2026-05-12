from __future__ import annotations

from pathlib import Path

from doctor_link.adapters.base import ProjectAdapter, ProjectContext


class VlyAdapter(ProjectAdapter):
    """Vly-specific adapter placeholder.

    The first Vly use case is Core Proof: all-in-one playback validation.
    """

    name = "vly"

    def detect(self, root: Path) -> bool:
        return root.name.lower() in {"vly", "vlytestlibrary"}

    def describe(self, root: Path) -> ProjectContext:
        return ProjectContext(name="Vly", root=root, kind=self.name)
