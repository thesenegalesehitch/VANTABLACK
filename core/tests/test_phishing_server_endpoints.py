from fastapi.testclient import TestClient
import importlib

ps = importlib.import_module("phishing_server")
client = TestClient(ps.app)

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_status_ok():
    r = client.get("/status")
    assert r.status_code == 200
    assert "target" in r.json()
