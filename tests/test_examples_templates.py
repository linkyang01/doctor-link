from __future__ import annotations

import json
from pathlib import Path

import yaml


EXAMPLE_PATHS = [
    "examples/sample-project/.doctorlink/diagnosis.yml",
    "examples/sample-project/.doctorlink/reproduce.yml",
    "examples/sample-project/.doctorlink/test-matrix.yml",
    "examples/diagnostic-package/README.md",
    "examples/diagnostic-package/doctor-report.json",
    "examples/diagnostic-package/summary.md",
    "examples/diagnostic-package/verification-result.json",
    "examples/ai-handoff/README.md",
    "examples/before-after/README.md",
    "docs/template-gallery.md",
]


def test_example_files_exist() -> None:
    for path in EXAMPLE_PATHS:
        assert Path(path).exists(), path


def test_sample_project_yaml_configs_parse() -> None:
    for path in [
        Path("examples/sample-project/.doctorlink/diagnosis.yml"),
        Path("examples/sample-project/.doctorlink/reproduce.yml"),
        Path("examples/sample-project/.doctorlink/test-matrix.yml"),
    ]:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path


def test_example_diagnostic_json_files_parse() -> None:
    for path in [
        Path("examples/diagnostic-package/doctor-report.json"),
        Path("examples/diagnostic-package/verification-result.json"),
    ]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path


def test_template_gallery_mentions_all_example_groups() -> None:
    text = Path("docs/template-gallery.md").read_text(encoding="utf-8")

    for expected in ["sample-project", "diagnostic-package", "ai-handoff", "before-after"]:
        assert expected in text
    assert "must not contain real secrets" in text
