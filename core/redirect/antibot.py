import ipaddress
import re
from typing import List, Optional, Set, Dict
from fastapi import Request
import os
from core.cache.redis_manager import redis_cache

class AntiBotSystem:
    """
    Système Anti-Bot Avancé Vantablack v5
    Détecte et bloque les scanners, bots, et IPs de datacenters.
    """
    
    # User-Agents connus de bots et scanners
    BOT_USER_AGENTS = {
        r"Googlebot", r"Bingbot", r"Slurp", r"DuckDuckBot", r"Baiduspider",
        r"YandexBot", r"Sogou", r"Exabot", r"facebot", r"facebookexternalhit",
        r"ia_archiver", r"curl", r"wget", r"python-requests", r"libwww-perl",
        r"urllib", r"Scrapy", r"Nmap", r"Zgrab", r"Masscan", r"Go-http-client",
        r"censys", r"shodan", r"virustotal", r"PhishTank", r"Google-Read-Aloud",
        r"Barkrowler", r"Bot", r"Crawler", r"Spider", r"Mediapartners-Google",
        r"AdsBot-Google", r"Twitterbot", r"Slackbot-LinkExpanding", r"Applebot",
        r"Discordbot", r"WhatsApp", r"TelegramBot", r"SkypeUriPreview"
    }

    # Plages IP connues de datacenters (Exemple simplifié - à enrichir avec une DB réelle)
    # AWS, Azure, Google Cloud, DigitalOcean ranges mockées pour l'exemple
    DATACENTER_RANGES = [
        "3.0.0.0/9", "13.0.0.0/8", "18.0.0.0/8",  # AWS partial
        "20.0.0.0/10", "40.0.0.0/8",              # Azure partial
        "34.0.0.0/10", "35.0.0.0/8",              # GCP partial
        "104.16.0.0/12",                          # Cloudflare (si pas whiteliste)
    ]

    def __init__(self):
        self.bot_regex = re.compile("|".join(self.BOT_USER_AGENTS), re.IGNORECASE)
        self.datacenter_networks = []
        # Load default ranges
        for cidr in self.DATACENTER_RANGES:
            try:
                self.datacenter_networks.append(ipaddress.ip_network(cidr))
            except ValueError:
                pass

    def load_blacklist(self, file_path: str):
        """Charge une liste d'IPs/CIDR depuis un fichier texte (une entrée par ligne)."""
        if not os.path.exists(file_path):
             # Create directory if it doesn't exist
             os.makedirs(os.path.dirname(file_path), exist_ok=True)
             # Create empty file
             with open(file_path, 'w') as f:
                 f.write("# Add malicious IP ranges here (CIDR format)\n")
             print(f"[ANTIBOT Info] Created empty blacklist file: {file_path}")
             return

        try:
            count = 0
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        self.datacenter_networks.append(ipaddress.ip_network(line))
                        count += 1
                    except ValueError:
                        continue # Ignorer les lignes invalides
            print(f"[ANTIBOT] Loaded {count} rules from {file_path}")
        except Exception as e:
            print(f"[ANTIBOT Error] Failed to load blacklist: {e}")

    def is_bot_user_agent(self, user_agent: str) -> bool:
        """Vérifie si le User-Agent correspond à un bot connu."""
        if not user_agent or len(user_agent) < 5:
            return True  # UA vide ou trop court = suspect
        return bool(self.bot_regex.search(user_agent))

    def is_datacenter_ip(self, ip: str) -> bool:
        """Vérifie si l'IP appartient à un datacenter connu (AWS, Azure, GCP, etc.)."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for network in self.datacenter_networks:
                if ip_obj in network:
                    return True
        except ValueError:
            return False  # IP invalide
        return False

    async def check_request(self, request: Request) -> Dict[str, any]:
        """
        Analyse complète de la requête pour détecter les bots.
        Retourne un dict avec le résultat et la raison.
        """
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Check Redis Cache first
        cache_key = f"antibot:ip:{client_ip}"
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        result = {"blocked": False, "reason": "Clean", "type": "clean"}

        # 1. Vérification User-Agent
        if self.is_bot_user_agent(user_agent):
            result = {"blocked": True, "reason": "Bot User-Agent detected", "type": "bot_ua"}
        
        # 2. Vérification IP Datacenter
        elif self.is_datacenter_ip(client_ip):
            result = {"blocked": True, "reason": "Datacenter IP detected", "type": "datacenter_ip"}

        # 3. Vérification Headers suspects (Headless Chrome, Automation tools)
        elif self._has_suspicious_headers(request):
             result = {"blocked": True, "reason": "Suspicious headers detected", "type": "suspicious_headers"}

        # Cache the result for 5 minutes
        redis_cache.set(cache_key, result, expire=300)
        
        return result

    def _has_suspicious_headers(self, request: Request) -> bool:
        """Détecte les indicateurs de navigateurs automatisés (Puppeteer, Selenium, etc.)."""
        headers = request.headers
        
        # Manque de headers standards pour un navigateur moderne
        required_headers = ["accept-language", "accept-encoding", "user-agent"]
        for h in required_headers:
            if h not in headers:
                return True
            
        # Indicateurs explicites d'outils d'automatisation
        if "webdriver" in headers.get("user-agent", "").lower():
            return True
        if headers.get("webdriver") == "true" or headers.get("navigator-webdriver") == "true":
            return True
            
        # Headless Chrome specific
        if "HeadlessChrome" in headers.get("user-agent", ""):
            return True
            
        return False

# Instance globale
antibot = AntiBotSystem()
# Chargement optionnel d'une blacklist externe
antibot.load_blacklist("data/ip_blacklist.txt")
