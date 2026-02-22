import pytest
from core.redirect.antibot import AntiBotSystem
from core.redirect.fingerprint import BrowserFingerprint, FingerprintValidator

class MockRequest:
    def __init__(self, ip="127.0.0.1", ua="Mozilla/5.0"):
        self.client = type("Client", (), {"host": ip})()
        self.headers = {"user-agent": ua, "accept-language": "en-US"}

@pytest.mark.asyncio
async def test_antibot_detection():
    system = AntiBotSystem()
    
    # Test Clean Request
    req = MockRequest(ua="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
    result = await system.check_request(req)
    assert result["blocked"] is False
    
    # Test Bot User-Agent
    req_bot = MockRequest(ua="Googlebot/2.1 (+http://www.google.com/bot.html)")
    result = await system.check_request(req_bot)
    assert result["blocked"] is True
    assert result["type"] == "bot_ua"

    # Test Suspicious Headers (Missing Accept-Language)
    req_suspicious = MockRequest(ua="HeadlessChrome")
    req_suspicious.headers = {"user-agent": "HeadlessChrome"} # No accept-language
    result = await system.check_request(req_suspicious)
    assert result["blocked"] is True

def test_fingerprint_validator():
    validator = FingerprintValidator()
    
    # Valid Human Fingerprint
    fp_human = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="MacIntel",
        language="en-US",
        timezone_offset=-120,
        webgl_renderer="Intel Iris Plus Graphics 640",
        mouse_movements=100,
        scroll_events=50,
        time_on_page=5000
    )
    assert validator.validate(fp_human) is True
    
    # Invalid Bot Fingerprint (Headless)
    fp_bot = BrowserFingerprint(
        user_agent="Mozilla/5.0 (HeadlessChrome)",
        screen_width=800,
        screen_height=600,
        color_depth=24,
        platform="Linux x86_64",
        language="en-US",
        timezone_offset=0,
        webgl_renderer="SwiftShader", # Software renderer
        mouse_movements=0,
        scroll_events=0,
        time_on_page=100
    )
    assert validator.validate(fp_bot) is False
