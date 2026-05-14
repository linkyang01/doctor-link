from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from doctor_link.core.web_package_reader import DiagnosticPackageView, EvidencePreview


def write_package_detail_html(view: DiagnosticPackageView, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_package_detail_html(view), encoding="utf-8")
    return output


def render_package_detail_html(view: DiagnosticPackageView) -> str:
    warnings = _items(view.warnings) or "<li>None</li>"
    return _page(
        title=f"Doctor link - {view.title}",
        subtitle=f"{view.title} · {view.package_dir}",
        main=f"""
<section class="warnings"><h2>Package Warnings</h2><ul>{warnings}</ul></section>
{_overview(view)}
{_timeline(view)}
{_evidence(view)}
{_assertions(view)}
{_ai_task(view)}
{_verification(view)}
{_comparison(view)}
{_redaction(view)}
{_manifest(view)}
{_raw_files(view)}
""",
    )


def _overview(view: DiagnosticPackageView) -> str:
    report = _dict(view.json_data("doctor_report"))
    verification = _dict(view.json_data("verification_result"))
    assertions = _list(view.json_data("user_assertions"))
    redaction = _dict(view.json_data("redaction_report_json"))
    summary = _first([report.get("summary"), _nested(report, ["event", "summary"]), view.text("summary")])
    project = _first([report.get("project"), _nested(report, ["event", "project"]), "Unknown project"])
    status = str(verification.get("status") or _nested(report, ["verification_result", "status"]) or "missing")
    redaction_status = "missing" if not view.text("redaction_report") and not redaction else "present"
    return f"""
<section id="overview"><h2>Overview</h2>
<p>{html.escape(summary[:700] or 'No summary available.')}</p>
<div class="stats">
<div><strong>{html.escape(project)}</strong><span>Project</span></div>
<div><strong>{len(view.evidence_previews)}</strong><span>Evidence files</span></div>
<div><strong>{len(assertions)}</strong><span>User assertions</span></div>
<div><strong>{html.escape(status)}</strong><span>Verification</span></div>
<div><strong>{html.escape(redaction_status)}</strong><span>Redaction</span></div>
</div></section>
"""


def _timeline(view: DiagnosticPackageView) -> str:
    report = _dict(view.json_data("doctor_report"))
    steps = _list(report.get("timeline"))
    if steps:
        content = "".join(_timeline_step(step) for step in steps)
    elif view.text("timeline"):
        content = f"<div class=\"markdown\">{html.escape(view.text('timeline'))}</div>"
    else:
        content = "<p class=\"missing\">No timeline found.</p>"
    return f"<section id=\"timeline\"><h2>Timeline</h2><p class=\"muted\">Review failed, unknown, and evidence-linked steps first.</p>{content}</section>"


def _timeline_step(step: Any) -> str:
    data = _dict(step)
    title = str(data.get("title") or data.get("step") or data.get("action") or "Timeline step")
    status = str(data.get("status") or data.get("result") or "unknown")
    cls = _status_class(status)
    return f"""
<article class="mini-card {cls}"><h3>{html.escape(title)} <span class="badge {cls}">{html.escape(status)}</span></h3>
<pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2))}</pre></article>
"""


def _evidence(view: DiagnosticPackageView) -> str:
    if not view.evidence_previews:
        return "<section id=\"evidence\"><h2>Evidence</h2><p class=\"missing\">No evidence files found.</p></section>"
    groups: dict[str, list[EvidencePreview]] = {}
    for item in view.evidence_previews:
        groups.setdefault(item.evidence_type, []).append(item)
    body = "".join(f"<h3>{html.escape(name)}</h3><div class=\"grid\">{''.join(_evidence_item(p) for p in previews)}</div>" for name, previews in sorted(groups.items()))
    return f"<section id=\"evidence\"><h2>Evidence</h2><p class=\"muted\">Text evidence is previewed locally. Unknown binary attachments are listed but not embedded.</p>{body}</section>"


def _evidence_item(item: EvidencePreview) -> str:
    ids = ", ".join(item.evidence_ids) if item.evidence_ids else "not linked"
    risk = "danger" if item.redaction_status == "no_redaction_report" and item.evidence_type in {"logs", "command-output"} else ""
    if item.content:
        content = _format_json(item.content) if item.preview_kind == "json" else item.content
        preview = f"<pre>{html.escape(content)}</pre>"
    else:
        preview = f"<p class=\"missing\">{html.escape(item.warning or 'No inline preview.')}</p>"
    truncated = "<p class=\"muted\">Preview truncated.</p>" if item.truncated else ""
    return f"""
<article class="mini-card"><h4>{html.escape(item.path)}</h4>
<div class="badges"><span class="badge">{html.escape(item.preview_kind)}</span><span class="badge {risk}">redaction: {html.escape(item.redaction_status)}</span></div>
<p class="meta">{item.size_bytes} bytes · evidence IDs: {html.escape(ids)}</p>{preview}{truncated}</article>
"""


