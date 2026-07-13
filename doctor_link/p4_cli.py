from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.cli import main
from doctor_link.core.adapter_runtime import discover_adapters, run_adapter, validate_adapter_file
from doctor_link.core.ci_automation import write_ci_report
from doctor_link.core.conformance import run_conformance_suite, write_conformance_report
from doctor_link.core.diagnosis_pipeline import run_diagnosis_compare, run_diagnosis_verify
from doctor_link.core.diagnosis_workflow import create_after_package, create_before_package
from doctor_link.core.distribution_readiness import write_distribution_readiness_report
from doctor_link.core.integrity_privacy import (
    export_safety_gate,
    redaction_gate,
    scan_privacy,
    verify_integrity_manifest,
    write_gate_result,
    write_integrity_manifest,
    write_integrity_verify,
    write_privacy_scan,
)
from doctor_link.core.plugin_runtime import discover_plugins, run_plugin, validate_plugin_file
from doctor_link.core.project_health import write_project_health
from doctor_link.core.package_exporter import migrate_legacy_export_manifest
from doctor_link.core.reproduction import load_reproduction_catalog, run_reproduction
from doctor_link.core.schema_validator import validate_diagnostic_package, write_schema_validation_result
from doctor_link.core.test_matrix_runner import load_test_matrix, run_test_matrix


@main.group("reproduce")
def reproduce_group() -> None:
    """Manage reproduction entries."""


