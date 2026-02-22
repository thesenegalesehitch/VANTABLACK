
import pytest
import time
from core.proxy.aitm import AiTMProxy
from core.session.session_manager import SessionManager

@pytest.fixture
def aitm():
    return AiTMProxy()

@pytest.fixture
def session_manager():
    return SessionManager()

def test_rewrite_url_http(aitm):
    base_url = "https://example.com/page"
    url = "https://example.com/image.png"
    rewritten = aitm._rewrite_url(url, base_url, "/v5/proxy")
    assert "/v5/proxy?url=https%3A//example.com/image.png" in rewritten

def test_rewrite_url_ws(aitm):
    base_url = "https://example.com/page"
    url = "wss://example.com/socket"
    rewritten = aitm._rewrite_url(url, base_url, "/v5/proxy")
    # Should use /v5/proxy/ws
    assert "/v5/proxy/ws?url=wss%3A//example.com/socket" in rewritten

def test_rewrite_url_relative(aitm):
    base_url = "https://example.com/page/"
    url = "socket" # Relative URL, could be WS if context implies
    # The _rewrite_url method doesn't know context, so it treats as HTTP unless scheme is WS
    rewritten = aitm._rewrite_url(url, base_url, "/v5/proxy")
    assert "/v5/proxy?url=https%3A//example.com/page/socket" in rewritten

def test_rewrite_js_ws(aitm):
    js_content = b'var ws = new WebSocket("wss://api.example.com/chat");'
    rewritten = aitm.rewrite_js(js_content, "https://example.com", "/v5/proxy")
    # Verify the URL inside the JS is rewritten to the WS proxy endpoint
    assert b'/v5/proxy/ws?url=wss%3A//api.example.com/chat' in rewritten

def test_cookie_capture_expiration(aitm, session_manager):
    # Mocking cookie object from aiohttp/http.cookies is complex, 
    # so we test the logic if we were to extract it.
    # But since _capture_response_cookies takes headers, let's mock headers.
    
    from unittest.mock import MagicMock
    
    headers = MagicMock()
    # SimpleCookie format
    headers.getall.return_value = [
        "session=123; Domain=example.com; Path=/; Max-Age=3600",
        "user=alice; Domain=example.com; Path=/; Expires=Wed, 21 Oct 2025 07:28:00 GMT" # Expires ignored for now in our simple logic
    ]
    
    # We need to mock session_manager.capture_cookies to verify what it receives
    session_manager.capture_cookies = MagicMock()
    aitm.session_manager = session_manager
    
    aitm._capture_response_cookies("test_session", headers, "https://example.com")
    
    assert session_manager.capture_cookies.called
    args = session_manager.capture_cookies.call_args[0]
    session_id, cookies = args
    
    assert session_id == "test_session"
    assert len(cookies) == 2
    
    # Check Max-Age parsing
    c1 = next(c for c in cookies if c["name"] == "session")
    assert "expires" in c1
    # Check that expires is roughly now + 3600
    assert c1["expires"] > time.time() + 3500
    assert c1["expires"] < time.time() + 3700

