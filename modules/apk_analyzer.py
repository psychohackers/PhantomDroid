"""
PhantomDroid — APK Static Analyzer Module
Author: Mr. Psycho | @the_psycho_of_hackers
"""

import zipfile
import os
import re
import hashlib
import struct
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# ─── Dangerous Android Permissions ────────────────────────────────────────────
DANGEROUS_PERMS = {
    "android.permission.READ_CONTACTS":          "HIGH",
    "android.permission.WRITE_CONTACTS":         "HIGH",
    "android.permission.READ_SMS":               "HIGH",
    "android.permission.SEND_SMS":               "HIGH",
    "android.permission.RECEIVE_SMS":            "HIGH",
    "android.permission.READ_CALL_LOG":          "HIGH",
    "android.permission.WRITE_CALL_LOG":         "HIGH",
    "android.permission.RECORD_AUDIO":           "HIGH",
    "android.permission.CAMERA":                 "MEDIUM",
    "android.permission.ACCESS_FINE_LOCATION":   "HIGH",
    "android.permission.ACCESS_COARSE_LOCATION": "MEDIUM",
    "android.permission.READ_EXTERNAL_STORAGE":  "MEDIUM",
    "android.permission.WRITE_EXTERNAL_STORAGE": "MEDIUM",
    "android.permission.PROCESS_OUTGOING_CALLS": "HIGH",
    "android.permission.INTERNET":               "LOW",
    "android.permission.CHANGE_WIFI_STATE":      "MEDIUM",
    "android.permission.BLUETOOTH":              "LOW",
    "android.permission.NFC":                    "LOW",
    "android.permission.GET_ACCOUNTS":           "MEDIUM",
    "android.permission.USE_CREDENTIALS":        "HIGH",
    "android.permission.READ_PHONE_STATE":        "HIGH",
    "android.permission.CALL_PHONE":             "HIGH",
    "android.permission.RECEIVE_BOOT_COMPLETED": "MEDIUM",
    "android.permission.SYSTEM_ALERT_WINDOW":    "HIGH",
    "android.permission.INSTALL_PACKAGES":       "CRITICAL",
    "android.permission.DELETE_PACKAGES":        "CRITICAL",
    "android.permission.BIND_DEVICE_ADMIN":      "CRITICAL",
    "android.permission.MOUNT_UNMOUNT_FILESYSTEMS": "HIGH",
    "android.permission.MASTER_CLEAR":           "CRITICAL",
}

# ─── Secret patterns to search in DEX/resources ───────────────────────────────
SECRET_PATTERNS = [
    (r"(?i)(api_?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{16,})", "API Key"),
    (r"(?i)(secret|password|passwd|pwd)\s*[=:]\s*['\"]?(\S{8,})", "Secret/Password"),
    (r"(?i)(access_?token|auth_?token)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]{16,})", "Auth Token"),
    (r"(?i)(aws_?access_?key_?id)\s*[=:]\s*['\"]?(AKIA[0-9A-Z]{16})", "AWS Access Key"),
    (r"(?i)(aws_?secret)\s*[=:]\s*['\"]?([a-zA-Z0-9/+=]{40})", "AWS Secret"),
    (r"(?i)(BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY)", "Private Key"),
    (r"(?i)(client_?id|client_?secret)\s*[=:]\s*['\"]?(\S{8,})", "OAuth Credential"),
    (r"(?i)(firebase[a-zA-Z_]*)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]{16,})", "Firebase Config"),
    (r"(?i)google_maps_key\s*[=:]\s*['\"]?(AIza[0-9A-Za-z\-_]{35})", "Google Maps Key"),
    (r"(?i)(jdbc:[a-z]+://\S+)", "Database URL"),
    (r"https?://(?:\S+:)?\S+@[\w\.\-]+", "URL with Credentials"),
]


def _file_hash(path: str) -> dict:
    result = {}
    for algo in ["md5", "sha1", "sha256"]:
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        result[algo.upper()] = h.hexdigest()
    return result


def _parse_manifest_permissions(manifest_xml: str) -> list:
    return re.findall(r'android\.permission\.\w+', manifest_xml)


def _extract_strings_from_bytes(data: bytes) -> list:
    """Extract printable ASCII strings from binary data."""
    result = []
    current = []
    for byte in data:
        if 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= 8:
                result.append("".join(current))
            current = []
    return result


