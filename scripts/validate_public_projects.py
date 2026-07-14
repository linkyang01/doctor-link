#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def load_manifest(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    projects = payload.get("projects")
    if payload.get("schema") != "doctor-link-public-project-validation-v1" or not isinstance(projects, list):
        raise ValueError("Unsupported public-project validation manifest")
    return payload


def validate_project(project: dict[str, str], workspace: Path, doctor_link: str) -> dict[str, object]:
    target = workspace / project["name"]
    expected = project["commit"].strip().casefold()
    if len(expected) != 40 or any(ch not in "0123456789abcdef" for ch in expected):
        raise RuntimeError(f"{project['name']}: commit must be a full 40-character SHA")
    # Clone by exact commit so annotated tags and moving branch tips cannot drift.
    subprocess.run(["git", "init", "--quiet", str(target)], check=True)
    subprocess.run(["git", "remote", "add", "origin", project["url"]], cwd=target, check=True)
    subprocess.run(
        ["git", "fetch", "--quiet", "--depth", "1", "origin", project["commit"]],
        cwd=target,
        check=True,
    )
    subprocess.run(["git", "checkout", "--quiet", "--force", "FETCH_HEAD"], cwd=target, check=True)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=target, check=True, capture_output=True, text=True
    ).stdout.strip()
    if commit.casefold() != expected:
        raise RuntimeError(f"{project['name']}: expected {project['commit']}, got {commit}")
    completed = subprocess.run(
        [doctor_link, "preflight", "--json", str(target)], check=False, capture_output=True, text=True
    )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{project['name']}: preflight did not return JSON: {completed.stderr}") from exc
    # Third-party projects normally lack Doctor link configuration, so warnings are
    # expected. Success means preflight completed without blockers.
    blocking_count = int(report.get("blocking_count") or 0)
    status = str(report.get("status") or "unknown")
    passed = completed.returncode == 0 and blocking_count == 0 and status in {"passed", "warning"}
    return {
        "name": project["name"],
        "language": project["language"],
        "ref": project["ref"],
        "commit": commit,
        "passed": passed,
        "status": report.get("status"),
        "blocking_count": report.get("blocking_count"),
        "warning_count": report.get("warning_count"),
        "checks": len(report.get("checks", [])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run read-only Doctor link preflight on pinned public projects.")
    parser.add_argument("--manifest", type=Path, default=Path("examples/public-project-validation/projects.json"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--doctor-link", default=shutil.which("doctor-link"))
    args = parser.parse_args()
    if not args.doctor_link:
        parser.error("doctor-link was not found; install it or pass --doctor-link")

    manifest = load_manifest(args.manifest)
    args.out.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="doctor-link-public-projects-"))
    results: list[dict[str, object]] = []
    try:
        for project in manifest["projects"]:
            results.append(validate_project(project, workspace, args.doctor_link))
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    payload = {
        "schema": "doctor-link-public-project-validation-result-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_count": len(results),
        "passed_count": sum(bool(item["passed"]) for item in results),
        "results": results,
    }
    (args.out / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Public-project validation", "", f"Passed: {payload['passed_count']}/{payload['project_count']}", ""]
    lines.extend(
        f"- {'PASS' if item['passed'] else 'FAIL'} `{item['name']}` `{item['commit']}`: "
        f"{item['checks']} checks, {item['blocking_count']} blockers, {item['warning_count']} warnings"
        for item in results
    )
    (args.out / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if payload["passed_count"] != payload["project_count"]:
        raise SystemExit(1)
    print(f"Public-project validation passed: {payload['passed_count']}/{payload['project_count']}")


if __name__ == "__main__":
    main()
