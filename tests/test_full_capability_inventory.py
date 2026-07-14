from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import click
import pytest

from doctor_link.entrypoint import main


def _declared_capabilities() -> set[str]:
    path = Path("examples/full-capability-lab/run-all.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "CAPABILITIES":
                    value = ast.literal_eval(node.value)
                    return {str(item) for item in value}
    raise AssertionError("CAPABILITIES set was not found")


def _load_lab_module():
    path = Path("examples/full-capability-lab/run-all.py")
    spec = importlib.util.spec_from_file_location("doctor_link_full_capability_lab", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _cli_routes(group: click.Group, prefix: str = "") -> set[str]:
    routes: set[str] = set()
    for name, command in group.commands.items():
        route = f"{prefix} {name}".strip()
        if isinstance(command, click.Group):
            routes.update(_cli_routes(command, route))
        else:
            routes.add(route)
    return routes


def test_full_capability_inventory_matches_every_cli_route() -> None:
    declared = _declared_capabilities()
    actual = _cli_routes(main) | {"--version"}

    assert declared == actual
    assert len(declared) == 67


def test_full_capability_output_can_be_reused_only_with_its_marker(tmp_path: Path) -> None:
    lab = _load_lab_module()
    output = tmp_path / "lab-output"

    assert lab._prepare_output_directory(output) == output.resolve()
    assert (output / lab.OUTPUT_MARKER).is_file()
    stale = output / "stale-result.txt"
    stale.write_text("old run", encoding="utf-8")

    assert lab._prepare_output_directory(output) == output.resolve()
    assert not stale.exists()
    assert (output / lab.OUTPUT_MARKER).is_file()


def test_full_capability_output_refuses_to_replace_unowned_data(tmp_path: Path) -> None:
    lab = _load_lab_module()
    output = tmp_path / "user-data"
    output.mkdir()
    important = output / "important.txt"
    important.write_text("keep me", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Refusing to replace"):
        lab._prepare_output_directory(output)

    assert important.read_text(encoding="utf-8") == "keep me"
