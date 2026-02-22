import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket
from core.proxy.aitm import AiTMProxy
import aiohttp
from starlette.websockets import WebSocketDisconnect

@pytest.fixture
def mock_aiohttp_session():
    session = MagicMock()
    session.closed = False
    return session

@pytest.mark.asyncio
async def test_proxy_websocket_success(mock_aiohttp_session):
    proxy = AiTMProxy()
    proxy.session = mock_aiohttp_session
    
    # Mock WebSocket client (FastAPI side)
    client_ws = AsyncMock(spec=WebSocket)
    client_ws.receive.side_effect = [
        {"text": "hello from client"},
        {"bytes": b"binary data"},
        WebSocketDisconnect() # End of stream
    ]
    
    # Mock Upstream WebSocket (aiohttp side)
    upstream_ws = AsyncMock()
    # Mock iteration for async for
    upstream_msg_text = MagicMock()
    upstream_msg_text.type = aiohttp.WSMsgType.TEXT
    upstream_msg_text.data = "hello from server"
    
    upstream_msg_bin = MagicMock()
    upstream_msg_bin.type = aiohttp.WSMsgType.BINARY
    upstream_msg_bin.data = b"server binary"

    upstream_ws.__aiter__.return_value = [upstream_msg_text, upstream_msg_bin]
    
    # Context manager for ws_connect
    mock_aiohttp_session.ws_connect.return_value.__aenter__.return_value = upstream_ws
    
    await proxy.proxy_websocket(
        target_url="wss://example.com/socket",
        client_ws=client_ws,
        headers={"User-Agent": "Test"},
        cookies={}
    )
    
    # Verify Client -> Upstream
    upstream_ws.send_str.assert_called_with("hello from client")
    upstream_ws.send_bytes.assert_called_with(b"binary data")
    upstream_ws.close.assert_called() # Called when client disconnects
    
    # Verify Upstream -> Client
    client_ws.send_text.assert_called_with("hello from server")
    client_ws.send_bytes.assert_called_with(b"server binary")

@pytest.mark.asyncio
async def test_proxy_websocket_rewrite(mock_aiohttp_session):
    proxy = AiTMProxy()
    proxy.session = mock_aiohttp_session
    
    # Mock Client
    client_ws = AsyncMock(spec=WebSocket)
    client_ws.receive.side_effect = [WebSocketDisconnect()] # Just close immediately from client side
    
    # Mock Upstream
    upstream_ws = AsyncMock()
    
    # Message 1: JSON with URL
    msg1 = MagicMock()
    msg1.type = aiohttp.WSMsgType.TEXT
    msg1.data = '{"redirect": "https://login.microsoftonline.com/common/oauth2"}'
    
    # Message 2: Plain text with URL
    msg2 = MagicMock()
    msg2.type = aiohttp.WSMsgType.TEXT
    msg2.data = 'Please go to https://mysignins.microsoft.com/'
    
    upstream_ws.__aiter__.return_value = [msg1, msg2]
    mock_aiohttp_session.ws_connect.return_value.__aenter__.return_value = upstream_ws
    
    await proxy.proxy_websocket(
        target_url="wss://example.com/socket",
        client_ws=client_ws,
        headers={},
        cookies={}
    )
    
    # Verify rewrites
    # Expected: JSON rewrite
    # https://login.microsoftonline.com/common/oauth2 -> /v5/proxy?url=...
    call_args_list = client_ws.send_text.call_args_list
    assert len(call_args_list) == 2
    
    json_msg = call_args_list[0][0][0]
    assert "/v5/proxy?url=" in json_msg
    assert "login.microsoftonline.com" in json_msg # Encoded or part of param
    
    text_msg = call_args_list[1][0][0]
    assert "Please go to /v5/proxy?url=" in text_msg
