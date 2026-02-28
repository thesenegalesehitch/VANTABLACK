"""
Vantablack Core v5 - Internationalization System
Système de traduction français/anglais pour l'interface utilisateur
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path

class I18N:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.locales_dir = self.project_root / "core" / "locales"
        self.current_language = "fr"  # Default language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Charge les traductions depuis les fichiers JSON"""
        translations = {}
        
        # Charger français
        fr_file = self.locales_dir / "fr.json"
        if fr_file.exists():
            with open(fr_file, 'r', encoding='utf-8') as f:
                translations["fr"] = json.load(f)
        
        # Charger anglais
        en_file = self.locales_dir / "en.json"
        if en_file.exists():
            with open(en_file, 'r', encoding='utf-8') as f:
                translations["en"] = json.load(f)
        
        return translations
    
    def set_language(self, lang: str):
        """Définit la langue courante"""
        if lang in self.translations:
            self.current_language = lang
        else:
            self.current_language = "en"  # Fallback to English
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Retourne la traduction pour la clé donnée"""
        if self.current_language in self.translations:
            return self.translations[self.current_language].get(key, default or key)
        return default or key
    
    def get_banner(self) -> str:
        """Retourne la bannière dans la langue courante"""
        banner = """
  █████╗ ██╗     ███████╗██╗  ██╗ 
 ██╔══██╗██║     ██╔════╝╚██╗██╔╝ 
 ███████║██║     █████╗   ╚███╔╝  
 ██╔══██║██║     ██╔══╝   ██╔██╗  
 ██║  ██║███████╗███████╗██╔╝ ██╗ 
 ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ 

        V A N T A B L A C K
     THESENEGALESEHITCH
"""
        
        if self.current_language == "fr":
            return banner + "\n═══════════════════════════════════════════\nChargement des modules...\n═══════════════════════════════════════════"
        else:
            return banner + "\n═══════════════════════════════════════════\nLoading modules...\n═══════════════════════════════════════════"

# Instance globale
i18n = I18N()

def t(key: str, default: Optional[str] = None, **kwargs) -> str:
    """Fonction helper pour accéder aux traductions avec formatage"""
    translation = i18n.get(key, default)
    if translation and kwargs:
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation
    return translation
