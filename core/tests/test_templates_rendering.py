import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure the core module is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.social.templates import MicrosoftLoginTemplate, GoogleLoginTemplate

class TestTemplateRendering:
    def setup_method(self):
        # We don't need manager for this test, we test templates directly
        pass

    def test_microsoft_template_rendering(self):
        """Test if the Microsoft template is loaded and variables are substituted."""
        template = MicrosoftLoginTemplate()
        context = {"target_email": "victim@example.com"}
        
        # Ensure the template file exists (it should, as we modified it)
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "templates", "high_fidelity", "microsoft.html"
        )
        assert os.path.exists(template_path), "Microsoft template file not found!"

        # Render the template
        content = template.render(context)
        
        # Check for variable substitution
        assert "victim@example.com" in content
        assert 'value="victim@example.com"' in content
        assert '<span id="user-email-display">victim@example.com</span>' in content
        assert "Log in" in content  # Check for the updated text we added

    def test_google_template_rendering(self):
        """Test if the Google template is loaded and variables are substituted."""
        template = GoogleLoginTemplate()
        context = {"target_email": "target@gmail.com"}
        
        # Ensure the template file exists
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "templates", "high_fidelity", "google.html"
        )
        assert os.path.exists(template_path), "Google template file not found!"

        # Render the template
        content = template.render(context)
        
        # Check for variable substitution
        assert "target@gmail.com" in content
        assert 'value="target@gmail.com"' in content
        assert '<span id="user-email-display">target@gmail.com</span>' in content
        assert "Log in" in content 

if __name__ == "__main__":
    pytest.main([__file__])
