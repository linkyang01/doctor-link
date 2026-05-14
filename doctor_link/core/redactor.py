from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Pattern

from doctor_link.core.models import utc_now_iso

DEFAULT_PATTERNS: dict[str, str] = {
    "authorization_header": r"(?i)(Authorization\s*:\s*)(Bearer\s+)?[A-Za-z0-9._~+/=-]{12,}",
    "cookie_header": r"(?i)(Cookie\s*:\s*)[^\n\r]+",
    "password_assignment": r"(?i)(password\s*[:=]\s*)[^\s,;]+",
    "secret_assignment": r"(?i)(secret\s*[:=]\s*)[^\s,;]+",
    "api_key_assignment": r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+",
    "access_token_assignment": r"(?i)(access[_-]?token\s*[:=]\s*)[^\s,;]+",
    "generic_token_assignment": r"(?i)(token\s*[:=]\s*)[^\s,;]+",
}

OPTIONAL_PATTERNS: dict[str, str] = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "phone": r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)",
}

REDACTION_TEXT = "[REDACTED]"


@dataclass
class RedactionOptions:
    redact_email: bool = False
    redact_phone: bool = False
    custom_patterns: list[str] = field(default_factory=list)


@dataclass
class RedactionMatch:
    pattern_name: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RedactionResult:
    redacted_text: str
    matches: list[RedactionMatch] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return any(item.count > 0 for item in self.matches)

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed": self.changed,
            "matches": [item.to_dict() for item in self.matches],
        }


@dataclass
class RedactionReport:
    generated_at: str = field(default_factory=utc_now_iso)
    files: list[dict[str, Any]] = field(default_factory=list)
    total_replacements: int = 0

    def add_file(self, path: str, result: RedactionResult) -> None:
        replacements = sum(item.count for item in result.matches)
        self.total_replacements += replacements
        self.files.append({"path": path, "changed": result.changed, "replacements": replacements, "matches": [item.to_dict() for item in result.matches]})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Doctor link Redaction Report",
            "",
            f"- Generated at: `{self.generated_at}`",
            f"- Files scanned: `{len(self.files)}`",
            f"- Total replacements: `{self.total_replacements}`",
            "",
            "## Files",
            "",
        ]
        if not self.files:
            lines.append("- None")
        for item in self.files:
            lines.extend([
                f"### {item['path']}",
                "",
                f"- Changed: `{item['changed']}`",
                f"- Replacements: `{item['replacements']}`",
                "",
            ])
            if item["matches"]:
                lines.append("Matches:")
                lines.extend(f"- {match['pattern_name']}: {match['count']}" for match in item["matches"])
                lines.append("")
        return "\n".join(lines)


def redact_text(text: str, options: RedactionOptions | None = None) -> RedactionResult:
    """Redact sensitive information from text and return a replacement report."""
    options = options or RedactionOptions()
    patterns = _build_patterns(options)
    redacted = text
    matches: list[RedactionMatch] = []
    for name, pattern in patterns:
        redacted, count = _replace(pattern, redacted)
        if count:
            matches.append(RedactionMatch(pattern_name=name, count=count))
    return RedactionResult(redacted_text=redacted, matches=matches)


def redact_file(path: Path, options: RedactionOptions | None = None) -> RedactionResult:
    text = path.read_text(encoding="utf-8", errors="replace")
    result = redact_text(text, options)
    if result.changed:
        path.write_text(result.redacted_text, encoding="utf-8")
    return result


def redact_files(paths: list[Path], report_path: Path, options: RedactionOptions | None = None) -> RedactionReport:
    report = RedactionReport()
    for path in paths:
        if not path.is_file():
            continue
        result = redact_file(path, options)
        report.add_file(str(path), result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.to_markdown(), encoding="utf-8")
    json_path = report_path.with_suffix(".json")
    json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def _build_patterns(options: RedactionOptions) -> list[tuple[str, Pattern[str]]]:
    pattern_specs = dict(DEFAULT_PATTERNS)
    if options.redact_email:
        pattern_specs["email"] = OPTIONAL_PATTERNS["email"]
    if options.redact_phone:
        pattern_specs["phone"] = OPTIONAL_PATTERNS["phone"]
    compiled: list[tuple[str, Pattern[str]]] = [(name, re.compile(pattern)) for name, pattern in pattern_specs.items()]
    for index, pattern in enumerate(options.custom_patterns, start=1):
        compiled.append((f"custom_{index}", re.compile(pattern)))
    return compiled


def _replace(pattern: Pattern[str], text: str) -> tuple[str, int]:
    def replacement(match: re.Match[str]) -> str:
        if match.lastindex and match.lastindex >= 1:
            return f"{match.group(1)}{REDACTION_TEXT}"
        return REDACTION_TEXT

    return pattern.subn(replacement, text)
