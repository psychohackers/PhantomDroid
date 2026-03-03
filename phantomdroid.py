#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║          PhantomDroid — Advanced Android Pentesting Tool         ║
║          Author : Mr. Psycho                                     ║
║          Contact: Instagram @the_psycho_of_hackers               ║
║          For authorized penetration testing use only             ║
╚══════════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
import os
import time
import json
import random

# ── Rich UI ────────────────────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    from rich.align import Align
    from rich.columns import Columns
except ImportError:
    print("[!] 'rich' not installed. Run: pip install rich")
    sys.exit(1)

# ── Modules ────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from modules import adb_manager, apk_analyzer, network_scanner
from modules import vulnerability_scanner, exploit_engine, payload_generator, report_generator

console = Console()

VERSION     = "2.0.0"
AUTHOR      = "Mr. Psycho"
INSTAGRAM   = "@the_psycho_of_hackers"
TOOL_NAME   = "PhantomDroid"
YEAR        = "2026"


# ═══════════════════════════════════════════════════════════════════════════════
#  BANNER & ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════

BANNER_ART = r"""
    ____  __                __                  ____            _     __
   / __ \/ /_  ____ _____  / /_____  ____ ___  / __ \_________ (_)___/ /
  / /_/ / __ \/ __ `/ __ \/ __/ __ \/ __ `__ \/ / / / ___/ __ \/ / __  / 
 / ____/ / / / /_/ / / / / /_/ /_/ / / / / / / /_/ / /  / /_/ / / /_/ /  
/_/   /_/ /_/\__,_/_/ /_/\__/\____/_/ /_/ /_/_____/_/   \____/_/\__,_/   
"""

BANNER_LINES_GRADIENT = [
    "magenta", "bright_magenta", "purple", "deep_pink3", "orchid", "violet"
]

def get_banner_status():
    """Gather live status info for the banner."""
    try:
        devices = adb_manager.list_devices()
        device_count = len(devices)
        status_color = "green" if device_count > 0 else "red"
        device_text = f"[{status_color}]{device_count} Connected[/]"
    except:
        device_text = "[yellow]ADB Not Found[/]"

    from datetime import datetime
    now = datetime.now().strftime("%H:%M:%S")
    
    return (
        f"📅 [bold white]{now}[/]  |  "
        f"📱 [bold cyan]Devices:[/] {device_text}  |  "
        f"🚀 [bold green]v{VERSION}[/]"
    )

def animate_glitch_banner():
    """Display a matrix/glitch reveal for the banner."""
    from rich.markup import escape
    lines = BANNER_ART.strip("\n").split("\n")
    
    # Glitch phase
    chars = "01$#!@%^&*()_+=-[]{}|;:,.<>?/"
    for _ in range(12):
        glitch_lines = []
        for line in lines:
            glitch_line = "".join(random.choice(chars) if c != " " else " " for c in line)
            color = random.choice(BANNER_LINES_GRADIENT)
            # Escape the glitch line to prevent MarkupError
            glitch_lines.append(f"[bold {color}]{escape(glitch_line)}[/]")
        
        console.clear()
        for gl in glitch_lines:
            console.print(Align.center(gl))
        time.sleep(0.06)

    # Settling phase (line by line reveal)
    console.clear()
    for i, line in enumerate(lines):
        color = BANNER_LINES_GRADIENT[i % len(BANNER_LINES_GRADIENT)]
        console.print(Align.center(f"[bold {color}]{line}[/]"))
        time.sleep(0.05)

def print_banner():
    """Print the animated PhantomDroid banner with live status."""
    animate_glitch_banner()

    # Tagline
    tagline = Text("◈ ADVANCED ANDROID PENTESTING FRAMEWORK ◈", style="bold italic bright_magenta")
    console.print(Align.center(tagline))
    console.print()

    # Status Panel
    status_text = get_banner_status()
    console.print(Align.center(Panel(
        status_text,
        border_style="magenta",
        box=box.HORIZONTALS,
        padding=(0, 2),
        title="[bold magenta]System Status[/]",
        title_align="left"
    )))
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ═══════════════════════════════════════════════════════════════════════════════

