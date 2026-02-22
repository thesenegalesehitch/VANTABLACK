
import pytest
from unittest.mock import MagicMock, patch
from core.session.session_manager import SessionManager

@pytest.fixture
def mock_redis():
    with patch("core.session.session_manager.redis_cache") as mock:
        storage = {}
        
        def set_impl(key, value, expire=None):
            storage[key] = value
            return True
            
        def get_impl(key):
            return storage.get(key)
            
        mock.set.side_effect = set_impl
        mock.get.side_effect = get_impl
        yield mock

@pytest.fixture
def session_manager(mock_redis):
    return SessionManager()

def test_export_session_json(session_manager):
    session_id = "test-session-export"
    cookies = [
        {"name": "session_token", "value": "abc123xyz", "domain": ".example.com", "path": "/", "secure": True, "expires": 1735689600}
    ]
    
    # Create session and add cookies
    session_manager.create_session("campaign-1", "127.0.0.1", "Mozilla/5.0")
    # Manually inject for test since create generates random ID
    session_data = {
        "session_id": session_id,
        "campaign_id": "campaign-1",
        "cookies": cookies
    }
    session_manager._save_session(session_id, session_data)
    
    exported = session_manager.export_session(session_id, format="json")
    assert exported == cookies
    assert exported[0]["value"] == "abc123xyz"

def test_export_session_netscape(session_manager):
    session_id = "test-session-netscape"
    cookies = [
        {"name": "auth", "value": "secret_token", "domain": ".google.com", "path": "/", "secure": True, "expires": 1700000000},
        {"name": "pref", "value": "dark_mode", "domain": "google.com", "path": "/settings", "secure": False, "expires": 0}
    ]
    
    session_data = {
        "session_id": session_id,
        "campaign_id": "campaign-1",
        "cookies": cookies
    }
    session_manager._save_session(session_id, session_data)
    
    exported = session_manager.export_session(session_id, format="netscape")
    
    lines = exported.split("\n")
    assert lines[0] == "# Netscape HTTP Cookie File"
    
    # Check first cookie
    # .google.com	TRUE	/	TRUE	1700000000	auth	secret_token
    parts1 = lines[1].split("\t")
    assert parts1[0] == ".google.com"
    assert parts1[1] == "TRUE"
    assert parts1[2] == "/"
    assert parts1[3] == "TRUE"
    assert parts1[5] == "auth"
    assert parts1[6] == "secret_token"
    
    # Check second cookie
    # google.com	FALSE	/settings	FALSE	0	pref	dark_mode
    parts2 = lines[2].split("\t")
    assert parts2[0] == "google.com"
    assert parts2[1] == "FALSE"
    assert parts2[3] == "FALSE"
    assert parts2[5] == "pref"
    assert parts2[6] == "dark_mode"

def test_export_session_not_found(session_manager):
    exported = session_manager.export_session("non-existent", format="json")
    assert exported == []
