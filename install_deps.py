#!/usr/bin/env python3
"""
Script d'installation automatique des dépendances manquantes
Détection et installation des packages requis pour Vantablack Core v5
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Exécute une commande et retourne le succès"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0 and check:
            print(f"❌ Erreur: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_package(package_name):
    """Vérifie si un package Python est installé"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_missing_deps():
    """Installe les dépendances manquantes"""
    print("🔍 Recherche des dépendances manquantes...")
    
    # Liste des dépendances critiques
    critical_deps = [
        'fastapi', 'uvicorn', 'pydantic', 'jinja2', 'pyyaml',
        'requests', 'aiohttp', 'redis', 'python-multipart',
        'python-jose', 'passlib', 'bcrypt', 'cryptography',
        'pillow', 'qrcode', 'colorama', 'python-dotenv'
    ]
    
    missing_deps = []
    for dep in critical_deps:
        if not check_package(dep):
            missing_deps.append(dep)
            print(f"⚠️  Manquant: {dep}")
    
    if not missing_deps:
        print("✅ Toutes les dépendances critiques sont installées")
        return True
    
    print(f"\n📦 Installation de {len(missing_deps)} dépendances manquantes...")
    
    # Installer avec pip
    pip_cmd = f"{sys.executable} -m pip install {' '.join(missing_deps)}"
    if run_command(pip_cmd):
        print("✅ Dépendances installées avec succès")
        return True
    else:
        print("❌ Échec de l'installation des dépendances")
        return False

def check_system_tools():
    """Vérifie les outils système requis"""
    print("\n🔧 Vérification des outils système...")
    
    tools = ['git', 'python3', 'pip3', 'docker', 'cloudflared']
    missing_tools = []
    
    for tool in tools:
        if run_command(f"which {tool}", check=False):
            print(f"✅ {tool}")
        else:
            missing_tools.append(tool)
            print(f"❌ {tool}")
    
    return missing_tools

def install_system_tools():
    """Installe les outils système manquants"""
    missing_tools = check_system_tools()
    
    if not missing_tools:
        print("✅ Tous les outils système sont installés")
        return True
    
    print(f"\n🛠️  Installation des outils système manquants: {', '.join(missing_tools)}")
    
    # Détection de l'OS
    import platform
    os_name = platform.system().lower()
    
    install_commands = []
    
    if os_name == "darwin":  # macOS
        if 'git' in missing_tools or 'python3' in missing_tools:
            install_commands.append("brew update")
            install_commands.append("brew install git python3")
        if 'cloudflared' in missing_tools:
            install_commands.append("brew install cloudflared")
    
    elif os_name == "linux":
        # Détection de la distribution
        try:
            with open('/etc/os-release') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content:
                    install_commands.append("sudo apt update")
                    install_commands.append("sudo apt install -y git python3 python3-pip")
                    install_commands.append("sudo wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb")
                    install_commands.append("sudo dpkg -i cloudflared-linux-amd64.deb")
                elif 'arch' in content:
                    install_commands.append("sudo pacman -Syu --noconfirm git python python-pip")
                    install_commands.append("yay -S cloudflared")
        except:
            pass
    
    # Exécuter les commandes d'installation
    for cmd in install_commands:
        print(f"Exécution: {cmd}")
        if not run_command(cmd):
            print(f"❌ Échec de: {cmd}")
            return False
    
    print("✅ Outils système installés")
    return True

def main():
    """Point d'entrée principal"""
    print("=" * 50)
    print("VANTABLACK CORE v5 - INSTALLATION AUTOMATIQUE")
    print("=" * 50)
    
    # Vérifier et installer les dépendances Python
    if not install_missing_deps():
        print("\n❌ Échec de l'installation des dépendances Python")
        sys.exit(1)
    
    # Vérifier et installer les outils système
    if not install_system_tools():
        print("\n⚠️  Certains outils système manquent, mais l'installation peut continuer")
    
    print("\n" + "=" * 50)
    print("✅ INSTALLATION TERMINÉE")
    print("=" * 50)
    print("\nProchaines étapes:")
    print("1. Créer un environnement virtuel: python3 -m venv .venv")
    print("2. Activer: source .venv/bin/activate")
    print("3. Installer les requirements: pip install -r requirements.txt")
    print("4. Lancer: python setup.py")
    
    # Vérifier si on est dans un venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\n🎉 Vous êtes dans un environnement virtuel!")
    else:
        print("\n⚠️  Vous n'êtes pas dans un environnement virtuel")

if __name__ == "__main__":
    main()