MENU_OPTIONS = [
    ("1",  "📱", "Device Manager",          "List & manage connected Android devices"),
    ("2",  "🔎", "APK Static Analyzer",     "Decompile & audit an APK file"),
    ("3",  "🌐", "Network Scanner",         "Port scan, WiFi info, host discovery"),
    ("4",  "🚨", "Vulnerability Scanner",   "CVE mapping, root check, insecure storage"),
    ("5",  "💥", "Exploit Engine",          "Launch activities, deep links, shell dropper"),
    ("6",  "🎯", "Payload Generator",       "APK payloads, reverse shells, obfuscation"),
    ("7",  "📋", "Report Generator",        "Generate HTML/JSON security report"),
    ("8",  "📡", "ADB WiFi Connect",        "Enable & connect ADB over WiFi"),
    ("9",  "📸", "Screenshot Capture",      "Capture device screenshot via ADB"),
    ("10", "📦", "Package Manager",         "Enumerate installed packages"),
    ("11", "🐛", "Logcat Analyzer",         "Capture & analyze logcat for secrets"),
    ("12", "🔐", "SSL Pinning Check",       "Detect SSL pinning in target app"),
    ("13", "📂", "File Transfer",           "Pull/push files from/to device"),
    ("14", "💻", "Interactive ADB Shell",   "Drop into live ADB shell"),
    ("15", "ℹ️ ", "About",                   "About PhantomDroid"),
    ("0",  "🚪", "Exit",                    "Exit PhantomDroid"),
]


def print_main_menu():
    t = Table(
        title=f"\n[bold magenta]👻  {TOOL_NAME}  —  Main Menu[/]\n",
        box=box.DOUBLE_EDGE,
        border_style="magenta",
        header_style="bold cyan",
        show_lines=True,
        min_width=70,
    )
    t.add_column("  #  ",   style="bold cyan",   width=5,  no_wrap=True)
    t.add_column("  ",      style="",             width=3,  no_wrap=True)
    t.add_column("Module",  style="bold white",   min_width=24)
    t.add_column("Description", style="dim",      min_width=38)

    for num, icon, name, desc in MENU_OPTIONS:
        style = "on #1a0030" if num == "0" else ""
        t.add_row(f"[bold cyan] {num} [/]", icon, name, desc, style=style)

    console.print(t)


# ═══════════════════════════════════════════════════════════════════════════════
#  DEVICE SELECTION HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def select_device() -> str:
    """Select a connected device; return its serial."""
    devices = adb_manager.list_devices()
    if not devices:
        return None
    if len(devices) == 1:
        dev = devices[0]["serial"]
        console.print(f"[green]Auto-selected device:[/] {dev}")
        return dev
    serial = Prompt.ask("[cyan]Enter device serial[/]")
    return serial


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def handle_device_manager():
    console.rule("[bold magenta]📱 Device Manager[/]")
    adb_manager.check_adb()
    device_id = select_device()
    if not device_id:
        return
    adb_manager.device_info(device_id)


def handle_apk_analyzer():
    console.rule("[bold magenta]🔎 APK Static Analyzer[/]")
    apk_path = Prompt.ask("[cyan]APK file path[/]")
    findings  = apk_analyzer.analyze_apk(apk_path)
    if Confirm.ask("[cyan]Save findings to report?[/]", default=True):
        _save_to_session(findings, "apk_analysis")
        console.print("[green]✓ Added to session report.[/]")