def analyze_apk(apk_path: str) -> dict:
    """Full static analysis of an APK file."""
    findings = {
        "path": apk_path,
        "hashes": {},
        "manifest": {},
        "permissions": [],
        "dangerous_permissions": [],
        "exported_components": {"activities": [], "services": [], "receivers": [], "providers": []},
        "secrets": [],
        "urls": [],
        "ips": [],
        "libs": [],
        "certificate": {},
        "obfuscated": False,
        "backup_enabled": False,
        "debuggable": False,
        "network_security_config": False,
        "vulnerabilities": [],
    }

    if not os.path.isfile(apk_path):
        console.print(f"[red]✗ File not found: {apk_path}[/]")
        return findings

    console.print(Panel(f"[bold cyan]Analyzing:[/] {apk_path}", border_style="magenta"))

    # ── File hashes ──────────────────────────────────────────────────────────
    with console.status("[cyan]Computing hashes...[/]"):
        findings["hashes"] = _file_hash(apk_path)

    h_table = Table(title="File Hashes", box=box.SIMPLE, border_style="dim")
    h_table.add_column("Algorithm", style="cyan")
    h_table.add_column("Hash", style="white")
    for algo, val in findings["hashes"].items():
        h_table.add_row(algo, val)
    console.print(h_table)

    try:
        zf = zipfile.ZipFile(apk_path, "r")
    except zipfile.BadZipFile:
        console.print("[red]✗ Not a valid APK (ZIP) file.[/]")
        return findings

    namelist = zf.namelist()
    console.print(f"[dim]APK contains [bold]{len(namelist)}[/] entries.[/]")

    # ── Manifest parsing ─────────────────────────────────────────────────────
    if "AndroidManifest.xml" in namelist:
        with console.status("[cyan]Parsing AndroidManifest.xml...[/]"):
            raw_manifest = zf.read("AndroidManifest.xml")
            # Try to decode as text (non-binary APKs or already decoded)
            try:
                manifest_text = raw_manifest.decode("utf-8", errors="ignore")
            except Exception:
                manifest_text = raw_manifest.decode("latin-1", errors="ignore")

            # Parse flags
            findings["debuggable"] = "android:debuggable=\"true\"" in manifest_text or \
                                     b'debuggable' in raw_manifest
            findings["backup_enabled"] = "android:allowBackup=\"true\"" in manifest_text or \
                                         b'allowBackup' in raw_manifest

            # Extract all permissions
            perms = _parse_manifest_permissions(manifest_text)
            # Also scan binary bytes
            perms += re.findall(rb'android\.permission\.(\w+)', raw_manifest)
            perms = list(set([p if isinstance(p, str) else f"android.permission.{p.decode()}" for p in perms]))
            findings["permissions"] = perms

            for perm in perms:
                full = perm if perm.startswith("android.permission.") else perm
                sev = DANGEROUS_PERMS.get(full)
                if sev:
                    findings["dangerous_permissions"].append({"permission": full, "severity": sev})

            # Exported components
            for comp_type, tag in [("activities", "activity"), ("services", "service"),
                                    ("receivers", "receiver"), ("providers", "provider")]:
                exported = re.findall(
                    rf'<{tag}[^>]*android:name="([^"]+)"[^>]*android:exported="true"', manifest_text)
                findings["exported_components"][comp_type] = exported

            # Network security config
            findings["network_security_config"] = "network_security_config" in manifest_text

            # Package & SDK
            pkg = re.search(r'package="([^"]+)"', manifest_text)
            min_sdk = re.search(r'android:minSdkVersion="(\d+)"', manifest_text)
            target_sdk = re.search(r'android:targetSdkVersion="(\d+)"', manifest_text)
            findings["manifest"] = {
                "package": pkg.group(1) if pkg else "Unknown",
                "min_sdk": min_sdk.group(1) if min_sdk else "Unknown",
                "target_sdk": target_sdk.group(1) if target_sdk else "Unknown",
            }

    # ── Native libraries ─────────────────────────────────────────────────────
    libs = [n for n in namelist if n.endswith(".so")]
    findings["libs"] = libs

    # ── Secret scanning across all files ────────────────────────────────────
    with console.status("[cyan]Scanning for hardcoded secrets...[/]"):
        for entry in namelist:
            if any(entry.endswith(ext) for ext in [".dex", ".xml", ".json", ".properties", ".js", ".html", ".txt"]):
                try:
                    content = zf.read(entry).decode("utf-8", errors="ignore")
                    for pattern, label in SECRET_PATTERNS:
                        for match in re.finditer(pattern, content):
                            findings["secrets"].append({
                                "file": entry,
                                "type": label,
                                "snippet": match.group(0)[:80],
                                "severity": "HIGH",
                            })
                except Exception:
                    pass

    # ── URL & IP extraction ──────────────────────────────────────────────────
    with console.status("[cyan]Extracting URLs and IPs...[/]"):
        all_text = ""
        for entry in namelist:
            try:
                all_text += zf.read(entry).decode("utf-8", errors="ignore")
            except Exception:
                pass

        urls = list(set(re.findall(r'https?://[^\s\'"<>{}\[\]]+', all_text)))
        ips = list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', all_text)))
        findings["urls"] = [u for u in urls if len(u) < 200][:50]
        findings["ips"] = [ip for ip in ips if not ip.startswith("0.") and ip != "127.0.0.1"][:20]

    # ── Obfuscation detection ────────────────────────────────────────────────
    dex_entries = [n for n in namelist if n.endswith(".dex")]
    if dex_entries:
        dex_content = zf.read(dex_entries[0]).decode("utf-8", errors="ignore")
        short_class_ratio = len(re.findall(r'\b[a-z]{1,2}\b', dex_content)) / max(len(dex_content), 1)
        findings["obfuscated"] = short_class_ratio > 0.01

    zf.close()

    # ── Vulnerability heuristics ─────────────────────────────────────────────
    if findings["debuggable"]:
        findings["vulnerabilities"].append({
            "name": "Debuggable Application",
            "severity": "HIGH",
            "detail": "android:debuggable=true allows attaching debugger, code extraction.",
            "cve": None,
        })
    if findings["backup_enabled"]:
        findings["vulnerabilities"].append({
            "name": "Backup Enabled",
            "severity": "MEDIUM",
            "detail": "android:allowBackup=true allows full data extraction via adb backup.",
            "cve": None,
        })
    if not findings["network_security_config"]:
        findings["vulnerabilities"].append({
            "name": "No Network Security Config",
            "severity": "MEDIUM",
            "detail": "App may allow cleartext HTTP traffic (no network_security_config defined).",
            "cve": None,
        })
    total_exported = sum(len(v) for v in findings["exported_components"].values())
    if total_exported > 0:
        findings["vulnerabilities"].append({
            "name": f"Exported Components ({total_exported})",
            "severity": "HIGH",
            "detail": f"Exported components may be exploited by other apps without permission.",
            "cve": None,
        })
    if findings["secrets"]:
        findings["vulnerabilities"].append({
            "name": f"Hardcoded Secrets ({len(findings['secrets'])})",
            "severity": "CRITICAL",
            "detail": "Hardcoded API keys, passwords, or tokens found in APK.",
            "cve": None,
        })

    _print_analysis_results(findings)
    return findings


