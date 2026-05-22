from __future__ import annotations

import json
from pathlib import Path

import yaml


EXAMPLE_CONFIGS = [
    "examples/basic-project/.doctorlink/diagnosis.yml",
    "examples/basic-project/.doctorlink/reproduce.yml",
    "examples/basic-project/.doctorlink/test-matrix.yml",
]

EXAMPLE_ARTIFACTS = [
    "examples/artifacts/example-ai-handoff-manifest.json",
    "examples/artifacts/example-diagnosis-workflow.json",
    "examples/artifacts/example-verification-result.json",
]


def test_example_configs_are_valid_yaml() -> None:
    for file_name in EXAMPLE_CONFIGS:
        path = Path(file_name)
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), file_name


def test_example_artifacts_are_valid_json() -> None:
    for file_name in EXAMPLE_ARTIFACTS:
        path = Path(file_name)
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), file_name


def test_basic_project_readme_mentions_core_commands() -> None:
    text = Path("examples/basic-project/README.md").read_text(encoding="utf-8")

    assert "doctor-link strategy validate" in text
    assert "doctor-link reproduce list" in text
    assert "doctor-link test run" in text


def test_examples_guide_mentions_required_template_categories() -> None:
    text = Path("docs/examples-and-templates.md").read_text(encoding="utf-8")

    for phrase in [
        "Example project",
        "Example diagnostic package flow",
        "Example AI handoff package",
        "Example before / after workflow",
        "Example verification result",
        "Template gallery",
    ]:
        assert phrase in text
