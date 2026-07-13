#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


CAPABILITIES = {
    "--version",
    "adapter list",
    "adapter run",
    "adapter validate",
    "ai-result",
    "ai-task",
    "archive create",
    "archive export",
    "archive inspect",
    "archive policy-check",
    "assert",
    "assertion-check",
    "ci report",
    "collect",
    "compare",
    "conformance run",
    "diagnose after",
    "diagnose before",
    "diagnose compare",
    "diagnose verify",
    "diagnose-now",
    "diagnosis-history",
    "distribution check",
    "doctor-package",
    "env",
    "handoff check",
    "handoff generate",
    "handoff list",
    "health",
    "home",
    "init",
    "integrity manifest",
    "integrity verify",
    "knowledge build",
    "knowledge export",
    "knowledge query",
    "legacy-report",
    "plan",
    "plugin list",
    "plugin run",
    "plugin validate",
    "preflight",
    "privacy export-gate",
    "privacy redaction-gate",
    "privacy scan",
    "probe",
    "record",
    "report",
    "reproduce list",
    "reproduce run",
    "risk-review",
    "scan",
    "schema validate",
    "schema migrate",
    "strategy validate",
    "test list",
    "test run",
    "verify",
    "view",
    "vly-proof",
    "wizard",
    "workbench-note",
}


@dataclass
class CommandResult:
    route: str
    arguments: list[str]
    exit_code: int
    outcome: str
    stdout_log: str
    stderr_log: str


class CapabilityRunner:
    def __init__(self, executable: str, output: Path) -> None:
        self.executable = executable
        self.output = output
        self.logs = output / "command-logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.results: list[CommandResult] = []
        self.scenario_checks: list[str] = []
        self._counter = 0

    def run(
        self,
        route: str,
        *arguments: str | Path,
        expected_codes: Iterable[int] = (0,),
        contains: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self._counter += 1
        slug = re.sub(r"[^a-z0-9]+", "-", route.casefold()).strip("-") or "command"
        stdout_path = self.logs / f"{self._counter:03d}-{slug}.stdout.log"
        stderr_path = self.logs / f"{self._counter:03d}-{slug}.stderr.log"
        command = [self.executable, *[str(item) for item in arguments]]
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            env=self._environment(),
        )
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        expected = set(expected_codes)
        combined = completed.stdout + "\n" + completed.stderr
        outcome = "passed" if completed.returncode == 0 else "expected_failure"
        self.results.append(
            CommandResult(
                route=route,
                arguments=command[1:],
                exit_code=completed.returncode,
                outcome=outcome,
                stdout_log=str(stdout_path.relative_to(self.output)),
                stderr_log=str(stderr_path.relative_to(self.output)),
            )
        )
        if completed.returncode not in expected:
            raise RuntimeError(
                f"{route} returned {completed.returncode}; expected {sorted(expected)}\n{combined[-2000:]}"
            )
        if contains is not None and contains not in combined:
            raise RuntimeError(
                f"{route} output did not contain {contains!r}\n{combined[-2000:]}"
            )
        return completed

    def run_external(self, name: str, command: list[str]) -> None:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            env=self._environment(),
        )
        path = self.logs / f"scenario-{name}.log"
        path.write_text(completed.stdout + "\n" + completed.stderr, encoding="utf-8")
        if completed.returncode != 0:
            raise RuntimeError(
                f"Scenario {name} failed\n{completed.stdout}\n{completed.stderr}"
            )
        self.scenario_checks.append(name)

    def _environment(self) -> dict[str, str]:
        environment = dict(os.environ)
        executable_parent = str(Path(self.executable).resolve().parent)
        environment["PATH"] = (
            executable_parent + os.pathsep + environment.get("PATH", "")
        )
        return environment


def _extract_path(output: str, label: str) -> Path:
    for line in output.splitlines():
        if line.startswith(label):
            return Path(line.split(": ", 1)[1]).resolve()
    raise RuntimeError(f"Could not find {label!r} in output:\n{output}")


def _extract_id(output: str, label: str) -> str:
    for line in output.splitlines():
        if line.startswith(label):
            return line.split(": ", 1)[1].strip()
    raise RuntimeError(f"Could not find {label!r} in output:\n{output}")


