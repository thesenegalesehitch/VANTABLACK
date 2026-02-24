from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Any

class ScreenInfo(BaseModel):
    width: int = 0
    height: int = 0
    availWidth: int = 0
    availHeight: int = 0
    colorDepth: int = 0
    pixelRatio: float = 1.0

class WindowInfo(BaseModel):
    width: int = 0
    height: int = 0

class TimezoneInfo(BaseModel):
    offset: int = 0
    name: str = "unknown"

class WebGLInfo(BaseModel):
    vendor: Optional[str] = None
    renderer: Optional[str] = None
    extensions: Optional[List[str]] = None
    shadingLanguageVersion: Optional[str] = None
    version: Optional[str] = None
    precision: Optional[Dict[str, Any]] = None

class InteractionInfo(BaseModel):
    mouseMoves: int = 0
    scrollEvents: int = 0
    keyPresses: int = 0
    timeOnPage: int = 0

class BrowserFingerprint(BaseModel):
    """
    Structure de données pour l'empreinte digitale du navigateur (V5).
    """
    userAgent: str
    language: str
    platform: str
    hardwareConcurrency: Union[str, int] = "unknown"
    deviceMemory: Union[str, float, int] = "unknown"
    screen: ScreenInfo
    window: WindowInfo
    timezone: TimezoneInfo
    botSignals: List[str] = []
    canvasHash: Optional[str] = None
    audioHash: Optional[str] = None
    webgl: Optional[WebGLInfo] = None
    webglHash: Optional[str] = None
    interaction: InteractionInfo

class FingerprintValidator:
    """
    Validateur de fingerprint pour détecter les bots headless/émulés.
    """
    
    def validate(self, fp: BrowserFingerprint) -> bool:
        """
        Vérifie si l'empreinte semble humaine.
        Retourne True si valide (humain), False si suspect (bot).
        """
        
        # 1. Bot Signals (Explicit)
        if fp.botSignals:
            # If any bot signal is present, block
            print(f"[FP Validator] Bot Signals Detected: {fp.botSignals}")
            return False

        # 2. Screen Dimensions (Headless often 800x600 or 0x0)
        if fp.screen.width < 100 or fp.screen.height < 100:
             return False

        if fp.screen.width < fp.screen.availWidth or fp.screen.height < fp.screen.availHeight:
             # Impossible physically
             return False

        # 3. WebGL Check
        if fp.webgl:
            renderer = (fp.webgl.renderer or "").lower()
            vendor = (fp.webgl.vendor or "").lower()
            if "swiftshader" in renderer or "llvmpipe" in renderer or "software" in renderer:
                 return False
            if "google" in vendor and "google" in renderer and "intel" not in renderer and "nvidia" not in renderer and "amd" not in renderer:
                 # Often indicative of cloud headless instance (though Chrome sometimes reports Google Inc.)
                 # Checking for specific lack of GPU branding
                 pass

        # 4. Consistency Check (Platform vs UA)
        if "MacIntel" in fp.platform and "Windows" in fp.userAgent:
             return False
             
        # 5. Hardware Concurrency
        if fp.hardwareConcurrency != 'unknown':
            try:
                concurrency = int(fp.hardwareConcurrency)
                if concurrency < 1: return False
            except: pass

        # 6. Device Memory
        if fp.deviceMemory != 'unknown':
             try:
                 memory = float(fp.deviceMemory)
                 if memory < 0.25: return False
             except: pass
             
        return True

# Instance globale
fp_validator = FingerprintValidator()