def handle_network_scanner():
    console.rule("[bold magenta]🌐 Network Scanner[/]")
    choice = Prompt.ask("[cyan]Scan mode[/]", choices=["device", "host", "wifi", "discover", "mitm"], default="device")

    if choice == "device":
        device_id = select_device()
        if not device_id:
            return
        ip = network_scanner.get_device_ip(device_id)
        if ip:
            console.print(f"[green]Device IP:[/] {ip}")
            network_scanner.port_scan(ip)
        else:
            console.print("[red]Could not determine device IP.[/]")

    elif choice == "host":
        target = Prompt.ask("[cyan]Target IP/hostname[/]")
        port_range = Prompt.ask("[cyan]Port range (comma-list or 'all')[/]", default="common")
        if port_range == "all":
            ports = list(range(1, 65536))
        elif port_range == "common":
            ports = None
        else:
            ports = [int(p.strip()) for p in port_range.split(",") if p.strip().isdigit()]
        network_scanner.port_scan(target, ports)

    elif choice == "wifi":
        device_id = select_device()
        if device_id:
            network_scanner.get_wifi_info(device_id)

    elif choice == "discover":
        subnet = Prompt.ask("[cyan]Subnet (e.g. 192.168.1)[/]")
        network_scanner.discover_devices(subnet)

    elif choice == "mitm":
        network_scanner.mitm_setup_guide()


def handle_vulnerability_scanner():
    console.rule("[bold magenta]🚨 Vulnerability Scanner[/]")
    device_id = select_device()
    if not device_id:
        return
    pkg = Prompt.ask("[cyan]Target package (leave blank for device-level only)[/]", default="")
    report = vulnerability_scanner.full_vulnerability_scan(device_id, pkg or None)
    _save_to_session(report, "vulnerability_scan")


def handle_exploit_engine():
    console.rule("[bold magenta]💥 Exploit Engine[/]")
    device_id = select_device()
    if not device_id:
        return

    exploit_engine.exploit_menu(device_id)
    choice = Prompt.ask("[red]Select exploit[/]", choices=[str(i) for i in range(10)])

    if choice == "1":
        pkg  = Prompt.ask("[cyan]Package name[/]")
        act  = Prompt.ask("[cyan]Activity class[/]")
        exploit_engine.launch_exported_activity(device_id, pkg, act)

    elif choice == "2":
        pkg    = Prompt.ask("[cyan]Package name[/]")
        action = Prompt.ask("[cyan]Intent action[/]")
        exploit_engine.trigger_broadcast_receiver(device_id, pkg, action)

    elif choice == "3":
        uri = Prompt.ask("[cyan]Content provider URI (content://...)[/]")
        exploit_engine.extract_content_provider(device_id, uri)

    elif choice == "4":
        pkg    = Prompt.ask("[cyan]Package name[/]")
        scheme = Prompt.ask("[cyan]Deep link scheme (e.g. myapp)[/]")
        exploit_engine.deep_link_fuzzer(device_id, pkg, scheme)

    elif choice == "5":
        pkg = Prompt.ask("[cyan]Package name[/]")
        exploit_engine.frida_injection_guide(pkg)

    elif choice == "6":
        lhost = Prompt.ask("[cyan]LHOST[/]")
        lport = IntPrompt.ask("[cyan]LPORT[/]", default=4444)
        exploit_engine.shell_payload_dropper(device_id, lhost, lport)

    elif choice == "7":
        pkg  = Prompt.ask("[cyan]Package name[/]")
        db   = Prompt.ask("[cyan]Database filename[/]")
        exploit_engine.extract_database(device_id, pkg, db)

    elif choice == "8":
        exploit_engine.bypass_lock_screen(device_id)

    elif choice == "9":
        exploit_engine.enable_developer_options(device_id)


