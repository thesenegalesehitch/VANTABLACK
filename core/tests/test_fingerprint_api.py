
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from core.api.routes import router
from unittest.mock import AsyncMock, patch

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_smart_redirector():
    with patch("core.api.routes.smart_redirector") as mock:
        yield mock

def test_verify_fingerprint_success(client, mock_smart_redirector):
    # Mock verify_fingerprint return value
    mock_smart_redirector.verify_fingerprint = AsyncMock(return_value={"redirect_to": "/v5/phish/abc/login?sid=xyz"})
    
    payload = {
        "campaign_id": "test_cid",
        "session_id": "test_sid",
        "fingerprint": {
            "user_agent": "Mozilla/5.0",
            "canvas_hash": 12345
        }
    }
    
    response = client.post("/v5/verify_fingerprint", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["redirect_to"] == "/v5/phish/abc/login?sid=xyz"
    
    # Verify mock called with correct args
    mock_smart_redirector.verify_fingerprint.assert_called_once()
    call_args = mock_smart_redirector.verify_fingerprint.call_args
    assert call_args[0][0] == "test_sid" # sid
    assert call_args[0][1] == payload["fingerprint"] # fp_data
    assert call_args[0][2] == "test_cid" # cid

def test_verify_fingerprint_missing_fields(client, mock_smart_redirector):
    payload = {
        "campaign_id": "test_cid"
        # Missing session_id and fingerprint
    }
    
    response = client.post("/v5/verify_fingerprint", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["redirect_to"] == "https://google.com"
