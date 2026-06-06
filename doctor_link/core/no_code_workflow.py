from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from doctor_link.core.ai_handoff import build_handoff_package
from doctor_link.core.collector import collect_into_package
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core.user_assertion_manager import add_user_assertion
from doctor_link