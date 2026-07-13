from __future__ import annotations

import argparse
import json
import tarfile
import zipfile
from pathlib import Path


WHEEL_REQUIRED_SUFFIXES = {
    "doctor_link/entrypoint.py",
    "doctor_link/core/preflight.py",
    "doctor_link/core/safe_command_runner.py",
    "doctor_link/core/solve.py",
    "doctor_link/solve_cli.py",
    "doctor_link/py.typed",
}
SDIST_REQUIRED_SUFFIXES = {
    "README.md",
    "SECURITY.md",
    "MANIFEST.in",
    ".doctorlink/collect.yml",
    "docs/installation.md",
    "docs/automatic-solve.md",
    "schemas/v1/doctor-report.schema.json",
    "scripts/e2e_validate.sh",
    "scripts/p7_runtime_validate.sh",
    "doctor_link/core/preflight.py",
    "tests/test_preflight.py",
}
FORBIDDEN_PATH_PARTS = {
    "/.doctor-link/",
    "/__pycache__/",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".DS_Store"}


def validate_distribution_contents(dist_dir: Path) -> dict[str, object]:
    dist_dir = dist_dir.resolve()
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    errors: list[str] = []
    inspected: list[str] = []

    if not wheels:
        errors.append("No wheel found.")
    if not sdists:
        errors.append("No source distribution found.")

    for wheel in wheels:
        inspected.append(wheel.name)
        try:
            with zipfile.ZipFile(wheel) as archive:
                names = set(archive.namelist())
        except zipfile.BadZipFile:
            errors.append(f"Invalid wheel archive: {wheel.name}")
            continue
        errors.extend(_missing_suffixes(wheel.name, names, WHEEL_REQUIRED_SUFFIXES))
        if any(name.startswith("tests/") for name in names):
            errors.append(f"{wheel.name}: wheel must not include the test suite.")
        if not any(name.endswith(".dist-info/METADATA") for name in names):
            errors.append(f"{wheel.name}: METADATA is missing.")

    for sdist in sdists:
        inspected.append(sdist.name)
        try:
            with tarfile.open(sdist, "r:gz") as archive:
                names = set(archive.getnames())
        except tarfile.TarError:
            errors.append(f"Invalid source distribution: {sdist.name}")
            continue
        errors.extend(_missing_suffixes(sdist.name, names, SDIST_REQUIRED_SUFFIXES))
        errors.extend(_forbidden_members(sdist.name, names))

    return {
        "status": "passed" if not errors else "blocked",
        "dist_dir": str(dist_dir),
        "inspected": inspected,
        "errors": errors,
    }


def _missing_suffixes(artifact: str, names: set[str], required: set[str]) -> list[str]:
    return [
        f"{artifact}: required content is missing: {suffix}"
        for suffix in sorted(required)
        if not any(name.endswith(suffix) for name in names)
    ]


def _forbidden_members(artifact: str, names: set[str]) -> list[str]:
    return [
        f"{artifact}: generated or cache content must not be distributed: {name}"
        for name in sorted(names)
        if any(part in f"/{name}/" for part in FORBIDDEN_PATH_PARTS)
        or any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Doctor link wheel and sdist contents.")
    parser.add_argument("dist_dir", nargs="?", default="dist", type=Path)
    args = parser.parse_args()
    result = validate_distribution_contents(args.dist_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