def _write_report(runner: CapabilityRunner, output: Path) -> None:
    covered = {item.route for item in runner.results}
    missing = sorted(CAPABILITIES - covered)
    unexpected = sorted(covered - CAPABILITIES)
    payload = {
        "schema": "doctor-link-full-capability-validation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not missing and not unexpected else "failed",
        "expected_capabilities": len(CAPABILITIES),
        "covered_capabilities": len(covered & CAPABILITIES),
        "missing_capabilities": missing,
        "unexpected_capabilities": unexpected,
        "scenario_checks": runner.scenario_checks,
        "commands": [asdict(item) for item in runner.results],
    }
    (output / "full-capability-validation.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Doctor link Full Capability Validation",
        "",
        f"- Status: `{payload['status']}`",
        f"- Capability coverage: `{payload['covered_capabilities']}/{payload['expected_capabilities']}`",
        f"- Command invocations: `{len(runner.results)}`",
        f"- Complex scenario checks: `{len(runner.scenario_checks)}`",
        "",
        "## Complex scenarios",
        "",
        *[f"- {item}" for item in runner.scenario_checks],
        "",
        "## Capability routes",
        "",
        *[f"- `{item}`" for item in sorted(covered)],
        "",
    ]
    (output / "full-capability-validation.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    if missing or unexpected:
        raise RuntimeError(
            f"Capability inventory mismatch; missing={missing}, unexpected={unexpected}"
        )


def run_validation(executable: str, output: Path, dist_dir: Path | None = None) -> Path:
    lab_root = Path(__file__).resolve().parent
    repo_root = lab_root.parents[1]
    scenario_inputs = output / "scenario-inputs"
    repair = scenario_inputs / "repair-lifecycle"
    security = scenario_inputs / "security-incident"
    extensions = scenario_inputs / "extension-governance"
    shutil.copytree(lab_root / "repair-lifecycle", repair)
    shutil.copytree(lab_root / "security-incident", security)
    shutil.copytree(lab_root / "extension-governance", extensions)
    reports = output / "DoctorReports"
    reports.mkdir(parents=True, exist_ok=True)
    runner = CapabilityRunner(executable, output)

    runner.run("--version", "--version")
    runner.run("init", "init", output / "workspace")
    runner.run("scan", "scan", repair)
    runner.run("plan", "plan", repair)
    runner.run("preflight", "preflight", repair, "--json")
    report_run = runner.run("report", "report", repair, "--out", reports)
    package = _extract_path(report_run.stdout, "Generated diagnostic package")
    runner.run(
        "legacy-report", "legacy-report", repair, "--out", output / "legacy-report"
    )
    runner.run("ai-task", "ai-task", repair, "--out", output / "ai-task")
    runner.run(
        "env", "env", "--project-root", repair, "--out", output / "environment.json"
    )
    runner.run(
        "probe",
        "probe",
        repair / "samples/sample.mp4",
        "--ffprobe",
        "missing-ffprobe-full-capability",
        "--summary",
        "--out",
        output / "probe.json",
    )
    runner.run(
        "collect",
        "collect",
        package,
        "--project-root",
        repair,
        "--logs",
        "logs/*.txt",
        "--command",
        "python -c \"print('collect-ok')\"",
        "--probe",
        repair / "samples/sample.mp4",
        "--attachment",
        repair / "samples/input.txt",
        "--redact",
        "--redact-email",
        "--redact-pattern",
        "full-capability-secret",
    )
    assertion_run = runner.run(
        "assert",
        "assert",
        package,
        "--statement",
        "Collected evidence remains locally reviewable",
        "--expected",
        "Evidence is present",
        "--actual",
        "Evidence was collected",
    )
    package_assertion_id = _extract_id(assertion_run.stdout, "Added user assertion")
    runner.run(
        "record",
        "record",
        package,
        "--name",
        "Collection smoke",
        "--status",
        "passed",
        "--assertion-id",
        package_assertion_id,
    )
    runner.run(
        "vly-proof",
        "vly-proof",
        repair,
        "--package-dir",
        package,
        "--out",
        output / "vly-proof.md",
    )
    runner.run("strategy validate", "strategy", "validate", repair, "--json")
    runner.run("reproduce list", "reproduce", "list", repair, "--json")
    runner.run("test list", "test", "list", repair, "--json")

    before_run = runner.run(
        "diagnose before",
        "diagnose",
        "before",
        "--project",
        "Full Capability Checkout",
        "--summary",
        "Checkout duplicates charges",
        "--out",
        reports,
    )
    before = _extract_path(before_run.stdout, "Created before package")
    before_assertion = runner.run(
        "assert",
        "assert",
        before,
        "--statement",
        "Checkout duplicates charges",
        "--severity",
        "critical",
    )
    repair_assertion_id = _extract_id(before_assertion.stdout, "Added user assertion")
    after_run = runner.run(
        "diagnose after",
        "diagnose",
        "after",
        "--project",
        "Full Capability Checkout",
        "--summary",
        "Checkout repaired",
        "--before-package",
        before,
        "--out",
        reports,
    )
    after = _extract_path(after_run.stdout, "Created after package")
    runner.run(
        "reproduce run",
        "reproduce",
        "run",
        "checkout-fixed",
        repair,
        "--package-dir",
        after,
        "--json",
        contains='"status": "passed"',
    )
    runner.run(
        "test run",
        "test",
        "run",
        repair,
        "--package-dir",
        after,
        "--json",
        contains='"status": "passed"',
    )
    runner.run(
        "compare",
        "compare",
        before / "doctor-report.json",
        after / "doctor-report.json",
        "--package-dir",
        after,
    )
    runner.run(
        "diagnose compare",
        "diagnose",
        "compare",
        after,
        "--json",
        contains='"comparison_status": "generated"',
    )
    runner.run(
        "diagnose verify",
        "diagnose",
        "verify",
        after,
        "--json",
        contains='"success": true',
    )
    runner.run(
        "verify",
        "verify",
        after,
        "--write-back",
        "--json",
        contains="candidate_verified",
    )
    runner.run("schema validate", "schema", "validate", after, "--write", "--json")
    runner.run("handoff list", "handoff", "list", "--json")
    runner.run(
        "handoff check",
        "handoff",
        "check",
        after,
        "--tool",
        "codex",
        "--json",
        contains="ready_for_verification_review",
    )
    handoff_dir = output / "handoff"
    runner.run(
        "handoff generate",
        "handoff",
        "generate",
        after,
        "--tool",
        "codex",
        "--out",
        handoff_dir,
        "--json",
    )
    runner.run(
        "ai-result",
        "ai-result",
        after,
        "--summary",
        "Checkout repair validated",
        "--claimed-fix",
        "Single charge returned",
        "--tool",
        "codex",
        "--assertion-id",
        repair_assertion_id,
        "--file",
        "src/service.py",
        "--verification-step",
        "Run checkout regression",
    )
    runner.run(
        "diagnosis-history",
        "diagnosis-history",
        after,
        "--ai-pass",
        "Repair and verification pass",
        "--user-correction",
        "Keep assertion evidence linked",
        "--tool",
        "codex",
        "--verification-attempt",
        "checkout-regression",
    )
    runner.run("assertion-check", "assertion-check", after, "--json")
    runner.run(
        "risk-review",
        "risk-review",
        after,
        "--file",
        "src/service.py",
        "--boundary",
        "src/",
    )
    runner.run("view", "view", after, "--build-only")
    runner.run(
        "workbench-note",
        "workbench-note",
        after,
        "--note",
        "Full capability review completed",
        "--enable-write-back",
        "--json",
    )
    runner.run(
        "doctor-package",
        "doctor-package",
        security / "raw",
        "--out",
        output / "blocked-unsafe-package.zip",
        "--json",
        expected_codes=(1,),
        contains="Privacy export gate blocked",
    )
    runner.run(
        "doctor-package",
        "doctor-package",
        after,
        "--out",
        output / "checkout-package.zip",
        "--include-web",
        "--json",
    )
    migration_package = output / "legacy-export-package"
    shutil.copytree(after, migration_package)
    migration_target = migration_package / "package-export-manifest.json"
    legacy_payload = json.loads(migration_target.read_text(encoding="utf-8"))
    legacy_payload.pop("schema")
    legacy_payload.pop("privacy_gate")
    legacy_payload["package_dir"] = str(migration_package)
    legacy_payload["output_zip"] = str(output / "legacy-export.zip")
    legacy_payload["validation"]["package_dir"] = str(migration_package)
    legacy_payload["manifest_path"] = str(migration_package / "manifest.json")
    legacy_payload["package_readme_path"] = str(migration_package / "package-readme.md")
    migration_target.unlink()
    (migration_package / "manifest.json").write_text(
        json.dumps(legacy_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    runner.run(
        "schema migrate",
        "schema",
        "migrate",
        migration_package,
        "--json",
        contains='"status": "migrated"',
    )
    runner.run(
        "home", "home", "--reports", reports, "--output", output / "home", "--json"
    )
    runner.run("health", "health", reports, "--out", output / "health", "--json")
    runner.run(
        "diagnose-now",
        "diagnose-now",
        repair,
        "--full",
        "--handoff",
        "--tool",
        "generic",
        "--no-collect",
        "--reports",
        reports,
        "--output",
        output / "diagnose-now",
        "--json",
    )
    runner.run(
        "wizard",
        "wizard",
        "--folder",
        repair,
        "--summary",
        "Full capability guided run",
        "--no-collect-evidence",
        "--no-handoff",
        "--json",
    )
    runner.run("ci report", "ci", "report", reports, "--out", output / "ci", "--json")

    fixtures = output / "conformance-fixtures"
    for category, name in (
        ("valid", "valid-package"),
        ("backward-compatible", "legacy-package"),
        ("migration", "migration-package"),
        ("invalid", "invalid-package"),
    ):
        destination = fixtures / category / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(after, destination)
        if category == "invalid":
            (destination / "doctor-report.json").unlink()
    runner.run(
        "conformance run",
        "conformance",
        "run",
        fixtures,
        "--out",
        output / "conformance",
        "--json",
    )

    runner.run(
        "knowledge build",
        "knowledge",
        "build",
        reports,
        "--out",
        output / "knowledge.json",
        "--json",
    )
    runner.run(
        "knowledge query",
        "knowledge",
        "query",
        output / "knowledge.json",
        "checkout",
        "--json",
    )
    runner.run(
        "knowledge export",
        "knowledge",
        "export",
        output / "knowledge.json",
        output / "knowledge-export.json",
        "--json",
    )

    raw = security / "raw"
    runner.run(
        "privacy scan",
        "privacy",
        "scan",
        raw,
        "--json",
        expected_codes=(1,),
        contains="blocked",
    )
    runner.run(
        "privacy redaction-gate",
        "privacy",
        "redaction-gate",
        raw,
        "--json",
        expected_codes=(1,),
        contains="blocked",
    )
    runner.run(
        "privacy export-gate",
        "privacy",
        "export-gate",
        raw,
        "--json",
        expected_codes=(1,),
        contains="blocked",
    )
    safe = output / "safe-export"
    shutil.copytree(security / "safe", safe)
    integrity_manifest = output / "integrity-manifest.json"
    runner.run(
        "integrity manifest",
        "integrity",
        "manifest",
        safe,
        "--out",
        integrity_manifest,
        "--json",
    )
    runner.run(
        "integrity verify",
        "integrity",
        "verify",
        safe,
        integrity_manifest,
        "--strict",
        "--json",
        contains='"status": "passed"',
    )
    runner.run(
        "privacy scan", "privacy", "scan", safe, "--json", contains='"status": "passed"'
    )
    runner.run(
        "privacy redaction-gate",
        "privacy",
        "redaction-gate",
        safe,
        "--json",
        contains='"status": "passed"',
    )
    runner.run(
        "privacy export-gate",
        "privacy",
        "export-gate",
        safe,
        "--manifest",
        integrity_manifest,
        "--json",
        contains='"status": "passed"',
    )
    (safe / "safe.txt").write_text("tampered\n", encoding="utf-8")
    runner.run(
        "integrity verify",
        "integrity",
        "verify",
        safe,
        integrity_manifest,
        "--strict",
        "--json",
        expected_codes=(1,),
        contains="hash-mismatch",
    )
    shutil.copy2(security / "safe/safe.txt", safe / "safe.txt")
    archive = output / "archive"
    runner.run(
        "archive create",
        "archive",
        "create",
        safe,
        archive,
        "--metadata",
        "owner=full-capability",
        "--json",
    )
    runner.run("archive inspect", "archive", "inspect", archive, "--json")
    runner.run(
        "archive policy-check",
        "archive",
        "policy-check",
        archive,
        "--max-files",
        "20",
        "--json",
    )
    runner.run(
        "archive export", "archive", "export", archive, output / "archive.zip", "--json"
    )

    adapter_manifest = extensions / ".doctorlink/adapters/lab-adapter/adapter.yml"
    plugin_manifest = extensions / ".doctorlink/plugins/lab-plugin/plugin.yml"
    runner.run("adapter list", "adapter", "list", extensions, "--json")
    runner.run("adapter validate", "adapter", "validate", adapter_manifest, "--json")
    runner.run(
        "adapter run",
        "adapter",
        "run",
        "lab-adapter",
        "verification",
        extensions,
        "--out",
        output / "adapters-dry",
        "--json",
        contains='"dry_run": true',
    )
    runner.run(
        "adapter run",
        "adapter",
        "run",
        "lab-adapter",
        "verification",
        extensions,
        "--allow-run",
        "--out",
        output / "adapters-live",
        "--json",
        contains="adapter-full-capability-ok",
    )
    runner.run("plugin list", "plugin", "list", extensions, "--json")
    runner.run("plugin validate", "plugin", "validate", plugin_manifest, "--json")
    runner.run(
        "plugin run",
        "plugin",
        "run",
        "lab-plugin",
        "verification",
        extensions,
        "--out",
        output / "plugins-dry",
        "--json",
        contains='"dry_run": true',
    )
    runner.run(
        "plugin run",
        "plugin",
        "run",
        "lab-plugin",
        "verification",
        extensions,
        "--allow-run",
        "--out",
        output / "plugins-live",
        "--json",
        contains="plugin-full-capability-ok",
    )

    effective_dist = (dist_dir or repo_root / "dist").resolve()
    if not list(effective_dist.glob("*.whl")) or not list(
        effective_dist.glob("*.tar.gz")
    ):
        raise RuntimeError(
            f"Distribution artifacts are required under {effective_dist}; run `python -m build` first."
        )
    runner.run(
        "distribution check",
        "distribution",
        "check",
        repo_root,
        "--dist",
        effective_dist,
        "--out",
        output / "distribution",
        "--json",
    )

    concurrent = []
    for name in ("concurrent-auth", "concurrent-billing"):
        concurrent.append(
            subprocess.Popen(
                [
                    executable,
                    "record",
                    str(after),
                    "--name",
                    name,
                    "--status",
                    "passed",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=runner._environment(),
            )
        )
    for process in concurrent:
        stdout, stderr = process.communicate(timeout=30)
        if process.returncode != 0:
            raise RuntimeError(f"Concurrent record failed: {stdout}\n{stderr}")
    report = json.loads((after / "doctor-report.json").read_text(encoding="utf-8"))
    names = {
        item.get("name")
        for item in report.get("test_records", [])
        if isinstance(item, dict)
    }
    if not {"concurrent-auth", "concurrent-billing"}.issubset(names):
        raise RuntimeError("Concurrent package writes lost a test record")
    runner.scenario_checks.append("concurrent package writers preserve both records")

    bash = shutil.which("bash")
    if bash is not None:
        runner.run_external(
            "six-bug-system-keeps-known-failures-blocked",
            [bash, str(repo_root / "examples/shop-service-multi-bug/run-example.sh")],
        )
    runner.scenario_checks.extend(
        [
            "before/after repair resolves only linked passing assertions",
            "privacy gates block raw secrets and pass sanitized evidence",
            "integrity verification detects post-manifest tampering",
            "adapter and plugin dry-run plus explicit execution",
            "schema, conformance, distribution, knowledge, archive, and handoff governance",
            "package export blocks raw secrets and migrates legacy manifests safely",
        ]
    )
    _write_report(runner, output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run every Doctor link CLI capability through complex local scenarios."
    )
    parser.add_argument(
        "--doctor-link",
        default=shutil.which("doctor-link"),
        help="Doctor link executable path.",
    )
    parser.add_argument(
        "--out", type=Path, default=None, help="Output directory for logs and reports."
    )
    parser.add_argument(
        "--dist",
        type=Path,
        default=None,
        help="Directory containing built wheel and sdist artifacts.",
    )
    args = parser.parse_args()
    if not args.doctor_link:
        parser.error(
            "doctor-link executable was not found; install the package or pass --doctor-link"
        )
    output = args.out or Path(tempfile.mkdtemp(prefix="doctor-link-full-capability-"))
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    final = run_validation(args.doctor_link, output, args.dist)
    print(f"Full capability validation passed: {final}")
    print(f"Report: {final / 'full-capability-validation.md'}")


if __name__ == "__main__":
    main()
