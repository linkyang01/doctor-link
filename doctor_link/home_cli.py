from __future__ import annotations

import json
from pathlib import Path

import click

from doctor_link.core.friendly_errors import friendly_no_packages
from doctor_link.core.reports_indexer import index_reports
from doctor_link.p4_cli import main


@main.command("home")
@click.option("--reports", "reports_root", type=click.Path(file_okay=False, path_type=Path), default=Path("DoctorReports"), help="DoctorReports directory to index.")
@click.option("--output", "output", type=click.Path(file_okay=False, path_type=Path), default=Path(".doctor-link-home"), help="Output directory for the static home page.")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def home_command(reports_root: Path, output: Path, json_output: bool) -> None:
    """Build a local static homepage for recent diagnostic reports."""
    reports_root = reports_root.resolve()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    index = index_reports(reports_root) if reports_root.exists() else None
    packages = index.packages[:10] if index else []

    index_path = output / "index.html"
    index_path.write_text(_render_home(reports_root, packages), encoding="utf-8")

    payload = {
        "home_page": str(index_path),
        "reports_root": str(reports_root),
        "package_count": len(packages),
        "packages": [package.to_dict() for package in packages],
    }

    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    click.echo(f"Local home page: {index_path}")
    click.echo(f"Reports indexed: {len(packages)}")
    if not packages and reports_root.exists():
        click.echo("No diagnostic packages found yet.")
    elif not reports_root.exists():
        raise friendly_no_packages(reports_root)


def _render_home(reports_root: Path, packages) -> str:
    package_lines = []
    for package in packages:
        web_view = Path(package.path) / ".doctorlink-web" / "index.html"
        link = web_view if web_view.exists() else Path(package.path) / "summary.md"
        package_lines.append(
            f"<li><a href=\"file://{link}\">{package.project}</a> — {package.summary}</li>"
        )
    if not package_lines:
        package_lines.append("<li>No diagnostic packages yet. Run <code>doctor-link report .</code></li>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Doctor link Home</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; line-height: 1.5; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .muted {{ color: #555; }}
    code {{ background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Doctor link</h1>
  <p class="muted">Local diagnostic home page</p>
  <h2>Quick start</h2>
  <ul>
    <li><code>doctor-link wizard</code> — guided diagnosis</li>
    <li><code>doctor-link diagnose-now . --full</code> — one-command workflow</li>
    <li><code>doctor-link report .</code> — generate a diagnostic package</li>
  </ul>
  <h2>Recent packages</h2>
  <p class="muted">Reports root: <code>{reports_root}</code></p>
  <ul>
    {''.join(package_lines)}
  </ul>
  <h2>Docs</h2>
  <ul>
    <li>Quick start: <code>docs/quick-start.md</code></li>
    <li>Troubleshooting: <code>docs/troubleshooting.md</code></li>
  </ul>
</body>
</html>
"""