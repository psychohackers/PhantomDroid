"""
PhantomDroid — Report Generator Module
Author: Mr. Psycho | @the_psycho_of_hackers
"""

import json
import os
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
SEV_BADGE = {
    "CRITICAL": "#ff2d55",
    "HIGH":     "#ff6b35",
    "MEDIUM":   "#f7b731",
    "LOW":      "#2ecc71",
    "INFO":     "#74b9ff",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PhantomDroid — Security Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Rajdhani:wght@400;600;700&display=swap');
  :root {{
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --border: #2a2a3d;
    --accent: #8b5cf6;
    --accent2: #ec4899;
    --text: #e4e4f0;
    --dim: #6b6b8a;
    --crit: #ff2d55;
    --high: #ff6b35;
    --med: #f7b731;
    --low: #2ecc71;
    --info: #74b9ff;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    background-image:
      radial-gradient(ellipse at 10% 10%, rgba(139,92,246,0.12) 0%, transparent 50%),
      radial-gradient(ellipse at 90% 90%, rgba(236,72,153,0.10) 0%, transparent 50%);
  }}
  header {{
    background: linear-gradient(135deg, #1a0533 0%, #0d0d1a 50%, #1a0533 100%);
    border-bottom: 1px solid var(--accent);
    padding: 2rem 3rem;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 40px rgba(139,92,246,0.3);
  }}
  .logo {{
    font-size: 2.5rem; font-weight: 700; letter-spacing: 4px;
    background: linear-gradient(135deg, #8b5cf6, #ec4899, #f97316);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: none;
  }}
  .logo span {{ font-size: 1rem; color: var(--dim); display: block; font-family: 'JetBrains Mono'; margin-top: 4px; }}
  .meta {{ text-align: right; color: var(--dim); font-family: 'JetBrains Mono'; font-size: 0.8rem; }}
  .meta .target {{ color: var(--accent); font-size: 1rem; font-weight: 600; }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 2rem 2rem; }}
  .stats-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem; margin-bottom: 2rem;
  }}
  .stat-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem; text-align: center;
    transition: all 0.3s;
  }}
  .stat-card:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(139,92,246,0.2); }}
  .stat-num {{ font-size: 2.5rem; font-weight: 700; font-family: 'JetBrains Mono'; }}
  .stat-label {{ color: var(--dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
  .sev-crit {{ color: var(--crit); }} .sev-high {{ color: var(--high); }}
  .sev-med {{ color: var(--med); }} .sev-low {{ color: var(--low); }} .sev-info {{ color: var(--info); }}
  section {{ margin-bottom: 2.5rem; }}
  .section-title {{
    font-size: 1.3rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--accent);
    border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.5rem;
  }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{
    background: var(--surface2); color: var(--dim); text-transform: uppercase;
    font-size: 0.75rem; letter-spacing: 1px; padding: 0.75rem 1rem; text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  tbody tr {{
    border-bottom: 1px solid var(--border); transition: background 0.2s;
  }}
  tbody tr:hover {{ background: var(--surface2); }}
  td {{ padding: 0.8rem 1rem; font-family: 'JetBrains Mono'; font-size: 0.85rem; }}
  .badge {{
    display: inline-block; padding: 2px 10px; border-radius: 99px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
    font-family: 'JetBrains Mono';
  }}
  .finding-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.2rem; margin-bottom: 1rem;
    transition: all 0.2s;
  }}
  .finding-card:hover {{ border-color: var(--accent); }}
  .finding-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}
  .finding-name {{ font-size: 1rem; font-weight: 700; color: var(--text); }}
  .finding-detail {{ color: var(--dim); font-size: 0.85rem; margin-top: 0.4rem; font-family: 'JetBrains Mono'; }}
  .finding-fix {{ color: #2ecc71; font-size: 0.8rem; margin-top: 0.5rem; }}
  .cve-link {{ color: var(--accent); text-decoration: none; }}
  .cve-link:hover {{ color: var(--accent2); text-decoration: underline; }}
  .tag {{ display: inline-block; background: rgba(139,92,246,0.15); color: var(--accent);
           border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; margin: 2px; font-family: 'JetBrains Mono'; }}
  footer {{
    text-align: center; color: var(--dim); padding: 2rem;
    border-top: 1px solid var(--border); font-size: 0.8rem; font-family: 'JetBrains Mono';
  }}
  footer a {{ color: var(--accent); text-decoration: none; }}
  .disclaimer {{
    background: rgba(255,45,85,0.08); border: 1px solid rgba(255,45,85,0.3);
    border-radius: 8px; padding: 1rem; margin-bottom: 2rem;
    font-size: 0.85rem; color: #ff6b6b;
  }}
</style>
</head>
<body>
<header>
  <div>
    <div class="logo">👻 PhantomDroid<span>Advanced Android Pentesting Framework</span></div>
  </div>
  <div class="meta">
    <div class="target">{target}</div>
    <div>Generated: {timestamp}</div>
    <div>Report ID: {report_id}</div>
    <div>Author: Mr. Psycho | @the_psycho_of_hackers</div>
  </div>
</header>
<main>
  <div class="disclaimer">
    ⚠ This report is intended for authorized security testing only.
    Unauthorized use is illegal and unethical. Always obtain proper written permission before testing.
  </div>

  <div class="stats-grid">
    <div class="stat-card"><div class="stat-num sev-crit">{count_critical}</div><div class="stat-label">Critical</div></div>
    <div class="stat-card"><div class="stat-num sev-high">{count_high}</div><div class="stat-label">High</div></div>
    <div class="stat-card"><div class="stat-num sev-med">{count_medium}</div><div class="stat-label">Medium</div></div>
    <div class="stat-card"><div class="stat-num sev-low">{count_low}</div><div class="stat-label">Low</div></div>
    <div class="stat-card"><div class="stat-num" style="color:var(--accent)">{count_total}</div><div class="stat-label">Total Findings</div></div>
  </div>

  {sections}
</main>
<footer>
  <p>PhantomDroid &copy; 2026 | Author: <a href="https://instagram.com/the_psycho_of_hackers">Mr. Psycho</a> | For authorized use only</p>
</footer>
</body>
</html>
"""


def _badge(severity: str) -> str:
    color = SEV_BADGE.get(severity.upper(), "#74b9ff")
    return f'<span class="badge" style="background:{color}22;color:{color};border:1px solid {color}55">{severity.upper()}</span>'


def _remediations() -> dict:
    return {
        "Debuggable Application": "Set android:debuggable=false in AndroidManifest.xml and ensure ProGuard/R8 is enabled for release builds.",
        "Backup Enabled": "Set android:allowBackup=false in AndroidManifest.xml to prevent data extraction.",
        "No Network Security Config": "Define a network_security_config.xml that disables cleartext traffic.",
        "Hardcoded Secrets": "Use Android Keystore, encrypted SharedPreferences, or a secrets manager instead of hardcoded values.",
        "Exported Components": "Remove android:exported=true unless necessary; add permission checks to exported components.",
        "Task Hijacking": "Set android:taskAffinity='' and android:launchMode='singleTask' or use FLAG_ACTIVITY_NEW_DOCUMENT.",
        "SSL Pinning Bypassed": "Implement SSL pinning using OkHttp CertificatePinner or TrustKit; use multi-level pinning.",
    }


def generate_html_report(data: dict, output: str = "phantomdroid_report.html") -> str:
    """Generate a styled HTML report."""
    findings = data.get("findings", [])
    target   = data.get("target", "Unknown Target")
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = f"PD-{int(time.time())}"
    rems = _remediations()

    # Count severities
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in findings:
        sev = f.get("severity", "INFO").upper()
        counts[sev] = counts.get(sev, 0) + 1

    # Build findings section
    findings_html = '<section><div class="section-title">🚨 Security Findings</div>'
    sorted_findings = sorted(findings, key=lambda x: SEV_ORDER.get(x.get("severity", "INFO").upper(), 99))
    for f in sorted_findings:
        sev = f.get("severity", "INFO")
        name = f.get("name", "Unknown")
        detail = f.get("detail", "")
        cve = f.get("cve")
        fix = rems.get(name, "Review and apply the principle of least privilege.")
        cve_html = f' • <a class="cve-link" href="https://nvd.nist.gov/vuln/detail/{cve}" target="_blank">{cve}</a>' if cve else ""
        findings_html += f"""
        <div class="finding-card">
          <div class="finding-header">
            <div class="finding-name">{name}{cve_html}</div>
            {_badge(sev)}
          </div>
          <div class="finding-detail">{detail}</div>
          <div class="finding-fix">🛡 Remediation: {fix}</div>
        </div>"""
    findings_html += "</section>"

    # Permissions section
    perms = data.get("permissions", [])
    perms_html = ""
    if perms:
        perms_html = '<section><div class="section-title">🔐 Dangerous Permissions</div><table><thead><tr><th>Permission</th><th>Severity</th></tr></thead><tbody>'
        for p in perms:
            perms_html += f'<tr><td>{p["permission"]}</td><td>{_badge(p["severity"])}</td></tr>'
        perms_html += "</tbody></table></section>"

    # URLs section
    urls = data.get("urls", [])
    urls_html = ""
    if urls:
        urls_html = f'<section><div class="section-title">🌐 Embedded URLs ({len(urls)})</div><table><thead><tr><th>URL</th></tr></thead><tbody>'
        for u in urls[:30]:
            urls_html += f"<tr><td>{u}</td></tr>"
        urls_html += "</tbody></table></section>"

    # Secrets section
    secrets = data.get("secrets", [])
    secrets_html = ""
    if secrets:
        secrets_html = f'<section><div class="section-title">🔑 Hardcoded Secrets ({len(secrets)})</div><table><thead><tr><th>File</th><th>Type</th><th>Snippet</th></tr></thead><tbody>'
        for s in secrets[:20]:
            secrets_html += f"<tr><td>{s['file']}</td><td>{s['type']}</td><td>{s['snippet']}</td></tr>"
        secrets_html += "</tbody></table></section>"

    sections = findings_html + perms_html + secrets_html + urls_html

    html = HTML_TEMPLATE.format(
        target=target,
        timestamp=ts,
        report_id=report_id,
        count_critical=counts.get("CRITICAL", 0),
        count_high=counts.get("HIGH", 0),
        count_medium=counts.get("MEDIUM", 0),
        count_low=counts.get("LOW", 0),
        count_total=len(findings),
        sections=sections,
    )

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    console.print(f"[bold green]✓ HTML report saved:[/] {output}")
    return output


def generate_json_report(data: dict, output: str = "phantomdroid_report.json") -> str:
    """Generate a structured JSON report."""
    report = {
        "tool": "PhantomDroid",
        "author": "Mr. Psycho | @the_psycho_of_hackers",
        "generated": datetime.now().isoformat(),
        "target": data.get("target", "Unknown"),
        "summary": {
            "total_findings": len(data.get("findings", [])),
            "critical": sum(1 for f in data.get("findings", []) if f.get("severity") == "CRITICAL"),
            "high": sum(1 for f in data.get("findings", []) if f.get("severity") == "HIGH"),
            "medium": sum(1 for f in data.get("findings", []) if f.get("severity") == "MEDIUM"),
            "low": sum(1 for f in data.get("findings", []) if f.get("severity") == "LOW"),
        },
        "data": data,
    }
    with open(output, "w") as f:
        json.dump(report, f, indent=2, default=str)
    console.print(f"[bold green]✓ JSON report saved:[/] {output}")
    return output


def print_summary_table(data: dict):
    """Print a CLI summary table of findings."""
    findings = data.get("findings", [])
    SEV_COLOR = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green", "INFO": "cyan"}

    t = Table(title="[bold magenta]📋 PhantomDroid — Findings Summary[/]",
              box=box.DOUBLE_EDGE, border_style="magenta", header_style="bold cyan")
    t.add_column("#",        style="dim",    width=4)
    t.add_column("Finding",  style="white",  min_width=30)
    t.add_column("Severity", style="red",    width=12)
    t.add_column("CVE",      style="cyan",   width=18)
    t.add_column("Detail",   style="dim",    min_width=40)

    sorted_findings = sorted(findings, key=lambda x: SEV_ORDER.get(x.get("severity", "INFO").upper(), 99))
    for i, f in enumerate(sorted_findings, 1):
        sev = f.get("severity", "INFO")
        clr = SEV_COLOR.get(sev.upper(), "white")
        t.add_row(
            str(i),
            f.get("name", "Unknown"),
            f"[{clr}]{sev}[/]",
            f.get("cve") or "[dim]N/A[/]",
            f.get("detail", "")[:60],
        )
    console.print(t)
