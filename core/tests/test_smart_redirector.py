import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from core.redirect.smart_redirector import SmartRedirector

@pytest.fixture
def mock_session_manager():
    sm = MagicMock()
    sm.create_session.return_value = "test_session_id"
    return sm

@pytest.fixture
def mock_antibot():
    ab = AsyncMock()
    ab.check_request.return_value = {"blocked": False, "reason": "Clean"}
    return ab

@pytest.mark.asyncio
async def test_process_request_injects_js(mock_session_manager, mock_antibot):
    redirector = SmartRedirector(use_antibot=True)
    redirector.session_manager = mock_session_manager
    redirector.antibot = mock_antibot
    
    # Mock file reading
    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.read.side_effect = [
            "<html>{{ campaign_id }} {{ session_id }} /* {{ fingerprint_js }} */</html>", # redirect.html
            "console.log('fingerprint');" # fingerprint_collector.js
        ]
        mock_open.return_value.__enter__.return_value = mock_file
        
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = "Mozilla/5.0"
        
        response = await redirector.process_request(request, "camp123")
        
        assert response.status_code == 200
        content = response.body.decode()
        assert "camp123" in content
        assert "test_session_id" in content
        assert "console.log('fingerprint');" in content
