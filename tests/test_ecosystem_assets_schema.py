from __future__ import annotations

import json
from pathlib import Path


def test_ecosystem_assets_schema_exists() -> None:
    path = Path("schemas/v1/ecosystem-assets.schema.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["type"] == "object"
    assert "examples" in payload["required"]
    assert "templates" in payload["required"]
    assert "documentation_index" in payload["required"]
