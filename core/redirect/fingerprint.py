from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Union

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
    audio_hash: Optional[str] = None
    fonts_detected: List[str] = Field(default_factory=list)
    touch_support: bool = False
    max_touch_points: int = 0
    hardware_concurrency: Optional[Union[str, int]] = None
    device_memory: Optional[Union[str, float, int]] = None
    pixel_ratio: float = 1.0
    is_webdriver: bool = False
    
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

        # 2. Vérification Webdriver (Selenium, Puppeteer)
        if fp.is_webdriver:
            return False  # Bot détecté explicitement
            
        # 3. Vérification WebGL (Souvent vide ou générique sur VM/Headless)
        if not fp.webgl_renderer or "SwiftShader" in fp.webgl_renderer or "llvmpipe" in fp.webgl_renderer:
             # SwiftShader/llvmpipe sont des rendus software typiques de VM/Headless
             return False

        # 4. Vérification Comportement Humain (Mouvements souris/scroll)
        # Un bot clique directement sans mouvement ou scroll (sauf bot très avancé)
        # Note: Sur une page de redirection rapide, l'utilisateur n'a pas le temps de bouger.
        # On désactive cette vérification pour éviter les faux positifs sur les connexions rapides.
        # if fp.mouse_movements < 5 and fp.scroll_events == 0 and fp.time_on_page < 500:
        #    return False  # Trop rapide/statique -> Suspect
            
        # 5. Vérification Platform vs User-Agent
        if "MacIntel" in fp.platform and "Windows" in fp.user_agent:
            return False  # Incohérence -> Suspect (Spoofing UA)
            
        # 6. Vérification Fonts (Headless a souvent peu/pas de fonts)
        if len(fp.fonts_detected) == 0 and "Linux" not in fp.platform and "Android" not in fp.user_agent:
            # Linux peut parfois masquer les fonts, mais Windows/Mac ont toujours des fonts standard
            return False
            
        # 7. Hardware Concurrency (Headless often reports undefined or low)
        if fp.hardware_concurrency and fp.hardware_concurrency != 'unknown':
            try:
                concurrency = int(fp.hardware_concurrency)
                if concurrency < 1:
                     return False
            except ValueError:
                pass # Ignorer si format invalide

        # 8. Device Memory (Headless often reports undefined or low)
        if fp.device_memory and fp.device_memory != 'unknown':
             try:
                 memory = float(fp.device_memory)
                 if memory < 0.25: # < 256MB
                     return False
             except ValueError:
                 pass # Ignorer si format invalide
            
        return True

# Instance globale
fp_validator = FingerprintValidator()
