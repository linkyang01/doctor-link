from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LibraryFile:
    path: Path
    root: Path
    size_bytes: int

    @property
    def relative_path(self) -> str:
        return str(self.path.relative_to(self.root))

    @property
    def extension(self) -> str:
        return self.path.suffix.lower().lstrip(".")


@dataclass
class ScanResult:
    root: Path
    files: list[LibraryFile] = field(default_factory=list)


@dataclass
class TestPlan:
    title: str
    missing_categories: list[str]
    recommended_tests: list[str]
    detected_extensions: dict[str, int]

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        lines.append("## Detected extensions")
        if self.detected_extensions:
            for extension, count in sorted(self.detected_extensions.items()):
                lines.append(f"- `{extension}`: {count}")
        else:
            lines.append("- No files detected")
        lines.append("")
        lines.append("## Missing categories")
        for category in self.missing_categories or ["None"]:
            lines.append(f"- {category}")
        lines.append("")
        lines.append("## Recommended tests")
        for test in self.recommended_tests or ["No test generated"]:
            lines.append(f"- {test}")
        lines.append("")
        return "\n".join(lines)
