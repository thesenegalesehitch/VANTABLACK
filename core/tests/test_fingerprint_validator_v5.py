import pytest
from core.redirect.fingerprint import BrowserFingerprint, fp_validator

def test_fingerprint_validation_hardware_concurrency_low():
    """Test validation fails for low hardware concurrency (e.g. single core VM)."""
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
        is_webdriver=False,
        hardware_concurrency="0"  # Suspiciously low
    )
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_device_memory_low():
    """Test validation fails for low device memory."""
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
        is_webdriver=False,
        hardware_concurrency="4",
        device_memory="0.1"  # 100MB RAM? Suspicious.
    )
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_valid_modern_browser():
    """Test validation passes for a realistic modern browser."""
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
        mouse_movements=15,
        scroll_events=10,
        time_on_page=5000,
        is_webdriver=False,
        hardware_concurrency="8",
        device_memory="8"
    )
    assert fp_validator.validate(fp) is True
