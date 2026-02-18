import os
from core.edge.phishlets import PhishletLoader

def test_legacy_phishlet_conversion():
    loader = PhishletLoader()
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "phishlets", "example.yaml"))
    with open(path, "r") as f:
        y = f.read()
    cfg = loader.load_from_yaml(y)
    assert cfg.name in ("Legacy-Imported", cfg.name)
    assert len(cfg.proxy_hosts) >= 1
    # First target should look like "<sub>.<domain>"
    t0 = cfg.proxy_hosts[0].target
    assert "." in t0
    # Credentials mapped
    names = [c.name for c in cfg.credentials]
    assert "email" in names
    assert "password" in names
    # Landing path fallback present
    assert len(cfg.landing_path) >= 1
