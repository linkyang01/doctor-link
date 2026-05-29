from __future__ import annotations

import json
from pathlib import Path


def test_integrity_manifest_schema_exists() -> None:
    path = Path("schemas/v1/integrity-manifest.schema.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["type"] == "object"
    assert "package_id" in payload["required"]
    assert "files" in payload["required"]
    assert "signature" in payload["required"]
