"""
PhantomDroid — ADB Manager Module
Author: Mr. Psycho | @the_psycho_of_hackers
"""

import subprocess
import re
import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def run_adb(args: list, device_id: str = None, capture: bool = True):
    """Run an adb command and return stdout."""
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += args
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except FileNotFoundError:
        return None, -1
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -2


def check_adb():
    """Check if adb is installed."""
    out, rc = run_adb(["version"])
    if rc == -1:
        console.print("[bold red]✗ ADB not found![/] Install Android Debug Bridge first.", style="red")
        return False
    console.print(f"[green]✓ ADB found:[/] {out.splitlines()[0]}")
    return True


def list_devices():
    """List all connected Android devices."""
    out, rc = run_adb(["devices", "-l"])
    if out is None:
        console.print("[red]ADB not available.[/]")
        return []

    lines = out.strip().splitlines()
    devices = []
    table = Table(title="[bold magenta]📱 Connected Devices[/]", box=box.DOUBLE_EDGE,
                  border_style="magenta", header_style="bold cyan")
    table.add_column("Serial", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Transport", style="white")

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial = parts[0]
        state = parts[1]
        model = next((p.split(":")[1] for p in parts if p.startswith("model:")), "Unknown")
        transport = next((p.split(":")[1] for p in parts if p.startswith("transport_id:")), "N/A")
        devices.append({"serial": serial, "state": state, "model": model})
        table.add_row(serial, state, model, transport)

    console.print(table)
    if not devices:
        console.print("[yellow]⚠  No devices connected. Connect a device and enable USB Debugging.[/]")
    return devices


def device_info(device_id: str):
    """Gather comprehensive device info."""
    props = {
        "Brand": "ro.product.brand",
        "Model": "ro.product.model",
        "Android Version": "ro.build.version.release",
        "SDK Level": "ro.build.version.sdk",
        "Build ID": "ro.build.id",
        "Security Patch": "ro.build.version.security_patch",
        "Fingerprint": "ro.build.fingerprint",
        "CPU ABI": "ro.product.cpu.abi",
        "IMEI (if rooted)": "ril.serialnumber",
        "Serial": "ro.serialno",
    }

    table = Table(title=f"[bold magenta]🔎 Device Info [{device_id}][/]",
                  box=box.SIMPLE_HEAVY, border_style="cyan", header_style="bold cyan")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    for label, prop in props.items():
        val, _ = run_adb(["shell", f"getprop {prop}"], device_id)
        table.add_row(label, val or "[dim]N/A[/]")

    console.print(table)


def list_packages(device_id: str, pkg_filter: str = "all"):
    """List installed packages."""
    flags = {
        "all": [],
        "system": ["-s"],
        "third_party": ["-3"],
        "disabled": ["-d"],
    }
    flag = flags.get(pkg_filter, [])
    out, _ = run_adb(["shell", "pm", "list", "packages"] + flag, device_id)
    if not out:
        console.print("[red]Could not fetch packages.[/]")
        return []

    packages = [line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")]

    table = Table(title=f"[bold magenta]📦 Packages ({pkg_filter}) — {len(packages)} found[/]",
                  box=box.SIMPLE, border_style="cyan", header_style="bold cyan")
    table.add_column("#", style="dim", width=5)
    table.add_column("Package Name", style="white")

    for i, pkg in enumerate(packages, 1):
        table.add_row(str(i), pkg)

    console.print(table)
    return packages


def dumpsys(device_id: str, service: str = "package"):
    """Run dumpsys for a given service."""
    console.print(f"[cyan]Running dumpsys {service}...[/]")
    out, _ = run_adb(["shell", "dumpsys", service], device_id)
    if out:
        console.print(Panel(out[:3000] + ("..." if len(out) > 3000 else ""),
                            title=f"[bold]dumpsys {service}[/]", border_style="cyan"))
    return out


def capture_logcat(device_id: str, lines: int = 200):
    """Capture last N lines of logcat."""
    console.print(f"[cyan]Capturing last {lines} lines of logcat...[/]")
    out, _ = run_adb(["shell", f"logcat -d -t {lines}"], device_id)
    filename = f"phantomdroid_logcat_{int(time.time())}.txt"
    if out:
        with open(filename, "w") as f:
            f.write(out)
        console.print(f"[green]✓ Logcat saved to:[/] {filename}")

    # Highlight security-sensitive patterns
    patterns = ["password", "token", "secret", "api_key", "auth", "credential", "private"]
    hits = []
    for line in out.splitlines():
        low = line.lower()
        for p in patterns:
            if p in low:
                hits.append(line)
                break

    if hits:
        console.print(f"\n[bold red]⚠  {len(hits)} sensitive pattern(s) found in logcat:[/]")
        for h in hits[:20]:
            console.print(f"  [red]►[/] {h}")
    return out


def pull_file(device_id: str, remote_path: str, local_path: str = "."):
    """Pull a file from device."""
    out, rc = run_adb(["pull", remote_path, local_path], device_id)
    if rc == 0:
        console.print(f"[green]✓ Pulled:[/] {remote_path} → {local_path}")
    else:
        console.print(f"[red]✗ Failed to pull {remote_path}[/]")


def push_file(device_id: str, local_path: str, remote_path: str):
    """Push a file to device."""
    out, rc = run_adb(["push", local_path, remote_path], device_id)
    if rc == 0:
        console.print(f"[green]✓ Pushed:[/] {local_path} → {remote_path}")
    else:
        console.print(f"[red]✗ Failed to push {local_path}[/]")


def take_screenshot(device_id: str):
    """Take a screenshot and pull it."""
    remote = "/sdcard/phantomdroid_screen.png"
    local = f"screenshot_{int(time.time())}.png"
    run_adb(["shell", "screencap", "-p", remote], device_id)
    pull_file(device_id, remote, local)
    run_adb(["shell", "rm", remote], device_id)
    return local


def enable_adb_wifi(device_id: str, port: int = 5555):
    """Enable ADB over WiFi."""
    console.print(f"[cyan]Enabling ADB over WiFi on port {port}...[/]")
    run_adb(["shell", f"setprop service.adb.tcp.port {port}"], device_id)
    run_adb(["shell", "stop adbd && start adbd"], device_id)
    ip_out, _ = run_adb(["shell", "ip addr show wlan0"], device_id)
    ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", ip_out or "")
    if ip_match:
        ip = ip_match.group(1)
        console.print(f"[green]✓ ADB WiFi enabled![/] Connect with: [bold yellow]adb connect {ip}:{port}[/]")
        return ip, port
    else:
        console.print("[yellow]⚠  Could not determine device IP. Connect manually.[/]")
        return None, port


def shell_cmd(device_id: str, cmd: str):
    """Execute a raw shell command."""
    out, rc = run_adb(["shell", cmd], device_id)
    console.print(Panel(out or "(no output)", title=f"[dim]$ {cmd}[/]", border_style="dim"))
    return out


def interactive_shell(device_id: str):
    """Drop into an interactive ADB shell."""
    console.print("[bold yellow]Dropping into ADB shell. Type 'exit' to return.[/]")
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += ["shell"]
    subprocess.call(cmd)
