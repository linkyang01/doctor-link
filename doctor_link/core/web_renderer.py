from __future__ import annotations

import html
import json
from pathlib import Path

from doctor_link.core.reports_indexer import DiagnosticPackageIndexItem, DiagnosticReportsIndex
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

    return _page(
        title=f"Doctor link - {view.title}",
        header_title="Doctor link Diagnostic Package Browser",
        header_subtitle=f"{view.title} · {view.package_dir}",
        nav=f"<strong>Sections</strong>{nav}<a href=\"#evidence-files\">Evidence Files</a>",
        main=f"""
      <section class="warnings">
        <h2>Package Warnings</h2>
        <ul>{warnings}</ul>
      </section>
      {''.join(body_sections)}
""",
    )


def render_reports_index_html(index: DiagnosticReportsIndex) -> str:
    """Render a DoctorReports index as a self-contained HTML page."""
    packages = sorted(index.packages, key=lambda item: item.updated_at or "", reverse=True)
    warning_items = "".join(f"<li>{html.escape(item)}</li>" for item in index.warnings) or "<li>None</li>"
    cards = "".join(_render_package_card(item) for item in packages) or "<p class=\"missing\">No diagnostic packages found.</p>"
    filters = _render_filter_panel(index)
    return _page(
        title="Doctor link - Reports Index",
        header_title="Doctor link Diagnostic Workbench",
        header_subtitle=f"{index.total_packages} package(s) · {index.reports_root}",
        nav="""
          <strong>Workbench</strong>
          <a href="#overview">Overview</a>
          <a href="#filters">Status Filters</a>
          <a href="#packages">Packages</a>
          <a href="#warnings">Warnings</a>
        """,
        main=f"""
      <section id="overview">
        <h2>Reports Overview</h2>
        <div class="stats">
          <div><strong>{index.total_packages}</strong><span>Total packages</span></div>
          <div><strong>{_count_with_assertions(index)}</strong><span>With user assertions</span></div>
          <div><strong>{_count_verification_blockers(index)}</strong><span>Verification blockers</span></div>
          <div><strong>{_count_redaction_warnings(index)}</strong><span>Redaction warnings</span></div>
        </div>
      </section>
      <section id="filters">
        <h2>Status Filters</h2>
        {filters}
      </section>
      <section id="packages">
        <h2>Diagnostic Packages</h2>
        <div class="cards">{cards}</div>
      </section>
      <section id="warnings" class="warnings">
        <h2>Index Warnings</h2>
        <ul>{warning_items}</ul>
      </section>
""",
    )


def write_package_html(view: DiagnosticPackageView, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_package_html(view), encoding="utf-8")
    return output


def write_reports_index_html(index: DiagnosticReportsIndex, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_reports_index_html(index), encoding="utf-8")
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


def _render_package_card(item: DiagnosticPackageIndexItem) -> str:
    warning_list = "".join(f"<li>{html.escape(warning)}</li>" for warning in item.warnings[:4])
    if item.warning_count > 4:
        warning_list += f"<li>+ {item.warning_count - 4} more warning(s)</li>"
    warnings = f"<ul class=\"compact\">{warning_list}</ul>" if warning_list else "<p class=\"muted\">No package warnings.</p>"
    detail_href = f"packages/{html.escape(item.relative_path)}/index.html"
    return f"""
<article class="card" data-verification="{html.escape(item.verification_status)}" data-assertions="{item.user_assertion_count}" data-redaction="{html.escape(item.redaction_status)}">
  <div class="card-head">
    <h3>{html.escape(item.name)}</h3>
    <a class="open" href="{detail_href}">Open</a>
  </div>
  <p class="muted">{html.escape(item.project)}</p>
  <p>{html.escape(item.summary)}</p>
  <div class="badges">
    {_status_badge('verification', item.verification_status)}
    {_status_badge('redaction', item.redaction_status)}
    {_status_badge('export', item.package_export_status)}
  </div>
  <dl class="metrics">
    <div><dt>Evidence</dt><dd>{item.evidence_count}</dd></div>
    <div><dt>Timeline</dt><dd>{item.timeline_count}</dd></div>
    <div><dt>Assertions</dt><dd>{item.user_assertion_count}</dd></div>
    <div><dt>Warnings</dt><dd>{item.warning_count}</dd></div>
  </dl>
  <p class="meta">Updated: {html.escape(item.updated_at or 'unknown')}</p>
  {warnings}
</article>
"""


