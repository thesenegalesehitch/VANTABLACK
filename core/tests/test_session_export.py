
import pytest
from unittest.mock import MagicMock, patch
from core.session.session_manager import SessionManager
from core.api.routes import router
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

class TestSessionExport:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_session_manager(self):
        with patch("core.api.routes.session_manager") as mock:
            yield mock

    def test_export_json(self, client, mock_session_manager):
        session_id = "test-session-123"
        mock_data = {
            "session_id": session_id,
            "campaign_id": "camp-1",
            "captured_data": {"username": "admin", "password": "password123"},
            "cookies": [
                {"name": "session_token", "value": "abc123xyz", "domain": ".example.com", "path": "/", "secure": True, "expires": 1700000000}
            ]
        }
        
        mock_session_manager.get_session.return_value = mock_data
        mock_session_manager.export_session.return_value = mock_data["cookies"]

        response = client.get(f"/v5/sessions/{session_id}/export?format=json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["cookies"][0]["name"] == "session_token"
        assert data["captured_credentials"]["username"] == "admin"

    def test_export_netscape(self, client, mock_session_manager):
        session_id = "test-session-456"
        mock_data = {
            "session_id": session_id,
            "campaign_id": "camp-2",
            "cookies": [
                {"name": "auth", "value": "secret", "domain": ".secure.com", "path": "/", "secure": True, "expires": 1800000000}
            ]
        }
        
        # Expected Netscape content
        netscape_content = "# Netscape HTTP Cookie File\n.secure.com\tTRUE\t/\tTRUE\t1800000000\tauth\tsecret"
        
        mock_session_manager.get_session.return_value = mock_data
        mock_session_manager.export_session.return_value = netscape_content

        response = client.get(f"/v5/sessions/{session_id}/export?format=netscape")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "# Netscape HTTP Cookie File" in response.text
        assert ".secure.com" in response.text
        assert "secret" in response.text

    def test_session_not_found(self, client, mock_session_manager):
        mock_session_manager.get_session.return_value = None
        
        response = client.get("/v5/sessions/nonexistent/export")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
