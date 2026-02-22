
import pytest
import json
from unittest.mock import MagicMock, patch
from core.session.session_manager import SessionManager
from core.cache.redis_manager import redis_cache

class MockRedis:
    def __init__(self):
        self.store = {}
    
    def set(self, key, value, expire=None):
        if isinstance(value, (dict, list)):
            self.store[key] = json.dumps(value)
        else:
            self.store[key] = value
        return True
        
    def get(self, key):
        val = self.store.get(key)
        if val and isinstance(val, str):
            try:
                return json.loads(val)
            except:
                return val
        return val

@pytest.fixture
def mock_redis():
    return MockRedis()

@pytest.fixture
def session_manager(mock_redis):
    # Patch global redis_cache object methods
    original_set = redis_cache.set
    original_get = redis_cache.get
    
    redis_cache.set = mock_redis.set
    redis_cache.get = mock_redis.get
    
    yield SessionManager()
    
    # Restore
    redis_cache.set = original_set
    redis_cache.get = original_get

def test_export_session_netscape(session_manager):
    # Create session
    session_id = session_manager.create_session("camp-1", "127.0.0.1", "Mozilla/5.0")
    
    # DEBUG
    print(f"Session created: {session_manager.get_session(session_id)}")

    # Add cookies
    cookies = [
        {"name": "session_id", "value": "xyz123", "domain": ".example.com", "path": "/", "secure": True, "expires": 1700000000},
        {"name": "user_pref", "value": "dark_mode", "domain": "example.com", "path": "/app", "secure": False, "expires": 0}
    ]
    session_manager.capture_cookies(session_id, cookies)
    
    # DEBUG
    print(f"Session after capture: {session_manager.get_session(session_id)}")
    
    # Export Netscape
    netscape = session_manager.export_session(session_id, format="netscape")
    
    lines = netscape.split("\n")
    assert lines[0] == "# Netscape HTTP Cookie File"
    
    # Check first cookie
    # domain flag path secure expiration name value
    # .example.com TRUE / TRUE 1700000000 session_id xyz123
    assert ".example.com\tTRUE\t/\tTRUE\t1700000000\tsession_id\txyz123" in netscape
    
    # Check second cookie
    # example.com FALSE /app FALSE 0 user_pref dark_mode
    assert "example.com\tFALSE\t/app\tFALSE\t0\tuser_pref\tdark_mode" in netscape

def test_export_session_json(session_manager):
    session_id = session_manager.create_session("camp-1", "127.0.0.1", "Mozilla/5.0")
    
    cookies = [
        {"name": "token", "value": "abc", "domain": "api.com"}
    ]
    session_manager.capture_cookies(session_id, cookies)
    
    json_export = session_manager.export_session(session_id, format="json")
    assert isinstance(json_export, list)
    assert len(json_export) == 1
    assert json_export[0]["name"] == "token"
    assert json_export[0]["value"] == "abc"
