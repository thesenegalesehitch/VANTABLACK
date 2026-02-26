#!/usr/bin/env python3
"""
Vantablack Core v5 - Setup System Complet
Système interactif de configuration et installation automatique
"""

import os
import sys
import platform
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class SetupSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / ".venv"
        self.os_type = self.detect_os()
        self.python_cmd = self.find_python()
        
    def detect_os(self) -> str:
        """Détecte le système d'exploitation"""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            # Détecter la distribution Linux
            try:
                with open('/etc/os-release') as f:
                    content = f.read().lower()
                    if 'ubuntu' in content:
                        return "ubuntu"
                    elif 'debian' in content:
                        return "debian"
                    elif 'arch' in content:
                        return "arch"
                    elif 'fedora' in content or 'redhat' in content:
                        return "fedora"
            except:
                pass
            return "linux"
        return "unknown"
    
    def find_python(self) -> str:
        """Trouve la commande Python appropriée"""
        # Essayer python3 d'abord
        for cmd in ['python3', 'python3.11', 'python3.12', 'python']:
            if shutil.which(cmd):
                try:
                    result = subprocess.run([cmd, '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"{Colors.GREEN}✓ Python trouvé: {cmd} ({version}){Colors.RESET}")
                        return cmd
                except:
                    continue
        return None
    
    def check_requirements(self) -> Dict[str, bool]:
        """Vérifie les prérequis système"""
        requirements = {
            'python': bool(self.python_cmd),
            'pip': self.check_command('pip3') or self.check_command('pip'),
            'git': self.check_command('git'),
            'docker': self.check_command('docker'),
            'cloudflared': self.check_command('cloudflared'),
        }
        return requirements
    
    def check_command(self, cmd: str) -> bool:
        """Vérifie si une commande est disponible"""
        return shutil.which(cmd) is not None
    
    def install_system_deps(self):
        """Installe les dépendances système selon l'OS"""
        print(f"{Colors.BLUE}📦 Installation des dépendances système...{Colors.RESET}")
        
        if self.os_type == "macos":
            self.run_command("brew update")
            self.run_command("brew install python3 git cloudflared")
            
        elif self.os_type == "ubuntu" or self.os_type == "debian":
            self.run_command("sudo apt update")
            self.run_command("sudo apt install -y python3 python3-pip python3-venv git wget")
            # Installer cloudflared
            self.run_command("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb")
            self.run_command("sudo dpkg -i cloudflared-linux-amd64.deb")
            
        elif self.os_type == "arch":
            self.run_command("sudo pacman -Syu --noconfirm python python-pip git")
            self.run_command("yay -S cloudflared")
            
        elif self.os_type == "fedora":
            self.run_command("sudo dnf install -y python3 python3-pip git wget")
            self.run_command("sudo wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-x86_64.rpm")
            self.run_command("sudo rpm -i cloudflared-linux-x86_64.rpm")
    
    def create_venv(self):
        """Crée l'environnement virtuel"""
        if self.venv_path.exists():
            print(f"{Colors.YELLOW}⚠ Environnement virtuel existe déjà{Colors.RESET}")
            return True
            
        print(f"{Colors.BLUE}🐍 Création de l'environnement virtuel...{Colors.RESET}")
        cmd = [self.python_cmd, "-m", "venv", str(self.venv_path)]
        return self.run_command(cmd)
    
    def install_python_deps(self):
        """Installe les dépendances Python"""
        print(f"{Colors.BLUE}📦 Installation des dépendances Python...{Colors.RESET}")
        
        pip_cmd = self.get_venv_pip()
        if not pip_cmd:
            print(f"{Colors.RED}❌ Pip non trouvé dans le venv{Colors.RESET}")
            return False
        
        # Installer les requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            cmd = [pip_cmd, "install", "-r", str(requirements_file)]
            return self.run_command(cmd)
        
        return False
    
    def get_venv_pip(self) -> Optional[str]:
        """Retourne le chemin vers pip dans le venv"""
        if self.os_type == "windows":
            pip_path = self.venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = self.venv_path / "bin" / "pip"
        
        return str(pip_path) if pip_path.exists() else None
    
    def run_command(self, cmd, check=True) -> bool:
        """Exécute une commande et retourne le succès"""
        if isinstance(cmd, str):
            cmd = cmd.split()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode != 0 and check:
                print(f"{Colors.RED}❌ Erreur: {result.stderr}{Colors.RESET}")
                return False
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Exception: {e}{Colors.RESET}")
            return False
    
    def show_menu(self):
        """Affiche le menu interactif"""
        while True:
            print(f"\n{Colors.BOLD}{Colors.CYAN}=== VANTABLACK CORE v5 - MENU PRINCIPAL ==={Colors.RESET}")
            print(f"{Colors.GREEN}1.{Colors.RESET} Installation complète automatique")
            print(f"{Colors.GREEN}2.{Colors.RESET} Vérifier les prérequis")
            print(f"{Colors.GREEN}3.{Colors.RESET} Installer dépendances système")
            print(f"{Colors.GREEN}4.{Colors.RESET} Créer environnement virtuel")
            print(f"{Colors.GREEN}5.{Colors.RESET} Installer dépendances Python")
            print(f"{Colors.GREEN}6.{Colors.RESET} Tester l'installation")
            print(f"{Colors.GREEN}7.{Colors.RESET} Lancer le serveur phishing")
            print(f"{Colors.GREEN}8.{Colors.RESET} Générer QR Code (Quishing)")
            print(f"{Colors.GREEN}9.{Colors.RESET} Configuration avancée")
            print(f"{Colors.GREEN}0.{Colors.RESET} Quitter")
            
            choice = input(f"\n{Colors.YELLOW}➤ Choisissez une option (0-9): {Colors.RESET}").strip()
            
            if choice == "1":
                self.full_install()
            elif choice == "2":
                self.check_prerequisites()
            elif choice == "3":
                self.install_system_deps()
            elif choice == "4":
                self.create_venv()
            elif choice == "5":
                self.install_python_deps()
            elif choice == "6":
                self.test_installation()
            elif choice == "7":
                self.launch_phishing_server()
            elif choice == "8":
                self.generate_qr_code()
            elif choice == "9":
                self.advanced_config()
            elif choice == "0":
                print(f"{Colors.GREEN}👋 Au revoir!{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}❌ Option invalide{Colors.RESET}")
    
    def full_install(self):
        """Installation complète automatique"""
        print(f"{Colors.BOLD}🚀 Installation complète automatique{Colors.RESET}")
        
        steps = [
            ("Vérification des prérequis", self.check_prerequisites),
            ("Installation dépendances système", self.install_system_deps),
            ("Création environnement virtuel", self.create_venv),
            ("Installation dépendances Python", self.install_python_deps),
            ("Test de l'installation", self.test_installation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{Colors.BLUE}▶ {step_name}...{Colors.RESET}")
            if not step_func():
                print(f"{Colors.RED}❌ Échec à l'étape: {step_name}{Colors.RESET}")
                return False
            time.sleep(1)
        
        print(f"\n{Colors.GREEN}✅ Installation complète réussie!{Colors.RESET}")
        return True
    
    def check_prerequisites(self):
        """Vérifie tous les prérequis"""
        print(f"{Colors.BLUE}🔍 Vérification des prérequis...{Colors.RESET}")
        
        reqs = self.check_requirements()
        all_ok = True
        
        for req, available in reqs.items():
            status = "✓" if available else "✗"
            color = Colors.GREEN if available else Colors.RED
            print(f"  {color}{status} {req}{Colors.RESET}")
            if not available:
                all_ok = False
        
        if not all_ok:
            print(f"{Colors.YELLOW}⚠ Certains prérequis manquent. Utilisez l'option 3 pour les installer.{Colors.RESET}")
        
        return all_ok
    
    def test_installation(self):
        """Teste l'installation complète"""
        print(f"{Colors.BLUE}🧪 Test de l'installation...{Colors.RESET}")
        
        tests = [
            ("Test Python", [self.get_venv_python(), "--version"]),
            ("Test Import API", [self.get_venv_python(), "-c", "import api.rest_api; print('API OK')"]),
            ("Test Import Core", [self.get_venv_python(), "-c", "import core; print('Core OK')"]),
        ]
        
        all_passed = True
        for test_name, cmd in tests:
            if self.run_command(cmd, check=False):
                print(f"  {Colors.GREEN}✓ {test_name}{Colors.RESET}")
            else:
                print(f"  {Colors.RED}✗ {test_name}{Colors.RESET}")
                all_passed = False
        
        return all_passed
    
    def get_venv_python(self) -> Optional[str]:
        """Retourne le chemin vers python dans le venv"""
        if self.os_type == "windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
        
        return str(python_path) if python_path.exists() else None
    
    def launch_phishing_server(self):
        """Lance le serveur phishing"""
        python_cmd = self.get_venv_python()
        if not python_cmd:
            print(f"{Colors.RED}❌ Python du venv non trouvé{Colors.RESET}")
            return
        
        print(f"{Colors.BLUE}🌐 Lancement du serveur phishing...{Colors.RESET}")
        print(f"{Colors.YELLOW}Targets disponibles: google, microsoft, facebook, twitter{Colors.RESET}")
        target = input(f"{Colors.YELLOW}➤ Choisissez une target: {Colors.RESET}").strip() or "google"
        
        cmd = [python_cmd, "phishing_server.py", "--target", target, "--port", "8080", "--stealth"]
        print(f"{Colors.CYAN}Commande: {' '.join(cmd)}{Colors.RESET}")
        
        # Exécuter en arrière-plan
        try:
            subprocess.Popen(cmd, cwd=self.project_root)
            print(f"{Colors.GREEN}✅ Serveur démarré sur http://localhost:8080{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
    
    def generate_qr_code(self):
        """Génère un QR Code pour le quishing"""
        python_cmd = self.get_venv_python()
        if not python_cmd:
            print(f"{Colors.RED}❌ Python du venv non trouvé{Colors.RESET}")
            return
        
        url = input(f"{Colors.YELLOW}➤ URL pour le QR Code: {Colors.RESET}").strip()
        if not url:
            print(f"{Colors.RED}❌ URL requise{Colors.RESET}")
            return
        
        logo_path = self.project_root / "core" / "assets" / "logos"
        logos = list(logo_path.glob("*.png")) + list(logo_path.glob("*.svg"))
        
        if logos:
            print(f"{Colors.YELLOW}Logos disponibles:{Colors.RESET}")
            for i, logo in enumerate(logos[:10]):  # Limiter à 10 logos
                print(f"  {i}: {logo.name}")
            
            logo_choice = input(f"{Colors.YELLOW}➤ Choisissez un logo (numéro): {Colors.RESET}").strip()
            try:
                logo_index = int(logo_choice)
                selected_logo = logos[logo_index]
            except:
                selected_logo = None
        else:
            selected_logo = None
        
        cmd = [python_cmd, "quishing.py", "--url", url]
        if selected_logo:
            cmd.extend(["--logo", str(selected_logo)])
        
        print(f"{Colors.CYAN}Génération du QR Code...{Colors.RESET}")
        self.run_command(cmd)
    
    def advanced_config(self):
        """Menu de configuration avancée"""
        print(f"\n{Colors.BOLD}⚙️ Configuration Avancée{Colors.RESET}")
        print(f"{Colors.GREEN}1.{Colors.RESET} Configurer Cloudflare Tunnel")
        print(f"{Colors.GREEN}2.{Colors.RESET} Configurer les phishlets")
        print(f"{Colors.GREEN}3.{Colors.RESET} Configurer le reverse proxy")
        print(f"{Colors.GREEN}4.{Colors.RESET} Tests de sécurité")
        
        choice = input(f"{Colors.YELLOW}➤ Option: {Colors.RESET}").strip()
        
        if choice == "1":
            self.setup_cloudflare_tunnel()
        elif choice == "2":
            self.configure_phishlets()
        elif choice == "3":
            self.setup_reverse_proxy()
        elif choice == "4":
            self.run_security_tests()
    
    def setup_cloudflare_tunnel(self):
        """Configure Cloudflare Tunnel"""
        print(f"{Colors.BLUE}🌐 Configuration Cloudflare Tunnel...{Colors.RESET}")
        
        if not self.check_command("cloudflared"):
            print(f"{Colors.RED}❌ Cloudflared non installé{Colors.RESET}")
            return
        
        # Configuration automatique
        config_content = """url: http://localhost:8080
credentials-file: .cloudflared/cert.pem
"""
        
        config_dir = self.project_root / ".cloudflared"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "config.yml"
        config_file.write_text(config_content)
        
        print(f"{Colors.GREEN}✅ Configuration créée: {config_file}{Colors.RESET}")
        print(f"{Colors.YELLOW}Pour lancer: cloudflared tunnel --config {config_file}{Colors.RESET}")
    
    def configure_phishlets(self):
        """Configure les phishlets"""
        print(f"{Colors.BLUE}🎣 Configuration des phishlets...{Colors.RESET}")
        
        phishlets_dir = self.project_root / "phishlets"
        if phishlets_dir.exists():
            phishlets = list(phishlets_dir.glob("*.yaml"))
            print(f"{Colors.GREEN}Phishlets disponibles:{Colors.RESET}")
            for phishlet in phishlets:
                print(f"  - {phishlet.name}")
        
        print(f"{Colors.YELLOW}Utilisez: python phishing_server.py --target <nom_phishlet>{Colors.RESET}")
    
    def run_security_tests(self):
        """Exécute les tests de sécurité"""
        python_cmd = self.get_venv_python()
        if not python_cmd:
            print(f"{Colors.RED}❌ Python du venv non trouvé{Colors.RESET}")
            return
        
        print(f"{Colors.BLUE}🔒 Exécution des tests de sécurité...{Colors.RESET}")
        
        tests = [
            ("Test Fingerprint", [python_cmd, "-m", "pytest", "core/tests/test_fingerprint_validator.py", "-v"]),
            ("Test API", [python_cmd, "-m", "pytest", "core/tests/test_api_integration_flow.py", "-v"]),
            ("Test Templates", [python_cmd, "-m", "pytest", "core/tests/test_templates_rendering.py", "-v"]),
        ]
        
        for test_name, cmd in tests:
            print(f"\n{Colors.CYAN}▶ {test_name}{Colors.RESET}")
            self.run_command(cmd)

def main():
    """Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}"""
    ██╗   ██╗ █████╗ ███╗   ██╗████████╗ █████╗ ██████╗ ██╗      █████╗  ██████╗██╗  ██╗
    ██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝
    ██║   ██║███████║██╔██╗ ██║   ██║   ███████║██████╔╝██║     ███████║██║     █████╔╝ 
    ╚██╗ ██╔╝██╔══██║██║╚██╗██║   ██║   ██╔══██║██╔══██╗██║     ██╔══██║██║     ██╔═██╗ 
     ╚████╔╝ ██║  ██║██║ ╚████║   ██║   ██║  ██║██████╔╝███████╗██║  ██║╚██████╗██║  ██╗
      ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
    """ + Colors.RESET)
    
    print(f"{Colors.BOLD}Vantablack Core v5 - Setup System{Colors.RESET}")
    print(f"{Colors.YELLOW}Système de configuration automatique et interactif{Colors.RESET}")
    
    setup = SetupSystem()
    setup.show_menu()

if __name__ == "__main__":
    main()