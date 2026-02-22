from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from fastapi import Request

class BrowserFingerprint(BaseModel):
    """
    Structure de données pour l'empreinte digitale du navigateur.
    Collecté via JavaScript côté client.
    """
    user_agent: str
    screen_width: int = Field(ge=0)
    screen_height: int = Field(ge=0)
    color_depth: int = Field(ge=0)
    platform: str
    language: str
    timezone_offset: int
    webgl_vendor: Optional[str] = None
    webgl_renderer: Optional[str] = None
    canvas_hash: Optional[str] = None
    fonts_detected: List[str] = Field(default_factory=list)
    touch_support: bool = False
    
    # Indicateurs de mouvement
    mouse_movements: int = 0
    scroll_events: int = 0
    time_on_page: int = 0  # ms

class FingerprintValidator:
    """
    Validateur de fingerprint pour détecter les bots headless/émulés.
    """
    
    def validate(self, fp: BrowserFingerprint) -> bool:
        """
        Vérifie si l'empreinte semble humaine.
        Retourne True si valide (humain), False si suspect (bot).
        """
        
        # 1. Vérification Résolution (Headless souvent 800x600 ou 0x0)
        if fp.screen_width < 100 or fp.screen_height < 100:
            return False  # Trop petit -> Suspect (Headless)
            
        # 2. Vérification WebGL (Souvent vide ou générique sur VM/Headless)
        if not fp.webgl_renderer or "SwiftShader" in fp.webgl_renderer or "llvmpipe" in fp.webgl_renderer:
             # SwiftShader/llvmpipe sont des rendus software typiques de VM/Headless
             return False

        # 3. Vérification Comportement Humain (Mouvements souris/scroll)
        # Un bot clique directement sans mouvement ou scroll (sauf bot très avancé)
        if fp.mouse_movements < 5 and fp.scroll_events == 0 and fp.time_on_page < 500:
            return False  # Trop rapide/statique -> Suspect
            
        # 4. Vérification Platform vs User-Agent
        if "MacIntel" in fp.platform and "Windows" in fp.user_agent:
            return False  # Incohérence -> Suspect (Spoofing UA)
            
        return True

# Instance globale
fp_validator = FingerprintValidator()
