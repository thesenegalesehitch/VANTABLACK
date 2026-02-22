
import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from core.social.manager import SocialEngineeringManager
from core.qr_link_system import QRConfig

# Mock Redis
class MockRedis:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value, expire=None):
        self.data[key] = value
        return True

@pytest.fixture
def mock_redis():
    with patch("core.social.manager.redis_cache") as mock:
        mock_instance = MockRedis()
        mock.get.side_effect = mock_instance.get
        mock.set.side_effect = mock_instance.set
        yield mock_instance

@pytest.fixture
def social_manager(mock_redis):
    # Ensure assets directory exists for QR codes
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qr_dir = os.path.join(base_dir, "assets", "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)
    
    manager = SocialEngineeringManager()
    return manager

def test_create_campaign_with_qr(social_manager):
    """Test creating a campaign and generating a QR code."""
    campaign_name = "Test Campaign"
    template_id = "microsoft"  # Assuming 'microsoft' template exists
    target_email = "victim@example.com"
    
    # Mock templates if necessary, but we can rely on TemplateLoader if templates exist
    # If templates don't exist in test env, we might need to mock TemplateLoader
    
    campaign = social_manager.create_campaign(
        name=campaign_name,
        template_id=template_id,
        target_email=target_email
    )
    
    assert campaign is not None
    assert campaign["name"] == campaign_name
    assert campaign["target_email"] == target_email
    assert "qr_code_path" in campaign
    assert "qr_code_url" in campaign
    assert os.path.exists(campaign["qr_code_path"])
    
    # Clean up QR code
    if os.path.exists(campaign["qr_code_path"]):
        os.remove(campaign["qr_code_path"])

def test_get_campaign(social_manager):
    """Test retrieving a campaign."""
    campaign_name = "Test Campaign 2"
    template_id = "google"
    target_email = "target@gmail.com"
    
    created_campaign = social_manager.create_campaign(
        name=campaign_name,
        template_id=template_id,
        target_email=target_email
    )
    
    fetched_campaign = social_manager.get_campaign(created_campaign["id"])
    assert fetched_campaign is not None
    assert fetched_campaign["id"] == created_campaign["id"]
    assert fetched_campaign["name"] == campaign_name

def test_get_template_content(social_manager):
    """Test rendering template content for a campaign."""
    campaign_name = "Test Campaign 3"
    template_id = "microsoft"
    target_email = "ceo@example.com"
    
    campaign = social_manager.create_campaign(
        name=campaign_name,
        template_id=template_id,
        target_email=target_email
    )
    
    content = social_manager.get_template_content(campaign["id"])
    assert content is not None
    assert "ceo@example.com" in content
    assert "Log in" in content or "Sign in" in content
