import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from core.delivery.templates import TemplateEngine
from core.delivery.smtp import SMTPConfig, SMTPClient
from core.delivery.tracking import TrackingService

@pytest.mark.asyncio
async def test_mjml_template_rendering():
    engine = TemplateEngine()
    
    mjml_content = """
    <mjml>
      <mj-body>
        <mj-section>
          <mj-column>
            <mj-text>Hello {{ name }}!</mj-text>
          </mj-column>
        </mj-section>
      </mj-body>
    </mjml>
    """
    
    context = {"name": "Target"}
    
    result = engine.render(mjml_content, context)
    
    assert "Hello Target!" in result["html"]
    assert "Hello Target!" in result["text"]
    assert "<mj-text>Hello Target!</mj-text>" in result["mjml"]

@pytest.mark.asyncio
async def test_smtp_client_config():
    config = SMTPConfig(
        host="smtp.example.com",
        username="user",
        password="password",
        from_name="Security Team",
        from_email="security@example.com"
    )
    
    client = SMTPClient(config)
    assert client.config.port == 587
    assert client.config.use_tls is True

@pytest.mark.asyncio
async def test_tracking_pixel_generation():
    service = TrackingService()
    pixel = service.generate_tracking_pixel("camp123", "target456")
    
    assert 'src="/track/open/camp123/target456"' in pixel
    assert 'style="display:none' in pixel

@pytest.mark.asyncio
async def test_link_wrapping():
    service = TrackingService()
    original_url = "https://example.com/login"
    wrapped = service.wrap_link(original_url, "camp1", "tgt1")
    
    assert "/track/click/camp1/tgt1" in wrapped
    assert "?u=" in wrapped
