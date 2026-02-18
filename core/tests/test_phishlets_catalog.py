import glob
from core.edge.phishlets import PhishletLoader

def test_catalog_loads_all_yaml():
    loader = PhishletLoader()
    files = glob.glob("phishlets/*.yaml")
    assert files, "No phishlet files found"
    for p in files:
        with open(p, "r") as f:
            y = f.read()
        cfg = loader.load_from_yaml(y)
        assert cfg.name
        assert cfg.proxy_hosts
        assert isinstance(cfg.blocklist, list)
        assert isinstance(cfg.form_actions, list)
