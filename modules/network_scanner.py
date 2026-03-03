"""
PhantomDroid — Network Scanner Module
Author: Mr. Psycho | @the_psycho_of_hackers
"""

import subprocess
import re
import socket
import concurrent.futures
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5555: "ADB",
    5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    8888: "HTTP-Alt2", 27017: "MongoDB", 9200: "Elasticsearch",
    4444: "Metasploit", 1099: "RMI", 8161: "ActiveMQ",
}


def _run_adb(args: list, device_id: str = None):
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return r.stdout.strip()
    except Exception:
        return ""


def get_device_ip(device_id: str) -> str:
    """Get device IP via ADB."""
    out = _run_adb(["shell", "ip addr show wlan0"], device_id)
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", out)
    if match:
        return match.group(1)
    # Fallback: try netcfg
    out2 = _run_adb(["shell", "netcfg"], device_id)
    match2 = re.search(r"wlan0\s+UP\s+(\d+\.\d+\.\d+\.\d+)", out2)
    return match2.group(1) if match2 else None


def get_wifi_info(device_id: str) -> dict:
    """Retrieve WiFi connection details."""
    info = {}
    # SSID + BSSID via wpa_supplicant or dumpsys
    wpa = _run_adb(["shell", "wpa_cli status"], device_id)
    dumpsys = _run_adb(["shell", "dumpsys wifi | grep -E 'SSID|BSSID|freq|rssi|ip_address'"], device_id)

    for line in (wpa + "\n" + dumpsys).splitlines():
        kv = line.strip().split("=", 1)
        if len(kv) == 2:
            k, v = kv[0].strip().lower(), kv[1].strip()
            if "ssid" in k and "bssid" not in k:
                info["SSID"] = v.strip('"')
            elif "bssid" in k:
                info["BSSID"] = v
            elif "freq" in k:
                info["Frequency"] = v + " MHz"
            elif "rssi" in k or "signal" in k:
                info["Signal"] = v + " dBm"
            elif "ip_address" in k or (k == "ip_address"):
                info["IP"] = v
            elif "security" in k or "key_mgmt" in k:
                info["Security"] = v

    table = Table(title="[bold magenta]📶 WiFi Info[/]", box=box.SIMPLE, border_style="cyan")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    for k, v in info.items():
        table.add_row(k, v)
    console.print(table)
    return info


def _scan_port(host: str, port: int, timeout: float = 0.8) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def port_scan(target: str, ports: list = None, timeout: float = 0.8, max_workers: int = 100):
    """Fast multithreaded port scanner."""
    if ports is None:
        ports = list(COMMON_PORTS.keys())

    console.print(Panel(f"[bold cyan]Port Scanning:[/] {target}  ({len(ports)} ports)", border_style="magenta"))
    open_ports = []

    with console.status(f"[cyan]Scanning {len(ports)} ports on {target}...[/]"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(_scan_port, target, p, timeout): p for p in ports}
            for fut in concurrent.futures.as_completed(futures):
                port = futures[fut]
                if fut.result():
                    open_ports.append(port)

    open_ports.sort()
    table = Table(title=f"[bold green]Open Ports on {target}[/]", box=box.SIMPLE_HEAVY,
                  border_style="green", header_style="bold green")
    table.add_column("Port", style="cyan", width=8)
    table.add_column("Service", style="white")
    table.add_column("Risk", style="red")

    risky = {21, 23, 3389, 5900, 4444, 1099, 5555}
    for p in open_ports:
        svc = COMMON_PORTS.get(p, "Unknown")
        risk = "[bold red]HIGH[/]" if p in risky else ("[yellow]MEDIUM[/]" if p in {80, 8080, 27017, 6379} else "[green]LOW[/]")
        table.add_row(str(p), svc, risk)

    if open_ports:
        console.print(table)
    else:
        console.print("[yellow]No open ports found in the scanned range.[/]")

    # Flag ADB port
    if 5555 in open_ports:
        console.print(Panel(
            "[bold red]⚠  ADB port 5555 is OPEN![/]\n"
            "The device may be exploitable via: [bold yellow]adb connect {target}:5555[/]",
            border_style="red"))

    return open_ports


def discover_devices(subnet: str) -> list:
    """Discover live hosts on a subnet (e.g., 192.168.1.0/24)."""
    console.print(f"[cyan]Discovering hosts on {subnet}...[/]")
    try:
        base = ".".join(subnet.split(".")[:3])
        live = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
            futures = {ex.submit(_scan_port, f"{base}.{i}", 80, 0.5): i for i in range(1, 255)}
            futures2 = {ex.submit(_scan_port, f"{base}.{i}", 443, 0.5): i for i in range(1, 255)}
            for fut in concurrent.futures.as_completed({**futures, **futures2}):
                # track by combining results
                pass

        # simpler approach: ping sweep
        hosts = []
        for i in range(1, 255):
            host = f"{base}.{i}"
            r = subprocess.run(["ping", "-c", "1", "-W", "1", host],
                               capture_output=True, text=True)
            if r.returncode == 0:
                hosts.append(host)
                console.print(f"  [green]✓ Live:[/] {host}")
        return hosts
    except Exception as e:
        console.print(f"[red]Error in discovery: {e}[/]")
        return []


def check_ssl_pinning(device_id: str, package: str) -> dict:
    """Check for SSL pinning indicators in app's network stack via logcat."""
    console.print(f"[cyan]Checking SSL pinning for {package}...[/]")
    out = _run_adb(["shell", f"logcat -d | grep -i '{package}' | grep -iE 'ssl|tls|pin|certificate'"], device_id)
    
    indicators = []
    if "CertificatePinning" in out or "TrustKit" in out or "OkHttp" in out:
        indicators.append("OkHttp / TrustKit pinning detected")
    if "public key" in out.lower() or "pin" in out.lower():
        indicators.append("Public key pinning suspected")
    if "SSLError" in out:
        indicators.append("SSL errors in logcat (possible MitM attempt detected by app)")

    result = {"pinning_detected": len(indicators) > 0, "indicators": indicators}
    if result["pinning_detected"]:
        console.print(f"[bold yellow]⚠  SSL Pinning indicators found:[/]")
        for ind in indicators:
            console.print(f"  [yellow]►[/] {ind}")
    else:
        console.print("[green]No obvious SSL pinning indicators in logcat.[/]")
    return result


def mitm_setup_guide():
    """Print a guide for setting up MitM with mitmproxy."""
    guide = """
[bold magenta]── MitM Proxy Setup Guide ──────────────────────────────────[/]

[bold cyan]1. Install mitmproxy:[/]
   pip install mitmproxy

[bold cyan]2. Start transparent proxy:[/]
   mitmproxy --mode transparent --showhost

[bold cyan]3. On device (ADB shell, requires root or WiFi proxy):[/]
   adb shell settings put global http_proxy <your-ip>:8080

[bold cyan]4. Install mitmproxy CA cert on device:[/]
   Browse to http://mitm.it from the device

[bold cyan]5. For SSL Pinning bypass, use Frida + objection:[/]
   objection -g <package_name> explore
   android sslpinning disable

[bold cyan]6. Capture traffic:[/]
   mitmweb --mode transparent
    """
    console.print(Panel(guide, title="[bold]MitM Setup Guide[/]", border_style="cyan"))
