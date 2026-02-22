import pytest
import ipaddress
from core.redirect.antibot import AntiBotSystem
from fastapi import Request
from unittest.mock import MagicMock, patch

def test_antibot_user_agent():
    antibot = AntiBotSystem()
    assert antibot.is_bot_user_agent("Googlebot/2.1 (+http://www.google.com/bot.html)") is True
    assert antibot.is_bot_user_agent("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)") is True
    assert antibot.is_bot_user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36") is False
    assert antibot.is_bot_user_agent("") is True # Empty UA is suspicious

def test_antibot_datacenter_ip():
    antibot = AntiBotSystem()
    # AWS range (3.0.0.0/9)
    assert antibot.is_datacenter_ip("3.5.0.1") is True
    # Local IP
    assert antibot.is_datacenter_ip("127.0.0.1") is False
    # Random residential IP (hopefully not in the small list)
    assert antibot.is_datacenter_ip("8.8.8.8") is False 

def test_antibot_suspicious_headers():
    antibot = AntiBotSystem()
    request = MagicMock(spec=Request)
    request.headers = {"user-agent": "Mozilla/5.0", "webdriver": "true"}
    assert antibot._has_suspicious_headers(request) is True
    
    request.headers = {"user-agent": "HeadlessChrome"}
    assert antibot._has_suspicious_headers(request) is True

    # Missing standard headers
    request.headers = {"user-agent": "Mozilla/5.0"}
    assert antibot._has_suspicious_headers(request) is True

    # Valid headers
    request.headers = {
        "user-agent": "Mozilla/5.0",
        "accept-language": "en-US",
        "accept-encoding": "gzip"
    }
    assert antibot._has_suspicious_headers(request) is False

@pytest.mark.asyncio
async def test_check_request_caching():
    with patch("core.redirect.antibot.redis_cache") as mock_redis:
        mock_redis.get.return_value = None # Cache miss
        
        antibot = AntiBotSystem()
        request = MagicMock(spec=Request)
        request.client.host = "1.2.3.4"
        request.headers = {"user-agent": "Googlebot"}
        
        # First call (Miss)
        result = await antibot.check_request(request)
        assert result["blocked"] is True
        assert mock_redis.set.called
        
        # Second call (Hit)
        mock_redis.get.return_value = {"blocked": True, "reason": "Cached"}
        result_cached = await antibot.check_request(request)
        assert result_cached["reason"] == "Cached"
