"""
Vantablack Core v5 - CLI (vanta)
================================

Unified Command Line Interface for:
- Campaign Management (setup, run, stop)
- Asset Generation (mutate, analyze)
- System Status (metrics, health)
"""

import click
import asyncio
import logging
from rich.console import Console
from rich.table import Table
from core.mutation.engine import MutationEngine
from core.mutation.scanner import DetectionScanner

console = Console()

@click.group()
def cli():
    """Vantablack Core v5 - Red Team Operations Suite"""
    logging.basicConfig(level=logging.INFO)

@cli.command()
@click.option("--name", prompt="Campaign Name", help="Name of the campaign")
@click.option("--target", prompt="Target Profile", help="Target organization/profile")
def setup(name, target):
    """Initialize a new campaign structure"""
    console.print(f"[green]Initializing campaign: {name} (Target: {target})[/green]")
    # TODO: Create campaign directory and config from template
    console.print("[bold]Done.[/bold]")

@cli.command()
@click.option("--campaign", required=True, help="Campaign ID to run")
def run(campaign):
    """Launch a campaign (Delivery + Edge)"""
    console.print(f"[yellow]Launching campaign {campaign}...[/yellow]")
    # TODO: Invoke Orchestrator
    console.print("[green]Campaign is RUNNING[/green]")

@cli.command()
@click.option("--file", required=True, help="Input HTML/JS file")
def mutate(file):
    """Obfuscate and mutate a payload file"""
    try:
        with open(file, 'r') as f:
            content = f.read()
        
        engine = MutationEngine()
        if file.endswith(".html"):
            mutated = engine.mutate_html(content)
        elif file.endswith(".js"):
            mutated = engine.mutate_js(content)
        else:
            console.print("[red]Unsupported file type[/red]")
            return

        out_file = f"{file}.mutated"
        with open(out_file, 'w') as f:
            f.write(mutated)
            
        console.print(f"[green]Mutation complete. Saved to {out_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option("--file", required=True, help="File to analyze")
def analyze(file):
    """Scan a file for detection signatures"""
    try:
        with open(file, 'r') as f:
            content = f.read()
            
        scanner = DetectionScanner()
        result = scanner.scan_content(content)
        
        table = Table(title="Analysis Result")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Status", result["status"])
        table.add_row("Risk Score", str(result["score"]))
        table.add_row("Signatures", ", ".join(result["matches"]))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    cli()
