from __future__ import annotations

SCHEMA_VERSION = "1.0.0"
SCHEMA_ID_PREFIX = "doctor-link.diagnostic-package"
DIAGNOSTIC_PACKAGE_SCHEMA_ID = f"{SCHEMA_ID_PREFIX}.v1"

CORE_PACKAGE_FILES = [
    "doctor-report.json",
    "ai-context.json",
    "user-assertions.json",
]

OPTIONAL_PACKAGE_FILES = [
    "verification-result.json",
    "ai-repair-result.json",
    "diagnosis-history.json",
]
