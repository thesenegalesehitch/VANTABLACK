from pydantic import BaseModel, Field, model_validator
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
    botSignals: List[str] = Field(default_factory=list)
    canvasHash: Optional[str] = None
    audioHash: Optional[str] = None
    webgl: Optional[WebGLInfo] = None
    webglHash: Optional[str] = None
    interaction: InteractionInfo
    
    @model_validator(mode="before")
    def _compat_transform(cls, values: Any):
        if not isinstance(values, dict):
            return values
        data = dict(values)
        if "user_agent" in data and "userAgent" not in data:
            data["userAgent"] = data.pop("user_agent")
        if "device_memory" in data and "deviceMemory" not in data:
            data["deviceMemory"] = data.pop("device_memory")
        if "hardware_concurrency" in data and "hardwareConcurrency" not in data:
            data["hardwareConcurrency"] = data.pop("hardware_concurrency")
        if "canvas_hash" in data and "canvasHash" not in data:
            data["canvasHash"] = data.pop("canvas_hash")
        if "audio_hash" in data and "audioHash" not in data:
            data["audioHash"] = data.pop("audio_hash")
        if "webgl_hash" in data and "webglHash" not in data:
            data["webglHash"] = data.pop("webgl_hash")
        # Screen
        if "screen" not in data:
            sw = data.pop("screen_width", None)
            sh = data.pop("screen_height", None)
            aw = data.pop("avail_width", None) or data.pop("availWidth", None)
            ah = data.pop("avail_height", None) or data.pop("availHeight", None)
            cd = data.pop("color_depth", None)
            pr = data.pop("pixel_ratio", None)
            if any(v is not None for v in (sw, sh, aw, ah, cd, pr)):
                data["screen"] = {
                    "width": sw or 0,
                    "height": sh or 0,
                    "availWidth": aw or (sw or 0),
                    "availHeight": ah or (sh or 0),
                    "colorDepth": cd or 0,
                    "pixelRatio": pr or 1.0,
                }
        # Window
        if "window" not in data:
            ww = data.pop("window_width", None)
            wh = data.pop("window_height", None)
            if ww is not None or wh is not None:
                data["window"] = {"width": ww or 0, "height": wh or 0}
            elif "screen" in data:
                # Default window size to screen size if available
                scr = data["screen"]
                data["window"] = {"width": scr.get("width", 0), "height": scr.get("height", 0)}
        # Timezone
        if "timezone" not in data:
            toff = data.pop("timezone_offset", None)
            tzname = data.pop("timezone_name", None)
            if toff is not None or tzname is not None:
                data["timezone"] = {"offset": toff or 0, "name": tzname or "unknown"}
        # WebGL
        if "webgl" not in data:
            vendor = data.pop("webgl_vendor", None)
            renderer = data.pop("webgl_renderer", None)
            if vendor is not None or renderer is not None:
                data["webgl"] = {"vendor": vendor, "renderer": renderer}
        # Interaction
        if "interaction" not in data:
            mm = data.pop("mouse_movements", None) or data.pop("mouseMoves", None)
            se = data.pop("scroll_events", None) or data.pop("scrollEvents", None)
            kp = data.pop("key_presses", None) or data.pop("keyPresses", None)
            top = data.pop("time_on_page", None) or data.pop("timeOnPage", None)
            if any(v is not None for v in (mm, se, kp, top)):
                data["interaction"] = {
                    "mouseMoves": mm or 0,
                    "scrollEvents": se or 0,
                    "keyPresses": kp or 0,
                    "timeOnPage": top or 0,
                }
        # Webdriver flag -> botSignals
        is_wd = data.pop("is_webdriver", None)
        if is_wd is True:
            bs = data.get("botSignals") or []
            if "webdriver" not in bs:
                bs.append("webdriver")
            data["botSignals"] = bs
        # Ignore extras
        data.pop("fonts_detected", None)
        data.pop("touch_support", None)
        return data

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
             except Exception: pass
             
        return True

# Instance globale
fp_validator = FingerprintValidator()
