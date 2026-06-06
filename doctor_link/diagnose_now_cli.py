from __future__ import annotations

from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.collector import collect_into_package
from doctor_link.core.package_builder import build_diagnostic_package, event_from_scan
from doctor_link.core.scanner import scan_library
from doctor_link.core.test_planner import generate_test_plan
from doctor_link.core