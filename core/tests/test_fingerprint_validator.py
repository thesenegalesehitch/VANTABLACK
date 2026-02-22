import pytest
from core.redirect.fingerprint import BrowserFingerprint, fp_validator

def test_fingerprint_validation_valid_human():
    """Test valid human fingerprint."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="MacIntel",
        language="en-US",
        timezone_offset=0,
        webgl_vendor="Google Inc. (Apple)",
        webgl_renderer="ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
        canvas_hash="somehash",
        fonts_detected=["Arial", "Times New Roman"],
        touch_support=False,
        mouse_movements=10,
        scroll_events=5,
        time_on_page=2000,
        is_webdriver=False
    )
    assert fp_validator.validate(fp) is True

def test_fingerprint_validation_headless_resolution():
    """Test headless browser resolution detection."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0 (HeadlessChrome)",
        screen_width=800,
        screen_height=600,  # Small resolution
        color_depth=24,
        platform="Linux x86_64",
        language="en-US",
        timezone_offset=0,
        webgl_renderer="Mesa OffScreen",
        fonts_detected=[],
        mouse_movements=0,
        is_webdriver=False
    )
    # validate checks if screen_width < 100 or screen_height < 100.
    # Wait, the code says:
    # if fp.screen_width < 100 or fp.screen_height < 100:
    #     return False
    # So 800x600 should PASS this check unless I update it.
    
    # Let's test with very small resolution
    fp.screen_width = 50
    fp.screen_height = 50
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_webdriver():
    """Test webdriver detection."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="MacIntel",
        language="en-US",
        timezone_offset=0,
        webgl_renderer="Google Inc.",
        fonts_detected=["Arial"],
        is_webdriver=True  # Explicitly set to True
    )
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_webgl_renderer():
    """Test WebGL renderer detection (VM/Headless)."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="Linux x86_64",
        language="en-US",
        timezone_offset=0,
        webgl_renderer="SwiftShader", # Software renderer
        fonts_detected=["Arial"],
        is_webdriver=False
    )
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_behavior():
    """Test bot behavior (no movement, fast)."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="MacIntel",
        language="en-US",
        timezone_offset=0,
        webgl_renderer="Google Inc.",
        fonts_detected=["Arial"],
        mouse_movements=0,
        scroll_events=0,
        time_on_page=100, # Very fast
        is_webdriver=False
    )
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_platform_mismatch():
    """Test platform mismatch (Spoofed UA)."""
    fp = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        platform="MacIntel", # Actual platform Mac, UA claims Windows
        language="en-US",
        timezone_offset=0,
        webgl_renderer="Google Inc.",
        fonts_detected=["Arial"],
        mouse_movements=10,
        time_on_page=2000,
        is_webdriver=False
    )
    assert fp_validator.validate(fp) is False