def _assertions(view: DiagnosticPackageView) -> str:
    assertions = _list(view.json_data("user_assertions"))
    if not assertions:
        body = "<p class=\"missing\">No human-confirmed assertions found.</p>"
    else:
        body = "".join(_assertion(item) for item in assertions)
    return f"<section id=\"assertions\"><h2>User Assertions</h2><p class=\"muted\">Human-confirmed issues are first-class diagnostic signals.</p>{body}</section>"


def _assertion(item: Any) -> str:
    data = _dict(item)
    statement = str(data.get("user_statement") or data.get("statement") or "User assertion")
    expected = str(data.get("expected_behavior") or data.get("expected") or "Not provided")
    actual = str(data.get("actual_behavior") or data.get("actual") or "Not provided")
    why = str(data.get("why_user_thinks_it_is_wrong") or data.get("why") or "Not provided")
    return f"""
<article class="assertion"><h3>{html.escape(statement)}</h3>
<div class="kv"><div><strong>Expected</strong><span>{html.escape(expected)}</span></div><div><strong>Actual</strong><span>{html.escape(actual)}</span></div><div><strong>Why</strong><span>{html.escape(why)}</span></div></div></article>
"""


def _ai_task(view: DiagnosticPackageView) -> str:
    task = view.text("ai_task")
    boundary = view.text("investigation_boundary")
    has_warning = "The human user has confirmed this as the problem" in task
    warning = "Human assertion warning present" if has_warning else "Human assertion warning not detected"
    cls = "success" if has_warning else "danger"
    return f"""
<section id="ai-task"><h2>AI Task <span class="badge {cls}">{html.escape(warning)}</span></h2>
<h3>Task</h3><div class="markdown">{html.escape(task or 'Missing ai-task.md')}</div>
<h3>Investigation Boundary</h3><div class="markdown">{html.escape(boundary or 'Missing investigation-boundary.md')}</div></section>
"""


def _verification(view: DiagnosticPackageView) -> str:
    result = _dict(view.json_data("verification_result"))
    status = str(result.get("status") or "missing")
    missing = _list(result.get("missing_evidence"))
    rerun = _list(result.get("tests_to_rerun"))
    commands = _list(result.get("next_commands"))
    cls = _status_class(status)
    return f"""
<section id="verification"><h2>Verification Workbench <span class="badge {cls}">{html.escape(status)}</span></h2>
<p class="muted">The UI must not claim a fix is complete when evidence is missing.</p>
<div class="stats"><div><strong>{len(missing)}</strong><span>Missing evidence</span></div><div><strong>{len(rerun)}</strong><span>Tests to rerun</span></div><div><strong>{len(commands)}</strong><span>Next commands</span></div></div>
{_list_block('Missing Evidence', missing)}{_list_block('Tests To Rerun', rerun)}{_list_block('Suggested Next Commands', commands)}
<h3>Checklist</h3><div class="markdown">{html.escape(view.text('verification_checklist') or 'Missing fix-verification-checklist.md')}</div>
<h3>Plan</h3><div class="markdown">{html.escape(view.text('verification_plan') or 'Missing verification-plan.md')}</div>
<h3>Raw Result</h3><pre>{html.escape(json.dumps(result, ensure_ascii=False, indent=2) if result else 'Missing verification-result.json')}</pre></section>
"""


def _comparison(view: DiagnosticPackageView) -> str:
    data = _dict(view.json_data("report_comparison_json"))
    markdown = view.text("report_comparison")
    if not data and not markdown:
        return "<section id=\"comparison\"><h2>Before / After Comparison</h2><p class=\"missing\">No comparison found.</p><pre>doctor-link compare before.json after.json --package-dir &lt;package_dir&gt;</pre></section>"
    buckets = []
    for key in ["resolved", "unresolved", "new", "changed", "resolved_signals", "unresolved_signals", "new_signals", "changed_signals"]:
        value = data.get(key)
        if isinstance(value, list):
            buckets.append(f"<div><strong>{len(value)}</strong><span>{html.escape(key.replace('_', ' '))}</span></div>")
    stats = f"<div class=\"stats\">{''.join(buckets)}</div>" if buckets else ""
    return f"<section id=\"comparison\"><h2>Before / After Comparison</h2>{stats}<div class=\"markdown\">{html.escape(markdown)}</div><pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2) if data else 'Missing report-comparison.json')}</pre></section>"


def _redaction(view: DiagnosticPackageView) -> str:
    data = _dict(view.json_data("redaction_report_json"))
    total = data.get("total_replacements", "missing") if data else "missing"
    cls = "danger" if total == "missing" else "success"
    return f"<section id=\"redaction\"><h2>Redaction <span class=\"badge {cls}\">replacements: {html.escape(str(total))}</span></h2><p class=\"muted\">Review sensitive text evidence before external sharing.</p><div class=\"markdown\">{html.escape(view.text('redaction_report') or 'Missing redaction-report.md')}</div><pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2) if data else 'Missing redaction-report.json')}</pre></section>"