def handle_payload_generator():
    console.rule("[bold magenta]🎯 Payload Generator[/]")
    payload_generator.payload_menu()
    choice = Prompt.ask("[red]Select payload type[/]", choices=["1", "2", "3", "4", "5", "0"])

    if choice == "1":
        lhost  = Prompt.ask("[cyan]LHOST[/]")
        lport  = IntPrompt.ask("[cyan]LPORT[/]", default=4444)
        ptype  = Prompt.ask("[cyan]Payload type[/]",
                             choices=["reverse_tcp", "reverse_https", "reverse_http", "shell_tcp"],
                             default="reverse_tcp")
        output = Prompt.ask("[cyan]Output file[/]", default="payload.apk")
        payload_generator.generate_msfvenom_apk(lhost, lport, ptype, output)

    elif choice == "2":
        action = Prompt.ask("[cyan]Intent action[/]")
        comp   = Prompt.ask("[cyan]Component (pkg/class or blank)[/]", default="")
        data   = Prompt.ask("[cyan]Data URI (or blank)[/]", default="")
        payload_generator.generate_intent_payload(action, comp or None, data or None)

    elif choice == "3":
        lhost = Prompt.ask("[cyan]LHOST[/]")
        lport = IntPrompt.ask("[cyan]LPORT[/]", default=4444)
        payload_generator.generate_reverse_shell_commands(lhost, lport)

    elif choice == "4":
        lhost  = Prompt.ask("[cyan]LHOST[/]")
        lport  = IntPrompt.ask("[cyan]LPORT[/]", default=4444)
        output = Prompt.ask("[cyan]Script filename[/]", default="adb_payload.sh")
        payload_generator.generate_adb_payload_script(None, lhost, lport, output)

    elif choice == "5":
        raw   = Prompt.ask("[cyan]Payload to obfuscate[/]")
        method = Prompt.ask("[cyan]Obfuscation method[/]", choices=["base64", "hex"], default="base64")
        payload_generator.obfuscate_payload(raw, method)


def handle_report_generator():
    console.rule("[bold magenta]📋 Report Generator[/]")
    target = Prompt.ask("[cyan]Target description (app/device name)[/]", default="Unknown Target")

    # Build report from session
    data = _get_session()
    data["target"] = target

    fmt = Prompt.ask("[cyan]Report format[/]", choices=["html", "json", "both", "table"], default="html")

    if fmt in ("html", "both"):
        out = Prompt.ask("[cyan]HTML output filename[/]", default="phantomdroid_report.html")
        report_generator.generate_html_report(data, out)

    if fmt in ("json", "both"):
        out = Prompt.ask("[cyan]JSON output filename[/]", default="phantomdroid_report.json")
        report_generator.generate_json_report(data, out)

    if fmt == "table":
        report_generator.print_summary_table(data)


def handle_adb_wifi():
    console.rule("[bold magenta]📡 ADB WiFi Connect[/]")
    device_id = select_device()
    if not device_id:
        return
    port = IntPrompt.ask("[cyan]Port[/]", default=5555)
    ip, p = adb_manager.enable_adb_wifi(device_id, port)


def handle_screenshot():
    console.rule("[bold magenta]📸 Screenshot Capture[/]")
    device_id = select_device()
    if not device_id:
        return
    path = adb_manager.take_screenshot(device_id)
    if path:
        console.print(f"[bold green]✓ Screenshot saved:[/] {path}")


def handle_package_manager():
    console.rule("[bold magenta]📦 Package Manager[/]")
    device_id = select_device()
    if not device_id:
        return
    pkg_type = Prompt.ask("[cyan]Package filter[/]",
                           choices=["all", "system", "third_party", "disabled"],
                           default="third_party")
    adb_manager.list_packages(device_id, pkg_type)


def handle_logcat():
    console.rule("[bold magenta]🐛 Logcat Analyzer[/]")
    device_id = select_device()
    if not device_id:
        return
    lines = IntPrompt.ask("[cyan]Lines to capture[/]", default=300)
    adb_manager.capture_logcat(device_id, lines)


def handle_ssl_check():
    console.rule("[bold magenta]🔐 SSL Pinning Check[/]")
    device_id = select_device()
    if not device_id:
        return
    pkg = Prompt.ask("[cyan]Package name[/]")
    network_scanner.check_ssl_pinning(device_id, pkg)