@reproduce_group.command("list")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def reproduce_list(project_root: Path, json_output: bool) -> None:
    """List reproduction entries from .doctorlink/reproduce.yml."""
    catalog = load_reproduction_catalog(project_root)
    if json_output:
        click.echo(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo("# Reproductions")
    for entry in catalog.entries:
        click.echo(f"- {entry.reproduction_id}: {entry.title} ({entry.kind})")
    for warning in catalog.warnings:
        click.echo(f"Warning: {warning}")


@reproduce_group.command("run")
@click.argument("reproduction_id")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--package-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional diagnostic package to receive reproduction evidence.")
@click.option("--timeout", default=60, show_default=True, type=int, help="Command timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def reproduce_run(reproduction_id: str, project_root: Path, package_dir: Path | None, timeout: int, json_output: bool) -> None:
    """Run a command or test reproduction entry."""
    result = run_reproduction(project_root, reproduction_id, package_dir=package_dir, timeout_seconds=timeout)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Reproduction: {result.reproduction_id}")
        click.echo(f"Status: {result.status}")
        if result.evidence_id:
            click.echo(f"Evidence: {result.evidence_id}")
    if result.status not in {"passed", "manual"}:
        raise click.exceptions.Exit(1)


@main.group("test")
def test_group() -> None:
    """Run project test matrix jobs."""


@test_group.command("list")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def test_list(project_root: Path, json_output: bool) -> None:
    """List executable test matrix jobs."""
    catalog = load_test_matrix(project_root)
    if json_output:
        click.echo(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo("# Test Matrix Jobs")
    for job in catalog.jobs:
        click.echo(f"- {job.job_id}: {job.title}")
    for warning in catalog.warnings:
        click.echo(f"Warning: {warning}")


@test_group.command("run")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--job", "job_id", default=None, help="Optional job id to run.")
@click.option("--package-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional diagnostic package to receive test evidence.")
@click.option("--timeout", default=120, show_default=True, type=int, help="Command timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def test_run(project_root: Path, job_id: str | None, package_dir: Path | None, timeout: int, json_output: bool) -> None:
    """Run executable test matrix jobs."""
    results = run_test_matrix(project_root, package_dir=package_dir, job_id=job_id, timeout_seconds=timeout)
    if json_output:
        click.echo(json.dumps([item.to_dict() for item in results], ensure_ascii=False, indent=2))
    else:
        for result in results:
            click.echo(f"Test job: {result.job_id}")
            click.echo(f"Status: {result.status}")
            if result.evidence_id:
                click.echo(f"Evidence: {result.evidence_id}")
    if any(result.required and result.status != "passed" for result in results):
        raise click.exceptions.Exit(1)


@main.group("diagnose")
def diagnose_group() -> None:
    """Run before / after diagnosis workflow commands."""


@diagnose_group.command("before")
@click.option("--project", required=True, help="Project name.")
@click.option("--summary", required=True, help="Before-state diagnostic summary.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def diagnose_before(project: str, summary: str, output: Path) -> None:
    """Create a before diagnostic package."""
    package_dir = create_before_package(project=project, summary=summary, output_dir=output)
    click.echo(f"Created before package: {package_dir}")
    click.echo(f"Before report: {package_dir / 'doctor-report.json'}")


@diagnose_group.command("after")
@click.option("--project", required=True, help="Project name.")
@click.option("--summary", required=True, help="After-state diagnostic summary.")
@click.option("--before-package", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True, help="Before diagnostic package.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), help="Output directory.")
def diagnose_after(project: str, summary: str, before_package: Path, output: Path) -> None:
    """Create an after diagnostic package linked to a before package."""
    package_dir = create_after_package(project=project, summary=summary, output_dir=output, before_package=before_package)
    click.echo(f"Created after package: {package_dir}")
    click.echo(f"Before report: {before_package / 'doctor-report.json'}")
    click.echo(f"After report: {package_dir / 'doctor-report.json'}")


@diagnose_group.command("compare")
@click.argument("after_package", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def diagnose_compare(after_package: Path, json_output: bool) -> None:
    """Generate comparison summary for an after package."""
    summary = run_diagnosis_compare(after_package)
    if json_output:
        click.echo(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Comparison status: {summary.comparison_status}")
    click.echo(f"Summary: {after_package / 'diagnosis-pipeline-summary.md'}")


@diagnose_group.command("verify")
@click.argument("after_package", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--no-write-back", is_flag=True, help="Do not write verification into report files.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def diagnose_verify(after_package: Path, no_write_back: bool, json_output: bool) -> None:
    """Run automated comparison and verification for an after package."""
    summary = run_diagnosis_verify(after_package, write_back=not no_write_back)
    if json_output:
        click.echo(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Verification status: {summary.verification_status}")
        click.echo(f"Pipeline success: {summary.success}")
        click.echo(f"Summary: {after_package / 'diagnosis-pipeline-summary.md'}")
    if not summary.success:
        raise click.exceptions.Exit(1)


@main.group("schema")
def schema_group() -> None:
    """Validate diagnostic package schema compatibility."""


@schema_group.command("validate")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--write", "write_result", is_flag=True, help="Write schema-validation-result files into the package.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def schema_validate(package_dir: Path, write_result: bool, json_output: bool) -> None:
    """Validate a diagnostic package against Doctor link schema v1 policy."""
    result = validate_diagnostic_package(package_dir)
    if write_result:
        write_schema_validation_result(package_dir, result)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Schema validation status: {result.status}")
        click.echo(f"Checked files: {len(result.checked_files)}")
        click.echo(f"Findings: {len(result.findings)}")
    if not result.valid:
        raise click.ClickException("Schema validation failed.")


@schema_group.command("migrate")
@click.argument("package_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def schema_migrate(package_dir: Path, json_output: bool) -> None:
    """Migrate a legacy package export manifest and preserve a backup."""
    try:
        result = migrate_legacy_export_manifest(package_dir)
    except (FileNotFoundError, FileExistsError, ValueError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Schema migration status: {result.status}")
    click.echo(f"Portable export manifest: {result.target_path}")
    if result.backup_path:
        click.echo(f"Legacy backup: {result.backup_path}")


@main.group("conformance")
def conformance_group() -> None:
    """Run schema compatibility conformance suites."""


@conformance_group.command("run")
@click.argument("fixtures_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports/conformance"), help="Output directory.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def conformance_run(fixtures_root: Path, output: Path, json_output: bool) -> None:
    """Run a compatibility and conformance suite."""
    report = run_conformance_suite(fixtures_root)
    write_conformance_report(output, report)
    if json_output:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Conformance status: {report.status}")
        click.echo(f"Compatibility score: {report.compatibility_score}")
        click.echo(f"Report: {output / 'conformance-report.md'}")
    if report.status != "passed":
        raise click.ClickException("Conformance suite failed.")


@main.group("ci")
def ci_group() -> None:
    """Generate CI and GitHub Actions diagnostic reports."""


@ci_group.command("report")
@click.argument("reports_dir", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), required=False)
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Output directory for CI report artifacts.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def ci_report(reports_dir: Path, output: Path | None, json_output: bool) -> None:
    """Generate CI report, GitHub step summary, trend, triage and artifact index."""
    report = write_ci_report(reports_dir, output_dir=output)
    if json_output:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return
    out = Path(report.output_dir)
    click.echo(f"CI report status: {report.status}")
    click.echo(f"Regression score: {report.regression_score}")
    click.echo(f"Report: {out / 'ci-report.md'}")
    click.echo(f"GitHub summary: {out / 'github-step-summary.md'}")
    click.echo(f"Artifact index: {out / 'ci-artifact-index.json'}")


@main.group("distribution")
def distribution_group() -> None:
    """Run local distribution readiness checks."""


@distribution_group.command("check")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--dist", "dist_dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Distribution artifact directory.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Output directory for distribution readiness artifacts.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def distribution_check(project_root: Path, dist_dir: Path | None, output: Path | None, json_output: bool) -> None:
    """Generate local distribution readiness report without publishing."""
    report = write_distribution_readiness_report(project_root, dist_dir=dist_dir, output_dir=output)
    if json_output:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        out = Path(report.output_dir)
        click.echo(f"Distribution readiness status: {report.status}")
        click.echo(f"Blocking findings: {report.blocking_count}")
        click.echo(f"Warnings: {report.warning_count}")
        click.echo(f"Report: {out / 'distribution-report.md'}")
        click.echo(f"Manifest: {out / 'distribution-manifest.json'}")
        click.echo(f"Checksums: {out / 'checksums.sha256'}")
    if report.status != "passed":
        raise click.ClickException("Distribution readiness blocked.")


@main.group("adapter")
def adapter_group() -> None:
    """Discover, validate, and run local adapters."""


@adapter_group.command("list")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--adapters-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Adapter directory override.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def adapter_list(project_root: Path, adapters_dir: Path | None, json_output: bool) -> None:
    """List discovered local adapters."""
    catalog = discover_adapters(project_root, adapters_dir)
    if json_output:
        click.echo(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo("# Adapters")
    if not catalog.adapters:
        click.echo("- None")
    for adapter in catalog.adapters:
        click.echo(f"- {adapter.adapter_id}: {adapter.name} ({adapter.version})")
    for finding in catalog.findings:
        click.echo(f"Finding: {finding.get('severity')} {finding.get('code')} {finding.get('message')}")


@adapter_group.command("validate")
@click.argument("manifest", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def adapter_validate(manifest: Path, json_output: bool) -> None:
    """Validate an adapter manifest."""
    result = validate_adapter_file(manifest)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Adapter validation status: {result.status}")
        click.echo(f"Adapter: {result.adapter_id}")
        click.echo(f"Findings: {len(result.findings)}")
    if not result.valid:
        raise click.ClickException("Adapter validation failed.")


@adapter_group.command("run")
@click.argument("adapter_id")
@click.argument("capability")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--adapters-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Adapter directory override.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Output directory for adapter run records.")
@click.option("--timeout", default=60, show_default=True, type=int, help="Adapter command timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def adapter_run(
    adapter_id: str,
    capability: str,
    project_root: Path,
    adapters_dir: Path | None,
    output: Path | None,
    timeout: int,
    json_output: bool,
) -> None:
    """Run a configured local adapter capability."""
    result = run_adapter(
        project_root,
        adapter_id,
        capability,
        adapters_dir=adapters_dir,
        output_dir=output,
        timeout_seconds=timeout,
    )
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Adapter run status: {result.status}")
    click.echo(f"Adapter: {result.adapter_id}")
    click.echo(f"Capability: {result.capability}")
    click.echo(f"Return code: {result.return_code}")
    if result.status != "passed":
        raise click.ClickException("Adapter run failed.")


@main.group("plugin")
def plugin_group() -> None:
    """Discover, validate, and run local plugins."""


@plugin_group.command("list")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--plugins-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Plugin directory override.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def plugin_list(project_root: Path, plugins_dir: Path | None, json_output: bool) -> None:
    """List discovered local plugins."""
    catalog = discover_plugins(project_root, plugins_dir)
    if json_output:
        click.echo(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo("# Plugins")
    if not catalog.plugins:
        click.echo("- None")
    for plugin in catalog.plugins:
        click.echo(f"- {plugin.plugin_id}: {plugin.name} ({plugin.version})")
    for finding in catalog.findings:
        click.echo(f"Finding: {finding.get('severity')} {finding.get('code')} {finding.get('message')}")


@plugin_group.command("validate")
@click.argument("manifest", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def plugin_validate(manifest: Path, json_output: bool) -> None:
    """Validate a plugin manifest."""
    result = validate_plugin_file(manifest)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Plugin validation status: {result.status}")
        click.echo(f"Plugin: {result.plugin_id}")
        click.echo(f"Findings: {len(result.findings)}")
    if not result.valid:
        raise click.ClickException("Plugin validation failed.")


@plugin_group.command("run")
@click.argument("plugin_id")
@click.argument("extension_point")
@click.argument("project_root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--plugins-dir", type=click.Path(file_okay=False, path_type=Path), default=None, help="Plugin directory override.")
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Output directory for plugin run records.")
@click.option("--timeout", default=60, show_default=True, type=int, help="Plugin command timeout in seconds.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def plugin_run(
    plugin_id: str,
    extension_point: str,
    project_root: Path,
    plugins_dir: Path | None,
    output: Path | None,
    timeout: int,
    json_output: bool,
) -> None:
    """Run a configured local plugin extension point."""
    result = run_plugin(
        project_root,
        plugin_id,
        extension_point,
        plugins_dir=plugins_dir,
        output_dir=output,
        timeout_seconds=timeout,
    )
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Plugin run status: {result.status}")
    click.echo(f"Plugin: {result.plugin_id}")
    click.echo(f"Extension point: {result.extension_point}")
    click.echo(f"Return code: {result.return_code}")
    if result.status != "passed":
        raise click.ClickException("Plugin run failed.")


@main.group("integrity")
def integrity_group() -> None:
    """Generate and verify local integrity manifests."""


@integrity_group.command("manifest")
@click.argument("root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=Path("DoctorReports/integrity-manifest.json"), help="Integrity manifest output path.")
@click.option("--include", "includes", multiple=True, help="Optional include glob. Can be passed multiple times.")
@click.option("--exclude", "excludes", multiple=True, help="Optional exclude glob. Can be passed multiple times.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def integrity_manifest(root: Path, output: Path, includes: tuple[str, ...], excludes: tuple[str, ...], json_output: bool) -> None:
    """Generate an unsigned local integrity manifest."""
    manifest = write_integrity_manifest(root, output, list(includes) or None, list(excludes) or None)
    if json_output:
        click.echo(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2))
        return
    click.echo(f"Integrity manifest: {output}")
    click.echo(f"Files: {len(manifest.files)}")
    click.echo("Warning: unsigned manifest")


@integrity_group.command("verify")
@click.argument("root", type=click.Path(file_okay=False, path_type=Path))
@click.argument("manifest", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional verification report output path.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def integrity_verify(root: Path, manifest: Path, output: Path | None, json_output: bool) -> None:
    """Verify hashes, missing files, and unsafe paths in an integrity manifest."""
    result = verify_integrity_manifest(root, manifest)
    if output:
        write_integrity_verify(result, output)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Integrity verification status: {result.status}")
        click.echo(f"Checked files: {result.checked_files}")
        click.echo(f"Findings: {len(result.findings)}")
    if result.status != "passed":
        raise click.ClickException("Integrity verification blocked.")


@main.group("privacy")
def privacy_group() -> None:
    """Run local privacy, redaction, and export safety gates."""


@privacy_group.command("scan")
@click.argument("root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--policy", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="Optional privacy policy file.")
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional privacy scan report output path.")
@click.option("--include", "includes", multiple=True, help="Optional include glob. Can be passed multiple times.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def privacy_scan(root: Path, policy: Path | None, output: Path | None, includes: tuple[str, ...], json_output: bool) -> None:
    """Scan local files for configured privacy patterns."""
    result = scan_privacy(root, policy, list(includes) or None)
    if output:
        write_privacy_scan(result, output)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Privacy scan status: {result.status}")
        click.echo(f"Scanned files: {result.scanned_files}")
        click.echo(f"Findings: {len(result.findings)}")
    if result.status != "passed":
        raise click.ClickException("Privacy scan blocked.")


@privacy_group.command("redaction-gate")
@click.argument("root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--policy", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="Optional privacy policy file.")
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional redaction gate output path.")
@click.option("--include", "includes", multiple=True, help="Optional include glob. Can be passed multiple times.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def privacy_redaction_gate(root: Path, policy: Path | None, output: Path | None, includes: tuple[str, ...], json_output: bool) -> None:
    """Block when files still contain privacy findings requiring redaction."""
    result = redaction_gate(root, policy, list(includes) or None)
    if output:
        write_gate_result(result, output)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Redaction gate status: {result.status}")
        click.echo(f"Findings: {len(result.findings)}")
    if result.status != "passed":
        raise click.ClickException("Redaction gate blocked.")


@privacy_group.command("export-gate")
@click.argument("root", type=click.Path(file_okay=False, path_type=Path), default=Path("."), required=False)
@click.option("--policy", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="Optional privacy policy file.")
@click.option("--manifest", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="Optional integrity manifest to verify before export.")
@click.option("--out", "output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Optional export gate output path.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def privacy_export_gate(root: Path, policy: Path | None, manifest: Path | None, output: Path | None, json_output: bool) -> None:
    """Block unsafe local exports using privacy and optional integrity checks."""
    result = export_safety_gate(root, policy, manifest)
    if output:
        write_gate_result(result, output)
    if json_output:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        click.echo(f"Export safety gate status: {result.status}")
        click.echo(f"Findings: {len(result.findings)}")
    if result.status != "passed":
        raise click.ClickException("Export safety gate blocked.")


@main.command("health")
@click.argument("reports_dir", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), required=False)
@click.option("--out", "output", type=click.Path(file_okay=False, path_type=Path), default=None, help="Optional output directory.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def health_command(reports_dir: Path, output: Path | None, json_output: bool) -> None:
    """Generate project health summary from DoctorReports."""
    summary = write_project_health(reports_dir, output_dir=output)
    if json_output:
        click.echo(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
        return
    out = output or reports_dir
    click.echo(f"Project health status: {summary.status}")
    click.echo(f"Summary: {out / 'project-health.md'}")


if __name__ == "__main__":
    main()
