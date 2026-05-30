from __future__ import annotations

import json
from pathlib import Path


def test_diagnostic_knowledge_schema_exists() -> None:
    path = Path("schemas/v1/diagnostic-knowledge.schema.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["type"] == "object"
    assert "problem_taxonomy" in payload["required"]
    assert "recurring_failure_signatures" in payload["required"]
    assert "privacy_boundaries" in payload["required"]