def handle_file_transfer():
    console.rule("[bold magenta]📂 File Transfer[/]")
    device_id = select_device()
    if not device_id:
        return
    direction = Prompt.ask("[cyan]Direction[/]", choices=["pull", "push"])
    if direction == "pull":
        remote = Prompt.ask("[cyan]Remote path (on device)[/]")
        local  = Prompt.ask("[cyan]Local destination[/]", default=".")
        adb_manager.pull_file(device_id, remote, local)
    else:
        local  = Prompt.ask("[cyan]Local file path[/]")
        remote = Prompt.ask("[cyan]Remote destination (on device)[/]")
        adb_manager.push_file(device_id, local, remote)


def handle_adb_shell():
    console.rule("[bold magenta]💻 Interactive ADB Shell[/]")
    device_id = select_device()
    if not device_id:
        return
    adb_manager.interactive_shell(device_id)


def handle_about():
    about = Panel(
        f"\n"
        f"  [bold magenta]👻  {TOOL_NAME} v{VERSION}[/]\n\n"
        f"  [bold cyan]Advanced Android Penetration Testing Framework[/]\n\n"
        f"  [white]A comprehensive tool for ethical hackers and security professionals.\n"
        f"  Covers static APK analysis, dynamic runtime analysis via ADB,\n"
        f"  network scanning, vulnerability mapping, exploit assistance,\n"
        f"  payload generation, and professional report generation.[/]\n\n"
        f"  [bold magenta]Author   :[/] [white]{AUTHOR}[/]\n"
        f"  [bold magenta]Instagram:[/] [cyan]{INSTAGRAM}[/]\n"
        f"  [bold magenta]Year     :[/] [white]{YEAR}[/]\n\n"
        f"  [bold red]⚠  For authorized penetration testing use only.[/]\n"
        f"  [dim]Unauthorized use is illegal and unethical.[/]\n",
        title="[bold]About PhantomDroid[/]",
        border_style="magenta",
        padding=(0, 4),
    )
    console.print(about)


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STORE (in-memory findings accumulator)
# ═══════════════════════════════════════════════════════════════════════════════

_SESSION = {"findings": [], "permissions": [], "secrets": [], "urls": []}


def _save_to_session(data: dict, source: str):
    """Merge findings from a module into the session store."""
    if isinstance(data, dict):
        for vuln in data.get("vulnerabilities", []):
            _SESSION["findings"].append(vuln)
        for vuln in data.get("cves", []):
            _SESSION["findings"].append({
                "name": vuln.get("cve", "CVE"),
                "severity": vuln.get("severity", "MEDIUM"),
                "detail": vuln.get("detail", ""),
                "cve": vuln.get("cve"),
            })
        _SESSION["permissions"].extend(data.get("dangerous_permissions", []))
        _SESSION["secrets"].extend(data.get("secrets", []))
        _SESSION["urls"].extend(data.get("urls", []))


def _get_session() -> dict:
    return _SESSION.copy()


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVE MODE
# ═══════════════════════════════════════════════════════════════════════════════

HANDLER_MAP = {
    "1":  handle_device_manager,
    "2":  handle_apk_analyzer,
    "3":  handle_network_scanner,
    "4":  handle_vulnerability_scanner,
    "5":  handle_exploit_engine,
    "6":  handle_payload_generator,
    "7":  handle_report_generator,
    "8":  handle_adb_wifi,
    "9":  handle_screenshot,
    "10": handle_package_manager,
    "11": handle_logcat,
    "12": handle_ssl_check,
    "13": handle_file_transfer,
    "14": handle_adb_shell,
    "15": handle_about,
}