def _print_analysis_results(f: dict):
    """Pretty-print analysis results."""
    SEV_COLOR = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "cyan", "INFO": "dim"}

    console.print("\n[bold magenta]══════════ APK ANALYSIS RESULTS ══════════[/]")

    # Manifest info
    m = f.get("manifest", {})
    console.print(Panel(
        f"  Package: [bold cyan]{m.get('package', 'N/A')}[/]\n"
        f"  Min SDK: [yellow]{m.get('min_sdk', 'N/A')}[/]  Target SDK: [yellow]{m.get('target_sdk', 'N/A')}[/]\n"
        f"  Debuggable: {'[bold red]YES ⚠[/]' if f['debuggable'] else '[green]No[/]'}   "
        f"Backup Enabled: {'[bold red]YES ⚠[/]' if f['backup_enabled'] else '[green]No[/]'}   "
        f"Obfuscated: {'[green]Yes[/]' if f['obfuscated'] else '[yellow]No[/]'}",
        title="[bold]App Info[/]", border_style="cyan"))

    # Dangerous permissions
    if f["dangerous_permissions"]:
        pt = Table(title=f"⚠ Dangerous Permissions ({len(f['dangerous_permissions'])})",
                   box=box.SIMPLE, border_style="red", header_style="bold red")
        pt.add_column("Permission", style="white")
        pt.add_column("Severity", style="red")
        for p in f["dangerous_permissions"]:
            sev = p["severity"]
            pt.add_row(p["permission"], f"[{SEV_COLOR.get(sev, 'white')}]{sev}[/]")
        console.print(pt)

    # Exported components
    for comp_type, items in f["exported_components"].items():
        if items:
            et = Table(title=f"📤 Exported {comp_type.title()} ({len(items)})",
                       box=box.SIMPLE, border_style="yellow", header_style="bold yellow")
            et.add_column("Component", style="white")
            for item in items:
                et.add_row(item)
            console.print(et)

    # Secrets
    if f["secrets"]:
        st = Table(title=f"🔑 Hardcoded Secrets ({len(f['secrets'])})",
                   box=box.SIMPLE, border_style="red", header_style="bold red")
        st.add_column("File", style="dim")
        st.add_column("Type", style="red")
        st.add_column("Snippet", style="white")
        for s in f["secrets"][:20]:
            st.add_row(s["file"], s["type"], s["snippet"])
        console.print(st)

    # URLs
    if f["urls"]:
        console.print(f"\n[bold cyan]🌐 Embedded URLs ({len(f['urls'])}):[/]")
        for u in f["urls"][:15]:
            console.print(f"  [dim]►[/] {u}")

    # Vulnerabilities summary
    if f["vulnerabilities"]:
        vt = Table(title=f"🚨 Vulnerabilities Found ({len(f['vulnerabilities'])})",
                   box=box.SIMPLE_HEAVY, border_style="red", header_style="bold red")
        vt.add_column("Finding", style="white")
        vt.add_column("Severity", style="red")
        vt.add_column("Detail", style="dim")
        for v in f["vulnerabilities"]:
            sev = v["severity"]
            vt.add_row(v["name"], f"[{SEV_COLOR.get(sev, 'white')}]{sev}[/]", v["detail"])
        console.print(vt)

    # Native libs
    if f["libs"]:
        console.print(f"\n[bold cyan]🔧 Native Libraries ({len(f['libs'])}):[/]")
        for lib in f["libs"]:
            console.print(f"  [dim]►[/] {lib}")

    console.print("\n[bold green]✓ Static analysis complete.[/]")
