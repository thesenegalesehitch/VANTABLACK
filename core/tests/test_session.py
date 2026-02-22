import pytest
from unittest.mock import MagicMock, patch
from core.session.session_manager import SessionManager

# Mock data storage
mock_storage = {}

def mock_set(key, value, expire=None):
    mock_storage[key] = value
    return True

def mock_get(key):
    return mock_storage.get(key)

@pytest.fixture
def mock_redis():
    mock_storage.clear()
    with patch('core.session.session_manager.redis_cache') as mock:
        mock.set.side_effect = mock_set
        mock.get.side_effect = mock_get
        yield mock

def test_create_session(mock_redis):
    manager = SessionManager()
    session_id = manager.create_session("campaign_123", "127.0.0.1", "Mozilla/5.0")
    
    assert session_id is not None
    
    # Vérifier les données stockées
    key = f"session:{session_id}"
    assert key in mock_storage
    stored_data = mock_storage[key]
    
    assert stored_data["campaign_id"] == "campaign_123"
    assert stored_data["client_ip"] == "127.0.0.1"
    assert stored_data["status"] == "active"

def test_capture_credential(mock_redis):
    manager = SessionManager()
    session_id = "test-session-id"
    initial_data = {
        "session_id": session_id,
        "captured_data": {},
        "cookies": {}
    }
    mock_storage[f"session:{session_id}"] = initial_data
    
    # Capturer un mot de passe
    manager.capture_credential(session_id, "password", "SuperSecret123!")
    
    # Vérifier
    updated_data = mock_storage[f"session:{session_id}"]
    assert updated_data["captured_data"]["password"] == "SuperSecret123!"

def test_capture_cookies(mock_redis):
    manager = SessionManager()
    session_id = "test-session-id"
    initial_data = {
        "session_id": session_id,
        "captured_data": {},
        "cookies": {}
    }
    mock_storage[f"session:{session_id}"] = initial_data
    
    cookies = {"session_token": "abc-123", "auth": "xyz-789"}
    manager.capture_cookies(session_id, cookies)
    
    updated_data = mock_storage[f"session:{session_id}"]
    assert updated_data["cookies"]["session_token"] == "abc-123"
