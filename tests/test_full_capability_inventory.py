from __future__ import annotations

import ast
from pathlib import Path

import click

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
    assert len(declared) == 63
