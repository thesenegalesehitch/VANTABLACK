import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from core.api.routes import router
from core.session.session_manager import session_manager
from fastapi import FastAPI

# Setup App for testing
app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_social_manager():
    with patch("core.api.routes.social_manager") as mock:
        # Load actual template content
        with open("core/assets/templates/high_fidelity/microsoft.html", "r") as f:
            content = f.read()
        mock.get_template_content.return_value = content
        yield mock

@pytest.fixture
def mock_session_manager():
    with patch("core.api.routes.session_manager") as mock:
        mock.get_session.return_value = {"session_id": "test_sid", "campaign_id": "test_cid", "cookies": []}
        yield mock

def test_template_variable_substitution(client, mock_social_manager, mock_session_manager):
    sid = "test_sid_123"
    cid = "test_cid_456"
    
    # Mock get_session to return valid session
    mock_session_manager.get_session.return_value = {"session_id": sid, "campaign_id": cid}
    
    response = client.get(f"/v5/phish/{cid}/login?sid={sid}")
    
    assert response.status_code == 200
    content = response.text
    
    # Check session_id substitution in Phantasm config
    expected_endpoint = f"apiEndpoint: '/v5/auth/login?sid={sid}'"
    assert expected_endpoint in content
    
    # Check that template placeholder is gone
    assert "{{ session_id }}" not in content

def test_session_export_json(client, mock_session_manager):
    sid = "test_sid_export"
    cookies = [
        {"name": "session", "value": "xyz", "domain": ".example.com", "path": "/", "secure": True, "httpOnly": True}
    ]
    
    mock_session_manager.get_session.return_value = {
        "session_id": sid, 
        "cookies": cookies, 
        "last_activity": 1234567890
    }
    mock_session_manager.export_session.return_value = cookies # Mocking the return of the manager method
    
    response = client.get(f"/v5/session/{sid}/export?format=json")
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == sid
    assert data["format"] == "json"
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "session"

def test_session_export_netscape(client, mock_session_manager):
    sid = "test_sid_export_ns"
    cookies = [
        {"name": "session", "value": "xyz", "domain": ".example.com", "path": "/", "secure": True, "httpOnly": True}
    ]
    
    # Mocking the manager behavior for netscape format
    netscape_content = "# Netscape HTTP Cookie File\n.example.com\tTRUE\t/\tTRUE\t0\tsession\txyz"
    mock_session_manager.get_session.return_value = {"session_id": sid, "cookies": cookies}
    mock_session_manager.export_session.return_value = netscape_content
    
    response = client.get(f"/v5/session/{sid}/export?format=netscape")
    
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "netscape"
    assert "# Netscape HTTP Cookie File" in data["data"]
    assert "session\txyz" in data["data"]
