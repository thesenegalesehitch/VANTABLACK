
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from core.web.server import create_app
from core.redirect.fingerprint import BrowserFingerprint, fp_validator

app = create_app()
client = TestClient(app)

@pytest.fixture
def mock_redis():
    with patch("core.cache.redis_manager.redis_cache") as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        yield mock

def test_fast_redirect_fingerprint_validation():
    """Test validation passes for fast redirects (low time, no mouse movement)."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="MacIntel",
        language="en-US",
        timezone_offset=0,
        webgl_vendor="Google Inc. (Apple)",
        webgl_renderer="ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
        canvas_hash="somehash",
        fonts_detected=["Arial", "Times New Roman"],
        touch_support=False,
        mouse_movements=0,  # No movement
        scroll_events=0,    # No scroll
        time_on_page=100,   # Very fast (100ms)
        is_webdriver=False,
        hardware_concurrency="8",
        device_memory="8"
    )
    # This should pass now that we relaxed the check
    assert fp_validator.validate(fp) is True

def test_verify_fingerprint_endpoint(mock_redis):
    """Test the API endpoint handles JS payload correctly."""
    
    # Payload similar to what JS sends (with extra fields)
    payload = {
        "campaign_id": "test-campaign",
        "session_id": "test-session",
        "fingerprint": {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "platform": "MacIntel",
            "language": "en-US",
            "languages": ["en-US", "en"], # Extra field
            "timezone_offset": 0,
            "screen_width": 1920,
            "screen_height": 1080,
            "avail_width": 1920, # Extra field
            "avail_height": 1080, # Extra field
            "window_width": 1920, # Extra field
            "window_height": 1080, # Extra field
            "color_depth": 24,
            "pixel_ratio": 2,
            "hardware_concurrency": 8, # Number
            "device_memory": 8, # Number
            "touch_support": False,
            "max_touch_points": 0,
            "is_webdriver": False,
            "has_chrome": True, # Extra field
            "has_plugins": False, # Extra field
            "webgl_vendor": "Google Inc. (Apple)",
            "webgl_renderer": "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
            "canvas_hash": "somehash",
            "audio_hash": "somehash",
            "fonts_detected": ["Arial", "Times New Roman"],
            "mouse_movements": 0,
            "scroll_events": 0,
            "time_on_page": 150
        }
    }
    
    # Mock redis for campaign lookup to determine final destination
    # smart_redirector._get_final_destination calls redis_cache.get(f"campaign:{campaign_id}")
    with patch("core.redirect.smart_redirector.redis_cache.get") as mock_get_campaign:
        mock_get_campaign.return_value = {"type": "template"}
        
        # We also need to mock session_manager if verify_fingerprint uses it?
        # verify_fingerprint calls smart_redirector.verify_fingerprint
        # smart_redirector calls fp_validator.validate
        # Then _get_final_destination
        
        resp = client.post("/v5/verify_fingerprint", json=payload)
        
        assert resp.status_code == 200
        data = resp.json()
        assert "redirect_to" in data
        assert "/v5/phish/test-campaign/login" in data["redirect_to"]