def _render_filter_panel(index: DiagnosticReportsIndex) -> str:
    verification = sorted({item.verification_status for item in index.packages})
    redaction = sorted({item.redaction_status for item in index.packages})
    verification_items = "".join(f"<li><span class=\"badge\">{html.escape(status)}</span> {_count_status(index, 'verification_status', status)}</li>" for status in verification)
    redaction_items = "".join(f"<li><span class=\"badge\">{html.escape(status)}</span> {_count_status(index, 'redaction_status', status)}</li>" for status in redaction)
    return f"""
<div class="filter-grid">
  <div>
    <h3>Verification</h3>
    <ul class="compact">{verification_items or '<li>None</li>'}</ul>
  </div>
  <div>
    <h3>Redaction</h3>
    <ul class="compact">{redaction_items or '<li>None</li>'}</ul>
  </div>
  <div>
    <h3>User Assertions</h3>
    <ul class="compact">
      <li><span class="badge">with assertions</span> {_count_with_assertions(index)}</li>
      <li><span class="badge">without assertions</span> {index.total_packages - _count_with_assertions(index)}</li>
    </ul>
  </div>
</div>
"""


def _page(title: str, header_title: str, header_subtitle: str, nav: str, main: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
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
      --danger: #8f1d1d;
      --danger-bg: #ffe8e8;
      --success: #17633a;
      --success-bg: #e6f6ee;
      --code-bg: #0f172a;
      --code-text: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--text); line-height: 1.55; }}
    header {{ padding: 28px 36px; background: linear-gradient(135deg, #1f4f86, #4e79ad); color: #fff; }}
    header h1 {{ margin: 0 0 8px; font-size: 28px; }}
    header p {{ margin: 0; opacity: .9; }}
    .layout {{ display: grid; grid-template-columns: 280px 1fr; gap: 24px; padding: 24px; }}
    nav {{ position: sticky; top: 24px; align-self: start; background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    nav a {{ display: block; padding: 8px 10px; color: var(--accent); text-decoration: none; border-radius: 8px; }}
    nav a:hover {{ background: var(--accent-soft); }}
    main {{ min-width: 0; }}
    section, .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 22px; margin-bottom: 18px; box-shadow: 0 6px 18px rgba(15, 23, 42, .05); }}
    h2 {{ margin: 0 0 10px; font-size: 20px; }}
    h3 {{ margin: 0 0 8px; font-size: 17px; }}
    .meta, .muted {{ color: var(--muted); font-size: 13px; }}
    .missing {{ color: var(--muted); font-style: italic; }}
    .warnings {{ background: var(--warning-bg); border-color: #f4d58d; color: var(--warning); }}
    pre {{ overflow: auto; background: var(--code-bg); color: var(--code-text); border-radius: 10px; padding: 14px; white-space: pre-wrap; word-break: break-word; }}
    .markdown {{ white-space: pre-wrap; }}
    .evidence-list {{ columns: 2; padding-left: 20px; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: 12px; }}
    .badge.danger {{ background: var(--danger-bg); color: var(--danger); }}
    .badge.success {{ background: var(--success-bg); color: var(--success); }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
    .card {{ margin: 0; }}
    .card-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    .open {{ color: #fff; background: var(--accent); padding: 7px 10px; border-radius: 8px; text-decoration: none; font-size: 13px; }}
    .badges {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 12px 0; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 14px 0; }}
    .metrics div, .stats div {{ background: var(--accent-soft); border-radius: 10px; padding: 10px; }}
    .metrics dt, .stats span {{ color: var(--muted); font-size: 12px; }}
    .metrics dd {{ margin: 0; font-weight: 700; }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }}
    .stats strong {{ display: block; font-size: 28px; }}
    .filter-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
    .compact {{ padding-left: 18px; margin: 8px 0 0; }}
    @media (max-width: 900px) {{ .layout {{ grid-template-columns: 1fr; }} nav {{ position: static; }} .evidence-list {{ columns: 1; }} .metrics {{ grid-template-columns: repeat(2, 1fr); }} }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(header_title)}</h1>
    <p>{html.escape(header_subtitle)}</p>
  </header>
  <div class="layout">
    <nav aria-label="Navigation">
      {nav}
    </nav>
    <main>
      {main}
    </main>
  </div>
</body>
</html>
"""


def _status_badge(kind: str, status: str) -> str:
    css = ""
    if status in {"not_verified", "missing", "missing_evidence", "invalid", "invalid_manifest"}:
        css = " danger"
    elif status in {"candidate_verified", "ready", "redacted", "clean", "exported"}:
        css = " success"
    return f'<span class="badge{css}">{html.escape(kind)}: {html.escape(status)}</span>'


def _count_status(index: DiagnosticReportsIndex, attr: str, value: str) -> int:
    return sum(1 for item in index.packages if getattr(item, attr) == value)


def _count_with_assertions(index: DiagnosticReportsIndex) -> int:
    return sum(1 for item in index.packages if item.user_assertion_count > 0)


def _count_verification_blockers(index: DiagnosticReportsIndex) -> int:
    return sum(1 for item in index.packages if item.verification_status in {"missing", "missing_evidence", "not_verified"})


def _count_redaction_warnings(index: DiagnosticReportsIndex) -> int:
    return sum(1 for item in index.packages if item.redaction_status in {"missing", "invalid"})
