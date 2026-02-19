"""
Vantablack Core v5 - Campaign Orchestrator
==========================================

This service manages the full lifecycle of a Red Team campaign:
- Playbook parsing (YAML DSL)
- Step execution (Delivery -> Edge -> Capture -> Mutation)
- State management and recovery
- Event coordination
"""

import yaml
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from core.edge.proxy import EdgeProxy, EdgeConfig, ProxyMode
from core.delivery.mailer import MailerService, DeliveryConfig, EmailTemplate
from core.orchestrator.autopilot import Autopilot

class CampaignState(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Playbook:
    name: str
    target_profile: str
    delivery_step: Dict[str, Any]
    edge_rules: Dict[str, Any]
    mutation_policy: str
    triggers: List[Dict[str, Any]]

class Orchestrator:
    """
    Central controller for campaign execution.
    """
    
    def __init__(self):
        self.campaigns: Dict[str, Any] = {}
        self.logger = logging.getLogger("vantablack.orchestrator")
        self.autopilot = Autopilot()
        self.proxy: Optional[EdgeProxy] = None
        self._running_campaigns: Dict[str, Dict] = {}
        
    def load_playbook(self, yaml_content: str) -> Playbook:
        """Parse YAML playbook into executable steps"""
        data = yaml.safe_load(yaml_content)
        return Playbook(
            name=data.get("name"),
            target_profile=data.get("target"),
            delivery_step=data.get("delivery"),
            edge_rules=data.get("edge"),
            mutation_policy=data.get("mutation", "adaptive"),
            triggers=data.get("triggers", [])
        )
        
    async def run_campaign(self, campaign_id: str, playbook: Playbook):
        """Execute a campaign based on the playbook"""
        self.logger.info(f"Starting campaign {campaign_id} with playbook {playbook.name}")
        self._running_campaigns[campaign_id] = {
            "state": CampaignState.RUNNING, 
            "playbook": playbook,
            "tasks": []
        }

        try:
            # 1. Configure Edge Proxy
            edge_conf = playbook.edge_rules or {}
            proxy_config = EdgeConfig(
                listen_host=edge_conf.get("listen_host", "0.0.0.0"),
                listen_port=edge_conf.get("listen_port", 443),
                mode=ProxyMode(edge_conf.get("mode", "reverse")),
                target_host=edge_conf.get("target_host", ""),
                tls_profile=edge_conf.get("tls_profile", "modern")
            )
            
            # Start Proxy
            phishlet_path = edge_conf.get("phishlet_path")
            if phishlet_path:
                self.proxy = EdgeProxy(proxy_config)
                proxy_task = asyncio.create_task(self.proxy.start(phishlet_path))
                self._running_campaigns[campaign_id]["tasks"].append(proxy_task)
                self.logger.info(f"Edge Proxy launched for campaign {campaign_id}")

            # 2. Start Autopilot Monitoring
            # TODO: Connect autopilot to proxy events
            
            # 3. Launch Delivery
            delivery_conf = playbook.delivery_step
            if delivery_conf:
                config = DeliveryConfig(
                    smtp_host=delivery_conf.get("smtp_host", "localhost"),
                    smtp_port=delivery_conf.get("smtp_port", 587),
                    username=delivery_conf.get("username", ""),
                    password=delivery_conf.get("password", ""),
                    use_tls=delivery_conf.get("use_tls", True)
                )
                mailer = MailerService(config)
                
                # Mock template/targets for now as they would come from profile
                template = EmailTemplate(
                    subject="Urgent Action Required",
                    html_content="<p>Click here</p>",
                    text_content="Click here",
                    sender_profile={"name": "Admin", "email": "admin@example.com"}
                )
                targets = [{"email": "victim@example.com"}] # Placeholder
                
                # In a real run, we'd start the worker and queue tasks
                # asyncio.create_task(mailer._worker())
                # await mailer.send_campaign(targets, template)
                self.logger.info(f"Delivery initialized for campaign {campaign_id}")

        except Exception as e:
            self.logger.error(f"Campaign failed to start: {e}")
            self._running_campaigns[campaign_id]["state"] = CampaignState.FAILED
            raise

    async def pause_campaign(self, campaign_id: str):
        """Pause execution safely"""
        if campaign_id in self._running_campaigns:
            self._running_campaigns[campaign_id]["state"] = CampaignState.PAUSED
            self.logger.info(f"Campaign {campaign_id} paused")
            # Logic to stop proxy/mailer would go here

    async def trigger_mutation(self, campaign_id: str, detection_event: Dict):
        """Handle detection event by mutating campaign assets"""
        await self.autopilot.process_event(detection_event)
