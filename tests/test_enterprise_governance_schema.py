from __future__ import annotations

import json
from pathlib import Path


def test_enterprise_governance_schema_exists() -> None:
    path = Path("schemas/v1/enterprise-governance.schema.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["type"] == "object"
    assert "retention_policy" in payload["required"]
    assert "audit_trail" in payload["required"]
    assert "export_policy" in payload["required"]