def _manifest(view: DiagnosticPackageView) -> str:
    data = _dict(view.json_data("manifest"))
    included = _list(data.get("included_files"))
    skipped = _list(data.get("skipped_files"))
    return f"<section id=\"manifest\"><h2>Manifest / Export</h2><div class=\"stats\"><div><strong>{len(included)}</strong><span>Included</span></div><div><strong>{len(skipped)}</strong><span>Skipped</span></div></div><div class=\"markdown\">{html.escape(view.text('package_readme') or 'Missing package-readme.md')}</div><pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2) if data else 'Missing manifest.json')}</pre></section>"


def _raw_files(view: DiagnosticPackageView) -> str:
    files = _items(view.evidence_files) or "<li>No evidence files found.</li>"
    return f"<section id=\"raw\"><h2>Raw Evidence File List</h2><ul>{files}</ul></section>"


def _page(title: str, subtitle: str, main: str) -> str:
    nav = """<strong>Package</strong><a href="#overview">Overview</a><a href="#timeline">Timeline</a><a href="#evidence">Evidence</a><a href="#assertions">Assertions</a><a href="#ai-task">AI Task</a><a href="#verification">Verification</a><a href="#comparison">Comparison</a><a href="#redaction">Redaction</a><a href="#manifest">Manifest</a><a href="#raw">Raw Files</a>"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><style>
:root{{--bg:#f4f7fb;--panel:#fff;--text:#142033;--muted:#667085;--line:#d8e0ea;--accent:#315f9f;--accent-soft:#e7eef8;--warning:#8a5a00;--warning-bg:#fff6df;--danger:#8f1d1d;--danger-bg:#ffe8e8;--success:#17633a;--success-bg:#e6f6ee;--code-bg:#0f172a;--code-text:#e5e7eb}}*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text);line-height:1.55}}header{{padding:28px 36px;background:linear-gradient(135deg,#1f4f86,#4e79ad);color:#fff}}header h1{{margin:0 0 8px;font-size:28px}}header p{{margin:0;opacity:.9}}.layout{{display:grid;grid-template-columns:280px 1fr;gap:24px;padding:24px}}nav{{position:sticky;top:24px;align-self:start;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px}}nav a{{display:block;padding:8px 10px;color:var(--accent);text-decoration:none;border-radius:8px}}nav a:hover{{background:var(--accent-soft)}}section,.mini-card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:18px;box-shadow:0 6px 18px rgba(15,23,42,.05)}}h2{{margin:0 0 10px;font-size:20px}}h3{{margin:18px 0 8px;font-size:17px}}h4{{margin:0 0 8px;font-size:14px}}.meta,.muted{{color:var(--muted);font-size:13px}}.missing{{color:var(--muted);font-style:italic}}.warnings{{background:var(--warning-bg);border-color:#f4d58d;color:var(--warning)}}pre{{overflow:auto;background:var(--code-bg);color:var(--code-text);border-radius:10px;padding:14px;white-space:pre-wrap;word-break:break-word;max-height:420px}}.markdown{{white-space:pre-wrap}}.badge{{display:inline-block;padding:2px 8px;border-radius:999px;background:var(--accent-soft);color:var(--accent);font-size:12px}}.badge.danger,.mini-card.danger{{background:var(--danger-bg);color:var(--danger)}}.badge.success,.mini-card.success{{background:var(--success-bg);color:var(--success)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}.stats,.kv{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin:14px 0}}.stats div,.kv div{{background:var(--accent-soft);border-radius:10px;padding:10px}}.stats strong,.kv strong{{display:block}}.stats span,.kv span{{color:var(--muted);font-size:12px}}.badges{{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}}@media(max-width:900px){{.layout{{grid-template-columns:1fr}}nav{{position:static}}}}
</style></head><body><header><h1>Doctor link Diagnostic Package Workbench</h1><p>{html.escape(subtitle)}</p></header><div class="layout"><nav>{nav}</nav><main>{main}</main></div></body></html>"""


def _items(values: list[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in values)


def _list_block(title: str, values: list[Any]) -> str:
    return f"<h3>{html.escape(title)}</h3><ul>{_items(values) or '<li>None</li>'}</ul>"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ["assertions", "user_assertions", "items", "missing_evidence", "tests_to_rerun", "next_commands"]:
            if isinstance(value.get(key), list):
                return value[key]
    return []


def _nested(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first(values: list[Any]) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _format_json(text: str) -> str:
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return text


def _status_class(status: str) -> str:
    if status in {"missing", "missing_evidence", "not_verified", "failed", "error", "unknown"}:
        return "danger"
    if status in {"candidate_verified", "ready", "passed", "success"}:
        return "success"
    return ""
