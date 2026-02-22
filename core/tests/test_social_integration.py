import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from core.social.manager import SocialEngineeringManager
from core.qr_link_system import QRConfig

@pytest.fixture
def mock_redis():
    with patch("core.social.manager.redis_cache") as mock:
        # Mock get/set methods
        mock.get.return_value = None
        mock.set.return_value = True
        yield mock

@pytest.fixture
def clean_qr_dir():
    # Setup: Ensure directory exists
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qr_dir = os.path.join(base_dir, "assets", "qr_codes")
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
        
    yield qr_dir
    
    # Teardown: Clean up generated files (optional, maybe keep for inspection if failed)
    # for f in os.listdir(qr_dir):
    #     if f.startswith("campaign_test_"):
    #         os.remove(os.path.join(qr_dir, f))

def test_campaign_qr_generation_integration(clean_qr_dir, mock_redis):
    """
    Integration test for SocialEngineeringManager + QRLinkSystem.
    Verifies that a campaign creation actually generates a QR code file on disk.
    """
    manager = SocialEngineeringManager()
    
    # Create a campaign
    # We use 'microsoft' template which should have a logo (microsoft.png or similar)
    campaign = manager.create_campaign(
        name="Integration Test Campaign",
        template_id="microsoft",
        target_email="test@example.com",
        use_logo=True
    )
    
    # Verify campaign data
    assert campaign["status"] == "active"
    assert "qr_code_path" in campaign
    assert "qr_code_url" in campaign
    
    # Verify file existence
    qr_path = campaign["qr_code_path"]
    assert os.path.exists(qr_path), f"QR code file not found at {qr_path}"
    assert os.path.getsize(qr_path) > 0, "QR code file is empty"
    
    # Verify Redis interaction
    mock_redis.set.assert_called()

def test_qr_logo_integration(mock_redis):
    """
    Verify that logo integration works (no errors thrown) and file is created.
    """
    manager = SocialEngineeringManager()
    
    # Check if logo exists for google
    logo_path = manager._get_logo_path("google")
    if not logo_path:
        pytest.skip("Google logo not found, skipping logo test")
        
    campaign = manager.create_campaign(
        name="Logo Test Campaign",
        template_id="google",
        use_logo=True
    )
    
    assert os.path.exists(campaign["qr_code_path"])
