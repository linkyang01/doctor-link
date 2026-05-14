from __future__ import annotations

import html
import json
from pathlib import Path

from doctor_link.core.web_package_reader import DiagnosticPackageView, PackageJsonSection, PackageSection


def render_package_html(view: DiagnosticPackageView) -> str:
    """Render a diagnostic package view as a self-contained HTML page."""
    nav_items = []
    body_sections = []

    for section in view.sections:
        anchor = f"section-{section.key}"
        nav_items.append(f'<a href="#{anchor}">{html.escape(section.title)}</a>')
        body_sections.append(_render_text_section(anchor, section))

    for section in view.json_sections:
        anchor = f"json-{section.key}"
        nav_items.append(f'<a href="#{anchor}">{html.escape(section.title)}</a>')
        body_sections.append(_render_json_section(anchor, section))

    body_sections.append(_render_evidence_files(view.evidence_files))

    warnings = "".join(f"<li>{html.escape(item)}</li>" for item in view.warnings) or "<li>None</li>"
    nav = "".join(nav_items)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Doctor link - {html.escape(view.title)}</title>
  <style>
    :root {{
      --bg: #f4f7fb;
      --panel: #ffffff;
      --text: #142033;
      --muted: #667085;
      --line: #d8e0ea;
      --accent: #315f9f;
      --accent-soft: #e7eef8;
      --warning: #8a5a00;
      --warning-bg: #fff6df;
      --code-bg: #0f172a;
      --code-text: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }}
    header {{
      padding: 28px 36px;
      background: linear-gradient(135deg, #1f4f86, #4e79ad);
      color: #fff;
    }}
    header h1 {{ margin: 0 0 8px; font-size: 28px; }}
    header p {{ margin: 0; opacity: .9; }}
    .layout {{ display: grid; grid-template-columns: 280px 1fr; gap: 24px; padding: 24px; }}
    nav {{ position: sticky; top: 24px; align-self: start; background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    nav a {{ display: block; padding: 8px 10px; color: var(--accent); text-decoration: none; border-radius: 8px; }}
    nav a:hover {{ background: var(--accent-soft); }}
    main {{ min-width: 0; }}
    section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 22px; margin-bottom: 18px; box-shadow: 0 6px 18px rgba(15, 23, 42, .05); }}
    h2 {{ margin: 0 0 10px; font-size: 20px; }}
    .meta {{ color: var(--muted); font-size: 13px; margin-bottom: 14px; }}
    .missing {{ color: var(--muted); font-style: italic; }}
    .warnings {{ background: var(--warning-bg); border-color: #f4d58d; color: var(--warning); }}
    pre {{ overflow: auto; background: var(--code-bg); color: var(--code-text); border-radius: 10px; padding: 14px; white-space: pre-wrap; word-break: break-word; }}
    .markdown {{ white-space: pre-wrap; }}
    .evidence-list {{ columns: 2; padding-left: 20px; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: 12px; }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      nav {{ position: static; }}
      .evidence-list {{ columns: 1; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Doctor link Diagnostic Package Browser</h1>
    <p>{html.escape(view.title)} · {html.escape(view.package_dir)}</p>
  </header>
  <div class="layout">
    <nav aria-label="Package sections">
      <strong>Sections</strong>
      {nav}
      <a href="#evidence-files">Evidence Files</a>
    </nav>
    <main>
      <section class="warnings">
        <h2>Package Warnings</h2>
        <ul>{warnings}</ul>
      </section>
      {''.join(body_sections)}
    </main>
  </div>
</body>
</html>
"""


def write_package_html(view: DiagnosticPackageView, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_package_html(view), encoding="utf-8")
    return output


def _render_text_section(anchor: str, section: PackageSection) -> str:
    if not section.exists:
        content = "<p class=\"missing\">Missing file.</p>"
    else:
        content = f'<div class="markdown">{html.escape(section.content)}</div>'
    return f"""
<section id="{html.escape(anchor)}">
  <h2>{html.escape(section.title)} <span class="badge">Markdown</span></h2>
  <div class="meta">{html.escape(section.path)}</div>
  {content}
</section>
"""


def _render_json_section(anchor: str, section: PackageJsonSection) -> str:
    if not section.exists:
        content = "<p class=\"missing\">Missing file.</p>"
    elif section.error:
        content = f"<p class=\"missing\">Invalid JSON: {html.escape(section.error)}</p>"
    else:
        payload = json.dumps(section.data, ensure_ascii=False, indent=2)
        content = f"<pre>{html.escape(payload)}</pre>"
    return f"""
<section id="{html.escape(anchor)}">
  <h2>{html.escape(section.title)} <span class="badge">JSON</span></h2>
  <div class="meta">{html.escape(section.path)}</div>
  {content}
</section>
"""


def _render_evidence_files(evidence_files: list[str]) -> str:
    if evidence_files:
        items = "".join(f"<li>{html.escape(item)}</li>" for item in evidence_files)
    else:
        items = "<li>No evidence files found.</li>"
    return f"""
<section id="evidence-files">
  <h2>Evidence Files</h2>
  <ul class="evidence-list">{items}</ul>
</section>
"""
