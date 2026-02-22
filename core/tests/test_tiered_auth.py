import pytest
from fastapi.testclient import TestClient
from core.web.server import create_app
from core.common import config
import os

# Mock config
@pytest.fixture
def tiered_app(monkeypatch):
    monkeypatch.setenv("TIER2_ENABLED", "true")
    monkeypatch.setenv("TIER2_SECRET", "secret123")
    
    # We need to reload the app or re-create it to pick up the env var
    # create_app reads config which reads os.environ
    app = create_app()
    return app

def test_tiered_auth_success(tiered_app):
    client = TestClient(tiered_app)
    response = client.get("/ui", headers={"X-Vantablack-Auth": "secret123"})
    assert response.status_code == 200

def test_tiered_auth_failure_no_header(tiered_app):
    client = TestClient(tiered_app)
    response = client.get("/ui")
    assert response.status_code == 403
    assert response.json() == {"error": "Tier 2 Authentication Failed"}

def test_tiered_auth_failure_wrong_header(tiered_app):
    client = TestClient(tiered_app)
    response = client.get("/ui", headers={"X-Vantablack-Auth": "wrong"})
    assert response.status_code == 403

def test_tiered_auth_health_bypass(tiered_app):
    client = TestClient(tiered_app)
    # /health might not be defined in web/server.py directly (it's in api/routes.py),
    # but let's check if the middleware allows it to pass through.
    # If /health is not found, it should be 404, not 403.
    response = client.get("/health")
    assert response.status_code != 403
    
    response = client.get("/v5/health")
    assert response.status_code != 403
