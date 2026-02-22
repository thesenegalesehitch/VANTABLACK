import pytest
from unittest.mock import MagicMock, patch
from core.social.manager import SocialEngineeringManager
from core.social.templates import PhishingTemplate

# Mocking external dependencies
@pytest.fixture
def mock_qr_system():
    with patch('core.social.manager.QRLinkSystem') as mock:
        instance = mock.return_value
        instance.generate_qr.return_value = (True, "QR Generated")
        yield instance

@pytest.fixture
def mock_redis():
    with patch('core.social.manager.redis_cache') as mock:
        # Simulate simple storage
        storage = {}
        def set_side_effect(key, value, expire=None):
            storage[key] = value
        def get_side_effect(key):
            return storage.get(key)
            
        mock.set.side_effect = set_side_effect
        mock.get.side_effect = get_side_effect
        yield mock

@pytest.fixture
def manager(mock_qr_system, mock_redis):
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
    assert "qr_code_path" in campaign
    assert "qr_code_url" in campaign
    assert campaign["qr_code_url"].startswith("/assets/qr_codes/")
    
    # Vérifier que la campagne est stockée
    assert manager.get_campaign(campaign["id"]) == campaign

def test_create_campaign_invalid_template(manager):
    with pytest.raises(ValueError):
        manager.create_campaign("Bad Campaign", "invalid_template_id")

def test_get_template_content(manager):
    campaign = manager.create_campaign("Test Content", "google")
    content = manager.get_template_content(campaign["id"])
    
    assert "Log in - Google Accounts" in content
    assert 'new Phantasm({' in content
    assert "sessionId: '{{ session_id }}'" in content

def test_template_rendering():
    from core.social.templates import GenericUpdateTemplate
    template = GenericUpdateTemplate()
    content = template.render({"company": "Acme Corp"})
    assert "Acme Corp Security Update" in content
