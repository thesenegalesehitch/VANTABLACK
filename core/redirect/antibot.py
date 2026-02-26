import ipaddress
import re
from typing import List, Optional, Set, Dict, Any
from fastapi import Request
import os
from core.cache.redis_manager import redis_cache
from core.common.config import get

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
        r"Discordbot", r"WhatsApp", r"TelegramBot", r"SkypeUriPreview",
        r"HeadlessChrome", r"PhantomJS", r"Selenium", r"Puppeteer"
    }

    def __init__(self):
        self.bot_regex = re.compile("|".join(self.BOT_USER_AGENTS), re.IGNORECASE)
        self.datacenter_networks = []
        
        # Load Datacenter CIDRs
        self.load_blacklist("core/config/datacenter_cidrs.txt")
        
        # Load external blacklist if exists
        self.load_blacklist("core/config/blacklist_ips.txt")

    def load_blacklist(self, file_path: str):
        """Charge une liste d'IPs/CIDR depuis un fichier texte (une entrée par ligne)."""
        if not os.path.exists(file_path):
             # Create directory if it doesn't exist
             os.makedirs(os.path.dirname(file_path), exist_ok=True)
             if not os.path.exists(file_path):
                 print(f"[ANTIBOT Info] Blacklist file not found: {file_path}")
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
            nets = self.datacenter_networks
            if not nets:
                nets = [
                    ipaddress.ip_network("3.0.0.0/9"),
                    ipaddress.ip_network("13.52.0.0/14"),
                    ipaddress.ip_network("52.0.0.0/11"),
                    ipaddress.ip_network("34.0.0.0/8"),
                    ipaddress.ip_network("35.0.0.0/8"),
                    ipaddress.ip_network("40.64.0.0/10"),
                    ipaddress.ip_network("104.40.0.0/13"),
                ]
            for network in nets:
                if ip_obj in network:
                    return True
        except ValueError:
            return False  # IP invalide
        return False

    async def check_request(self, request: Request) -> Dict[str, Any]:
        """
        Analyse complète de la requête pour détecter les bots.
        Retourne un dict avec le résultat et la raison.
        """
        # Support Reverse Proxies (Cloudflare, Tunnels)
        client_ip = request.headers.get("cf-connecting-ip") or request.client.host
        user_agent = request.headers.get("user-agent", "")
        mode = (get("ANTIBOT_MODE") or "standard").lower()
        
        cache_key = f"antibot:ip:{client_ip}"
        
        # Check Redis Cache for previous decision
        try:
            cached_result = redis_cache.get(cache_key)
            if cached_result:
                # If cached_result is bytes/string, parse it? No, redis_cache.get usually returns python object if json serialized
                # But here we assume it returns the dict we stored.
                return cached_result
        except Exception as e:
            print(f"[ANTIBOT Warning] Cache read error: {e}")
        
        result = {"blocked": False, "reason": "Clean", "type": "clean"}

        # 1. Vérification User-Agent
        if self.is_bot_user_agent(user_agent):
            result = {"blocked": True, "reason": "Bot User-Agent detected", "type": "bot_ua"}
        
        # 2. Vérification IP Datacenter
        elif mode != "relaxed" and self.is_datacenter_ip(client_ip):
            result = {"blocked": True, "reason": "Datacenter IP detected", "type": "datacenter_ip"}

        # 3. Vérification Headers suspects (Headless Chrome, Automation tools)
        elif mode != "relaxed" and self._has_suspicious_headers(request):
             result = {"blocked": True, "reason": "Suspicious headers detected", "type": "suspicious_headers"}

        # Cache the result for 5 minutes (300 seconds)
        try:
            redis_cache.set(cache_key, result, expire=300)
        except Exception as e:
            print(f"[ANTIBOT Warning] Cache write error: {e}")
        
        return result

    def _has_suspicious_headers(self, request: Request) -> bool:
        """Détecte les indicateurs de navigateurs automatisés (Puppeteer, Selenium, etc.)."""
        headers = request.headers
        user_agent = headers.get("user-agent", "").lower()
        
        # Reverse proxy/tunnel friendly: if coming via Cloudflare, relax checks
        if "cf-connecting-ip" in headers or "cf-ray" in headers:
            return False
        
        # Check 1: Missing common browser headers
        # Modern browsers almost always send these
        common_headers = ["accept-language", "accept-encoding"]
        for h in common_headers:
            if h not in headers:
                return True
                
        # Check 2: Explicit automation indicators
        if "webdriver" in user_agent:
            return True
        if headers.get("webdriver") == "true" or headers.get("navigator-webdriver") == "true":
            return True
            
        # Check 3: Headless Chrome specific
        if "headlesschrome" in user_agent:
            return True
            
        # Check 4: Sec-CH-UA (Client Hints) consistency
        # If User-Agent claims to be Chrome/Edge but no sec-ch-ua headers, it's suspicious
        # (Though some very old versions might not send it, we target modern victims)
        if "chrome" in user_agent and "sec-ch-ua" not in headers and "electron" not in user_agent:
            # Check version, if > 90 it should have hints. 
            # Simplified: just flag if missing on clear chrome UA.
            # But let's be careful with false positives.
            pass 

        return False

# Instance globale
antibot = AntiBotSystem()
