import pytest
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
from fastapi.responses import HTMLResponse
from core.redirect.smart_redirector import SmartRedirector

class TestSmartRedirectionIntegration:
    
    @pytest.fixture
    def redirector(self):
        # We need to patch the objects where they are used (imported)
        with patch("core.redirect.smart_redirector.session_manager") as mock_sm, \
             patch("core.redirect.smart_redirector.antibot") as mock_antibot:
            
            # Setup default behaviors
            mock_sm.create_session.return_value = "sess_123"
            mock_antibot.check_request = AsyncMock(return_value={"blocked": False})
            
            # Instantiate
            redirector = SmartRedirector()
            # Ensure instance uses mocks
            redirector.session_manager = mock_sm
            redirector.antibot = mock_antibot
            
            yield redirector

    @pytest.mark.asyncio
    async def test_process_request_serves_html(self, redirector):
        request = MagicMock()
        request.client.host = "1.2.3.4"
        request.headers.get.return_value = "Mozilla/5.0"
        
        # Mock file reading
        mock_content = "<html>{{ campaign_id }} {{ session_id }}</html>"
        with patch("builtins.open", mock_open(read_data=mock_content)):
            response = await redirector.process_request(request, "camp_123")
            
            assert isinstance(response, HTMLResponse)
            body = response.body.decode()
            assert "camp_123" in body
            assert "sess_123" in body

    @pytest.mark.asyncio
    async def test_verify_fingerprint_valid(self, redirector):
        # Valid fingerprint data
        fp_data = {
            "user_agent": "Mozilla/5.0 MacIntel",
            "screen_width": 1920,
            "screen_height": 1080,
            "color_depth": 24,
            "platform": "MacIntel",
            "language": "en-US",
            "timezone_offset": -120,
            "mouse_movements": 50,
            "scroll_events": 10,
            "time_on_page": 2000,
            "webgl_renderer": "Intel Iris",
            "webgl_vendor": "Intel Inc.",
            "fonts_detected": ["Arial"],
            "canvas_hash": "hash123",
            "is_webdriver": False
        }
        
        # Patch redis in the module
        with patch("core.redirect.smart_redirector.redis_cache") as mock_redis:
            mock_redis.get.return_value = {"type": "template"}
            
            result = await redirector.verify_fingerprint("sess_123", fp_data, "camp_123")
            
            assert "redirect_to" in result
            assert "/v5/phish/camp_123/login" in result["redirect_to"]

    @pytest.mark.asyncio
    async def test_verify_fingerprint_bot(self, redirector):
        # Invalid bot fingerprint (Headless properties)
        fp_data = {
            "user_agent": "HeadlessChrome",
            "screen_width": 0,
            "screen_height": 0,
            "color_depth": 24,
            "platform": "Linux",
            "language": "en-US",
            "timezone_offset": 0,
            "mouse_movements": 0,
            "scroll_events": 0,
            "time_on_page": 0,
            "webgl_renderer": "SwiftShader",
            "webgl_vendor": "Google Inc.",
            "fonts_detected": [],
            "canvas_hash": "hash123",
            "is_webdriver": False
        }
        
        # Redis patch not strictly needed if it fails early, but good practice
        with patch("core.redirect.smart_redirector.redis_cache") as mock_redis:
            result = await redirector.verify_fingerprint("sess_123", fp_data, "camp_123")
        
        assert "redirect_to" in result
        assert result["redirect_to"] == SmartRedirector.DECOY_URL

    @pytest.mark.asyncio
    async def test_verify_fingerprint_webdriver(self, redirector):
        # Webdriver detected
        fp_data = {
            "user_agent": "Mozilla/5.0",
            "screen_width": 1920,
            "screen_height": 1080,
            "color_depth": 24,
            "platform": "MacIntel",
            "language": "en-US",
            "timezone_offset": 0,
            "mouse_movements": 10,
            "scroll_events": 5,
            "time_on_page": 2000,
            "webgl_renderer": "Intel Iris",
            "webgl_vendor": "Intel Inc.",
            "fonts_detected": ["Arial"],
            "canvas_hash": "hash123",
            "is_webdriver": True
        }
        
        result = await redirector.verify_fingerprint("sess_123", fp_data, "camp_123")
        assert result["redirect_to"] == SmartRedirector.DECOY_URL
