import pytest
from unittest.mock import MagicMock, patch
from core.social.manager import SocialEngineeringManager
from core.social.templates import PhishingTemplate

# Mocking external dependencies
@pytest.fixture
def mock_qr_system():
    with patch('core.social.manager.QRLinkSystem') as mock:
        instance = mock.return_value
        instance.generate_qr.return_value = "/tmp/mock_qr.png"
        yield instance

@pytest.fixture
def manager(mock_qr_system):
    return SocialEngineeringManager()

def test_list_templates(manager):
    templates = manager.list_templates()
    assert len(templates) >= 3
    assert any(t["id"] == "microsoft" for t in templates)

def test_create_campaign(manager):
    campaign = manager.create_campaign("Test Campaign", "microsoft")
    
    assert campaign["id"] is not None
    assert campaign["name"] == "Test Campaign"
    assert campaign["template_id"] == "microsoft"
    assert campaign["status"] == "active"
    assert campaign["qr_code_path"] == "/tmp/mock_qr.png"
    
    # Vérifier que la campagne est stockée
    assert manager.get_campaign(campaign["id"]) == campaign

def test_create_campaign_invalid_template(manager):
    with pytest.raises(ValueError):
        manager.create_campaign("Bad Campaign", "invalid_template_id")

def test_get_template_content(manager):
    campaign = manager.create_campaign("Test Content", "google")
    content = manager.get_template_content(campaign["id"])
    
    assert "Sign in - Google Accounts" in content
    assert '<form action="/auth/login" method="POST">' in content

def test_template_rendering():
    from core.social.templates import GenericUpdateTemplate
    template = GenericUpdateTemplate()
    content = template.render({"company": "Acme Corp"})
    assert "Acme Corp Security Update" in content
