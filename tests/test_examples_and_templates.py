from __future__ import annotations

import json
from pathlib import Path

import yaml


EXAMPLE_CONFIGS = [
    "examples/basic-project/.doctorlink/diagnosis.yml",
    "examples/basic-project/.doctorlink/reproduce.yml",
    "examples/basic-project/.doctorlink/test-matrix.yml",
    "examples/shop-service-multi-bug/.doctorlink/diagnosis.yml",
    "examples/shop-service-multi-bug/.doctorlink/reproduce.yml",
    "examples/shop-service-multi-bug/.doctorlink/test-matrix.yml",
    "examples/python-api-bug/.doctorlink/diagnosis.yml",
    "examples/python-api-bug/.doctorlink/reproduce.yml",
    "examples/python-api-bug/.doctorlink/test-matrix.yml",
    "examples/media-playback-library/.doctorlink/diagnosis.yml",
    "examples/full-capability-lab/repair-lifecycle/.doctorlink/diagnosis.yml",
    "examples/full-capability-lab/repair-lifecycle/.doctorlink/reproduce.yml",
    "examples/full-capability-lab/repair-lifecycle/.doctorlink/test-matrix.yml",
    "examples/full-capability-lab/extension-governance/.doctorlink/adapters/lab-adapter/adapter.yml",
    "examples/full-capability-lab/extension-governance/.doctorlink/plugins/lab-plugin/plugin.yml",
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


def test_shop_service_multi_bug_readme_mentions_run_script() -> None:
    text = Path("examples/shop-service-multi-bug/README.md").read_text(encoding="utf-8")

    assert "run-example.sh" in text
    assert "shop-service-multi-bug" in text
    assert "P1" in text


def test_full_capability_lab_documents_complete_route_coverage() -> None:
    text = Path("examples/full-capability-lab/README.md").read_text(encoding="utf-8")

    assert "66/66" in text
    assert "run-all.py" in text
    assert "repair lifecycle" in text.casefold()
    assert "security" in text.casefold()


def test_repository_validation_outputs_are_gitignored() -> None:
    ignored = set(Path(".gitignore").read_text(encoding="utf-8").splitlines())

    assert "DoctorLinkValidation/" in ignored
    assert "DoctorLinkSelfValidation/" in ignored


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
