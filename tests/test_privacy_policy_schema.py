from __future__ import annotations

import json
from pathlib import Path


def test_privacy_policy_schema_exists() -> None:
    path = Path("schemas/v1/privacy-policy.schema.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["type"] == "object"
    assert "package_privacy_level" in payload["required"]
    assert "redaction_level" in payload["required"]
    assert "export_safety_level" in payload["required"]
