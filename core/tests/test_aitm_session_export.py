import pytest
from core.session.session_manager import SessionManager
from core.cache.redis_manager import redis_cache

# Mock Redis to avoid needing a real Redis server for unit tests
class MockRedis:
    def __init__(self):
        self.store = {}
    
    def set(self, key, value, expire=None):
        self.store[key] = value
        
    def get(self, key):
        return self.store.get(key)

@pytest.fixture
def session_manager():
    # Patch redis_cache with our mock
    original_set = redis_cache.set
    original_get = redis_cache.get
    
    mock_redis = MockRedis()
    redis_cache.set = mock_redis.set
    redis_cache.get = mock_redis.get
    
    manager = SessionManager()
    
    yield manager
    
    # Restore
    redis_cache.set = original_set
    redis_cache.get = original_get

def test_session_export_json(session_manager):
    # 1. Create session
    sid = session_manager.create_session("camp1", "127.0.0.1", "Mozilla/5.0")
    
    # 2. Add cookies
    cookies = [
        {"name": "session_token", "value": "abc12345", "domain": "example.com", "path": "/", "secure": True, "httpOnly": True},
        {"name": "user_pref", "value": "dark_mode", "domain": "example.com", "path": "/", "secure": False}
    ]
    session_manager.capture_cookies(sid, cookies)
    
    # 3. Export JSON
    exported = session_manager.export_session(sid, format="json")
    assert isinstance(exported, list)
    assert len(exported) == 2
    assert exported[0]["value"] == "abc12345"

def test_session_export_netscape(session_manager):
    # 1. Create session
    sid = session_manager.create_session("camp1", "127.0.0.1", "Mozilla/5.0")
    
    # 2. Add cookies
    cookies = [
        {"name": "session_token", "value": "abc12345", "domain": ".example.com", "path": "/", "secure": True, "expires": 1700000000}
    ]
    session_manager.capture_cookies(sid, cookies)
    
    # 3. Export Netscape
    exported = session_manager.export_session(sid, format="netscape")
    assert isinstance(exported, str)
    assert "# Netscape HTTP Cookie File" in exported
    assert ".example.com" in exported
    assert "abc12345" in exported
    
    # Check format: domain flag path secure expiration name value
    # .example.com TRUE / TRUE 1700000000 session_token abc12345
    parts = exported.split("\n")
    cookie_line = parts[1]
    columns = cookie_line.split("\t")
    assert columns[0] == ".example.com"
    assert columns[5] == "session_token"
    assert columns[6] == "abc12345"
