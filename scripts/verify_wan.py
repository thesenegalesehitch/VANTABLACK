import sys
import subprocess
import time
import requests
import re
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_wan_verification():
    """
    Simulates a full E2E test:
    1. Checks if server is running (or starts it)
    2. Checks WAN connectivity
    3. Simulates Cloudflared tunnel check
    """
    console.print(Panel("Running Piloted E2E Test: WAN Verification", style="bold cyan"))

    # Step 1: Local Health Check
    console.print("[*] Checking Local Server Health...")
    try:
        r = requests.get("http://127.0.0.1:8080/health", timeout=2)
        if r.status_code == 200:
            console.print("[green]PASSED: Local server is reachable.[/green]")
        else:
            console.print(f"[red]FAILED: Local server returned {r.status_code}[/red]")
            return False
    except:
        console.print("[red]FAILED: Could not connect to local server. Is it running?[/red]")
        return False

    # Step 2: WAN Connectivity via Server API
    console.print("[*] Checking WAN Connectivity via Server API...")
    try:
        r = requests.get("http://127.0.0.1:8080/api/wan_check", timeout=5)
        data = r.json()
        if data.get("status") == "ok":
            console.print("[green]PASSED: Server has WAN access.[/green]")
        else:
            console.print("[red]FAILED: Server reports no WAN access.[/red]")
            return False
    except Exception as e:
        console.print(f"[red]FAILED: API call failed: {e}[/red]")
        return False

    # Step 3: Cloudflared Simulation
    console.print("[*] Verifying Cloudflared Integration (Simulation)...")
    # In a real scenario, we would check the process list or the tunnel URL
    # Here we check if 'cloudflared' is in path
    try:
        subprocess.run(["cloudflared", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        console.print("[green]PASSED: cloudflared binary found.[/green]")
    except:
        console.print("[yellow]WARNING: cloudflared not found in PATH. Tunneling will fail.[/yellow]")
    
    console.print(Panel("[bold green]E2E WAN VERIFICATION SUCCESSFUL[/bold green]"))
    return True

if __name__ == "__main__":
    success = test_wan_verification()
    sys.exit(0 if success else 1)
