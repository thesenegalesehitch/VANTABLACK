
import pytest
from fastapi.testclient import TestClient
from core.web.server import create_app
from core.session.session_manager import session_manager
from core.cache.redis_manager import redis_cache
import time

# Mock Redis for testing to avoid needing a real Redis server running
# However, since we are using a real Redis client in the code, we might need to mock the methods.
# For this integration test, let's assume the environment might have Redis or we mock the cache manager.

class MockRedis:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value, expire=None):
        self.data[key] = value
        return True
        
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return True
        return False
        
    def scan_keys(self, pattern):
        # Simple pattern matching for "session:*"
        if pattern == "session:*":
            return [k for k in self.data.keys() if k.startswith("session:")]
        return []

# Monkey patch for the test
original_redis = redis_cache
mock_redis = MockRedis()

@pytest.fixture
def client():
    # Patch redis
    redis_cache.get = mock_redis.get
    redis_cache.set = mock_redis.set
    redis_cache.delete = mock_redis.delete
    redis_cache.scan_keys = mock_redis.scan_keys
    
    app = create_app()
    return TestClient(app)

def test_dashboard_stats(client):
    # 1. Create a dummy session
    session_id = session_manager.create_session("camp-test", "1.2.3.4", "Mozilla/Test")
    
    # 2. Call stats endpoint
    response = client.get("/v5/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert "active_sessions" in data
    assert data["active_sessions"] >= 1
    assert "captured_creds" in data

def test_dashboard_sessions_list(client):
    # 1. Create a dummy session
    session_id = session_manager.create_session("camp-list", "5.6.7.8", "Chrome/Test")
    
    # 2. Call sessions endpoint
    response = client.get("/v5/dashboard/sessions")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    found = False
    for s in data:
        if s["ip"] == "5.6.7.8":
            found = True
            break
    assert found

def test_dashboard_html(client):
    response = client.get("/v5/dashboard/")
    assert response.status_code == 200
    assert "VANTABLACK" in response.text
    assert "Active Sessions" in response.text
