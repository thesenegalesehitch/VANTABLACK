
import pytest
import json
from unittest.mock import MagicMock, patch
from core.proxy.aitm import AiTMProxy

class TestAiTMJsonRewrite:
    
    def setup_method(self):
        self.proxy = AiTMProxy()
        self.base_url = "https://example.com"
        self.proxy_base = "/proxy/"

    def test_rewrite_json_simple_url(self):
        """Test rewriting a simple URL in a JSON object."""
        original_json = {
            "redirect_url": "https://example.com/dashboard",
            "api_endpoint": "https://api.example.com/v1/data",
            "status": "ok"
        }
        json_content = json.dumps(original_json).encode('utf-8')
        
        # We need to implement rewrite_json method first, but let's assume we'll add it
        # For now, let's test if we can add this capability
        
        # Mock the rewrite_url method to simulate what we expect
        with patch.object(self.proxy, '_rewrite_url', side_effect=lambda url, base, proxy: f"/proxy/{url.replace('https://', '')}"):
            rewritten_content = self.proxy.rewrite_json(json_content, self.base_url, self.proxy_base)
            
            rewritten_json = json.loads(rewritten_content)
            assert rewritten_json["redirect_url"] == "/proxy/example.com/dashboard"
            assert rewritten_json["api_endpoint"] == "/proxy/api.example.com/v1/data"
            assert rewritten_json["status"] == "ok"

    def test_rewrite_json_nested(self):
        """Test rewriting URLs in nested JSON structures."""
        original_json = {
            "config": {
                "assets": [
                    "https://cdn.example.com/style.css",
                    "https://cdn.example.com/script.js"
                ],
                "login": {
                    "action": "https://auth.example.com/login"
                }
            }
        }
        json_content = json.dumps(original_json).encode('utf-8')
        
        with patch.object(self.proxy, '_rewrite_url', side_effect=lambda url, base, proxy: f"/proxy/{url.replace('https://', '')}"):
            rewritten_content = self.proxy.rewrite_json(json_content, self.base_url, self.proxy_base)
            
            rewritten_json = json.loads(rewritten_content)
            assert rewritten_json["config"]["assets"][0] == "/proxy/cdn.example.com/style.css"
            assert rewritten_json["config"]["login"]["action"] == "/proxy/auth.example.com/login"

    def test_rewrite_js_url(self):
        """Test rewriting a URL inside JavaScript content."""
        js_content = b"""
        const apiUrl = "https://api.example.com/v1/data";
        fetch("https://cdn.example.com/script.js");
        """
        
        # Mock rewrite_url
        with patch.object(self.proxy, '_rewrite_url', side_effect=lambda url, base, proxy: f"/proxy/{url.replace('https://', '')}"):
            rewritten_content = self.proxy.rewrite_js(js_content, self.base_url, self.proxy_base)
            
            rewritten_text = rewritten_content.decode('utf-8')
            assert '/proxy/api.example.com/v1/data' in rewritten_text
            assert '/proxy/cdn.example.com/script.js' in rewritten_text
            assert 'https://api.example.com' not in rewritten_text

    def test_rewrite_html_csp_removal(self):
        """Test removal of CSP meta tags."""
        html_content = b"""
        <html>
            <head>
                <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
                <meta http-equiv="refresh" content="0; url=https://example.com/login">
            </head>
            <body></body>
        </html>
        """
        
        with patch.object(self.proxy, '_rewrite_url', side_effect=lambda url, base, proxy: f"/proxy/{url.replace('https://', '')}"):
            rewritten_content = self.proxy.rewrite_html(html_content, self.base_url, self.proxy_base)
            
            rewritten_text = rewritten_content.decode('utf-8')
            assert 'Content-Security-Policy' not in rewritten_text
            assert 'default-src' not in rewritten_text
            assert '/proxy/example.com/login' in rewritten_text

if __name__ == "__main__":
    pytest.main([__file__])
