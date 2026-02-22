
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, WebSocket
from core.api.routes import router

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_session_manager():
    with patch("core.api.routes.session_manager") as mock:
        yield mock

@pytest.fixture
def mock_aitm_proxy():
    with patch("core.api.routes.aitm_proxy") as mock:
        mock.proxy_websocket = AsyncMock()
        yield mock

def test_websocket_proxy_success(client, mock_session_manager, mock_aitm_proxy):
    session_id = "test-session-ws"
    mock_session_manager.get_session.return_value = {"session_id": session_id}
    
    url = "wss://example.com/chat"
    
    # TestClient.websocket_connect is available
    with client.websocket_connect(f"/v5/p/{session_id}/ws?url={url}") as websocket:
        # Connection should be accepted
        pass
        
    # Verify aitm_proxy.proxy_websocket was called
    assert mock_aitm_proxy.proxy_websocket.called
    args = mock_aitm_proxy.proxy_websocket.call_args
    assert args[0][0] == url
    assert args[0][2] == session_id

def test_websocket_proxy_invalid_session(client, mock_session_manager, mock_aitm_proxy):
    session_id = "invalid-session"
    mock_session_manager.get_session.return_value = None
    
    try:
        with client.websocket_connect(f"/v5/p/{session_id}/ws?url=wss://example.com") as websocket:
            pass
    except Exception:
        # WebSocketDisconnect is expected usually, or just closed
        pass
    
    # Should not call proxy
    assert not mock_aitm_proxy.proxy_websocket.called

def test_websocket_proxy_missing_url(client, mock_session_manager, mock_aitm_proxy):
    session_id = "test-session-ws"
    mock_session_manager.get_session.return_value = {"session_id": session_id}
    
    try:
        with client.websocket_connect(f"/v5/p/{session_id}/ws") as websocket:
            pass
    except Exception:
        pass
        
    # Should not call proxy
    assert not mock_aitm_proxy.proxy_websocket.called