def interactive_mode():
    print_banner()
    console.print(Panel(
        "[bold red]⚠  LEGAL DISCLAIMER[/]\n\n"
        "[white]PhantomDroid is designed for authorized security testing ONLY.\n"
        "Use of this tool against systems you do not own or have explicit written\n"
        "permission to test is [bold red]ILLEGAL[/] and may result in criminal prosecution.\n"
        "The author assumes no liability for misuse.[/]",
        border_style="red", padding=(0, 2)))

    if not Confirm.ask("\n[bold red]I confirm I have authorization to test the target system[/]", default=False):
        console.print("[yellow]Exiting. Obtain proper authorization before testing.[/]")
        sys.exit(0)

    while True:
        console.print()
        print_main_menu()
        valid_choices = [str(i) for i in range(16)]
        choice = Prompt.ask("\n[bold cyan]PhantomDroid ▶[/]", choices=valid_choices, show_choices=False)

        if choice == "0":
            console.print("\n[bold magenta]👻 Exiting PhantomDroid. Stay ethical.[/]\n")
            sys.exit(0)

        handler = HANDLER_MAP.get(choice)
        if handler:
            try:
                console.print()
                handler()
            except KeyboardInterrupt:
                console.print("\n[yellow]↩ Returned to main menu.[/]")
            except Exception as e:
                console.print(f"\n[bold red]✗ Error:[/] {e}")
        else:
            console.print("[red]Invalid option.[/]")

        console.print()
        Prompt.ask("[dim]Press ENTER to continue[/]", default="")


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI MODE  (argparse)
# ═══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="phantomdroid",
        description=f"👻 PhantomDroid v{VERSION} — Advanced Android Pentesting Tool by {AUTHOR}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 phantomdroid.py --interactive
  python3 phantomdroid.py --apk app.apk --report html
  python3 phantomdroid.py --device ABC123 --vuln-scan --pkg com.example.app
  python3 phantomdroid.py --device ABC123 --port-scan
  python3 phantomdroid.py --payload reverse_tcp --lhost 10.0.0.1 --lport 4444
  python3 phantomdroid.py --device ABC123 --exploit deep-link --pkg com.example --scheme myapp
  python3 phantomdroid.py --devices
        """
    )

    p.add_argument("--interactive", "-i",  action="store_true",    help="Launch interactive menu mode")
    p.add_argument("--version",     "-v",  action="store_true",    help="Show version")

    # Device
    dg = p.add_argument_group("Device")
    dg.add_argument("--devices",           action="store_true",    help="List connected devices")
    dg.add_argument("--device", "-d",      metavar="SERIAL",       help="Target device serial number")
    dg.add_argument("--info",              action="store_true",    help="Show device info")
    dg.add_argument("--shell",             metavar="CMD",          help="Run ADB shell command")
    dg.add_argument("--adb-shell",         action="store_true",    help="Drop into interactive ADB shell")
    dg.add_argument("--adb-wifi",          action="store_true",    help="Enable ADB over WiFi")
    dg.add_argument("--screenshot",        action="store_true",    help="Capture device screenshot")
    dg.add_argument("--logcat",            metavar="N", type=int,  help="Capture N lines of logcat", nargs="?", const=200)
    dg.add_argument("--packages",          choices=["all","system","third_party","disabled"],
                                                                   help="List installed packages")
    dg.add_argument("--pull",              metavar="REMOTE",       help="Pull file from device")
    dg.add_argument("--push",             nargs=2, metavar=("LOCAL","REMOTE"), help="Push file to device")

    # APK Analysis
    ag = p.add_argument_group("APK Analysis")
    ag.add_argument("--apk",              metavar="FILE",          help="APK file to analyze")

    # Network
    ng = p.add_argument_group("Network")
    ng.add_argument("--port-scan",        action="store_true",    help="Port scan device IP")
    ng.add_argument("--target",           metavar="IP",           help="Explicit scan target IP")
    ng.add_argument("--ports",            metavar="PORTS",        help="Comma-separated ports or 'all'")
    ng.add_argument("--wifi-info",        action="store_true",    help="Show WiFi info")
    ng.add_argument("--discover",         metavar="SUBNET",       help="Discover hosts on subnet")
    ng.add_argument("--ssl-pinning",      metavar="PKG",          help="Check SSL pinning for package")
    ng.add_argument("--mitm-guide",       action="store_true",    help="Show MitM setup guide")

    # Vulnerability
    vg = p.add_argument_group("Vulnerability")
    vg.add_argument("--vuln-scan",        action="store_true",    help="Run full vulnerability scan")
    vg.add_argument("--pkg",             metavar="PKG",           help="Target package name")
    vg.add_argument("--cve-check",       action="store_true",     help="Check Android CVEs for device")
    vg.add_argument("--root-check",      action="store_true",     help="Check if device is rooted")

    # Exploit
    eg = p.add_argument_group("Exploit")
    eg.add_argument("--exploit",          metavar="MODULE",
                    choices=["activity","broadcast","provider","deep-link","frida","shell-drop","db-extract","lock-bypass","dev-options"],
                    help="Exploit module to run")
    eg.add_argument("--activity",         metavar="CLASS",        help="Activity class for --exploit activity")
    eg.add_argument("--action",           metavar="ACTION",       help="Intent action")
    eg.add_argument("--uri",              metavar="URI",          help="URI for content provider / deep link")
    eg.add_argument("--scheme",           metavar="SCHEME",       help="Deep link scheme")
    eg.add_argument("--lhost",            metavar="IP",           help="Listener host")
    eg.add_argument("--lport",            metavar="PORT", type=int, default=4444, help="Listener port")
    eg.add_argument("--db-name",          metavar="DB",           help="Database filename to extract")

    # Payload
    pg = p.add_argument_group("Payload")
    pg.add_argument("--payload",          metavar="TYPE",
                    choices=["reverse_tcp","reverse_https","reverse_http","shell_tcp",
                             "intent","reverse-shells","adb-script","obfuscate"],
                    help="Generate a payload")
    pg.add_argument("--payload-out",      metavar="FILE",         help="Output file for payload")
    pg.add_argument("--obfuscate-method", choices=["base64","hex"], default="base64",
                    help="Obfuscation method")
    pg.add_argument("--raw-payload",      metavar="CMD",          help="Payload string to obfuscate")

    # Report
    rg = p.add_argument_group("Report")
    rg.add_argument("--report",           choices=["html","json","both","table"],
                    help="Generate report after scan")
    rg.add_argument("--report-out",       metavar="FILE",         help="Report output filename")
    rg.add_argument("--target-name",      metavar="NAME",         help="Target name for report", default="Unknown Target")

    return p


def cli_mode(args):
    """Run CLI operations based on parsed arguments."""
    print_banner()

    device_id = args.device
    apk_data = {}

    # Version
    if args.version:
        console.print(f"[bold magenta]{TOOL_NAME}[/] v[bold cyan]{VERSION}[/] by [bold]{AUTHOR}[/]")
        return

    # Devices
    if args.devices:
        adb_manager.check_adb()
        adb_manager.list_devices()

    # Device info
    if args.info and device_id:
        adb_manager.device_info(device_id)

    # Shell command
    if args.shell and device_id:
        adb_manager.shell_cmd(device_id, args.shell)

    # Interactive ADB shell
    if args.adb_shell and device_id:
        adb_manager.interactive_shell(device_id)

    # ADB WiFi
    if args.adb_wifi and device_id:
        adb_manager.enable_adb_wifi(device_id, args.lport)

    # Screenshot
    if args.screenshot and device_id:
        adb_manager.take_screenshot(device_id)

    # Logcat
    if args.logcat is not None and device_id:
        adb_manager.capture_logcat(device_id, args.logcat)

    # Packages
    if args.packages and device_id:
        adb_manager.list_packages(device_id, args.packages)

    # Pull file
    if args.pull and device_id:
        adb_manager.pull_file(device_id, args.pull)

    # Push file
    if args.push and device_id:
        adb_manager.push_file(device_id, args.push[0], args.push[1])

    # APK Analysis
    if args.apk:
        apk_data = apk_analyzer.analyze_apk(args.apk)
        _save_to_session(apk_data, "apk")

    # Network
    if args.port_scan:
        target = args.target
        if not target and device_id:
            target = network_scanner.get_device_ip(device_id)
        if target:
            ports = None
            if args.ports == "all":
                ports = list(range(1, 65536))
            elif args.ports:
                ports = [int(p) for p in args.ports.split(",") if p.strip().isdigit()]
            network_scanner.port_scan(target, ports)
        else:
            console.print("[red]Provide --target or --device for port scan.[/]")

    if args.wifi_info and device_id:
        network_scanner.get_wifi_info(device_id)

    if args.discover:
        network_scanner.discover_devices(args.discover)

    if args.ssl_pinning and device_id:
        network_scanner.check_ssl_pinning(device_id, args.ssl_pinning)

    if args.mitm_guide:
        network_scanner.mitm_setup_guide()

    # Vulnerability
    if args.vuln_scan and device_id:
        report = vulnerability_scanner.full_vulnerability_scan(device_id, args.pkg)
        _save_to_session(report, "vuln")

    if args.cve_check and device_id:
        findings = vulnerability_scanner.check_android_version_cves(device_id)
        _save_to_session({"cves": findings}, "cve")

    if args.root_check and device_id:
        vulnerability_scanner.check_root_status(device_id)

    # Exploit
    if args.exploit and device_id:
        ex = args.exploit
        if ex == "activity":
            exploit_engine.launch_exported_activity(device_id, args.pkg, args.activity)
        elif ex == "broadcast":
            exploit_engine.trigger_broadcast_receiver(device_id, args.pkg, args.action)
        elif ex == "provider":
            exploit_engine.extract_content_provider(device_id, args.uri)
        elif ex == "deep-link":
            exploit_engine.deep_link_fuzzer(device_id, args.pkg, args.scheme)
        elif ex == "frida":
            exploit_engine.frida_injection_guide(args.pkg)
        elif ex == "shell-drop":
            exploit_engine.shell_payload_dropper(device_id, args.lhost, args.lport)
        elif ex == "db-extract":
            exploit_engine.extract_database(device_id, args.pkg, args.db_name)
        elif ex == "lock-bypass":
            exploit_engine.bypass_lock_screen(device_id)
        elif ex == "dev-options":
            exploit_engine.enable_developer_options(device_id)

    # Payload
    if args.payload:
        out = args.payload_out
        if args.payload in ("reverse_tcp","reverse_https","reverse_http","shell_tcp"):
            payload_generator.generate_msfvenom_apk(args.lhost, args.lport, args.payload, out or "payload.apk")
        elif args.payload == "intent":
            payload_generator.generate_intent_payload(args.action, args.pkg, args.uri)
        elif args.payload == "reverse-shells":
            payload_generator.generate_reverse_shell_commands(args.lhost, args.lport)
        elif args.payload == "adb-script":
            payload_generator.generate_adb_payload_script(device_id, args.lhost, args.lport, out or "adb_payload.sh")
        elif args.payload == "obfuscate":
            payload_generator.obfuscate_payload(args.raw_payload or "", args.obfuscate_method)

    # Report
    if args.report:
        data = _get_session()
        data["target"] = args.target_name
        if apk_data:
            data.update(apk_data)
        if args.report in ("html", "both"):
            out = args.report_out or "phantomdroid_report.html"
            report_generator.generate_html_report(data, out)
        if args.report in ("json", "both"):
            out = args.report_out or "phantomdroid_report.json"
            report_generator.generate_json_report(data, out)
        if args.report == "table":
            report_generator.print_summary_table(data)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = build_parser()

    if len(sys.argv) == 1:
        # No args → interactive
        interactive_mode()
        return

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        cli_mode(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold magenta]👻 PhantomDroid interrupted. Stay ethical.[/]\n")
        sys.exit(0)


