import pytest
from core.redirect.fingerprint import BrowserFingerprint, fp_validator

def test_fingerprint_validation_valid_human():
    """Test valid human fingerprint."""
    fp = BrowserFingerprint(
        userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        platform="MacIntel",
        language="en-US",
        screen={
            "width": 1920,
            "height": 1080,
            "availWidth": 1920,
            "availHeight": 1080,
            "colorDepth": 24,
            "pixelRatio": 1.0
        },
        window={
            "width": 1920,
            "height": 1080
        },
        timezone={
            "offset": 0,
            "name": "UTC"
        },
        webgl={
            "vendor": "Google Inc. (Apple)",
            "renderer": "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
            "extensions": ["EXT_texture_filter_anisotropic", "OES_standard_derivatives"],
            "shadingLanguageVersion": "WebGL GLSL ES 1.0",
            "version": "WebGL 1.0"
        },
        canvasHash="somehash",
        interaction={
            "mouseMoves": 10,
            "scrollEvents": 5,
            "keyPresses": 2,
            "timeOnPage": 2000
        }
    )
    assert fp_validator.validate(fp) is True

def test_fingerprint_validation_headless_resolution():
    """Test headless browser resolution detection."""
    fp = BrowserFingerprint(
        userAgent="Mozilla/5.0 (HeadlessChrome)",
        platform="Linux x86_64",
        language="en-US",
        screen={
            "width": 800,
            "height": 600,
            "availWidth": 800,
            "availHeight": 600,
            "colorDepth": 24,
            "pixelRatio": 1.0
        },
        window={
            "width": 800,
            "height": 600
        },
        timezone={
            "offset": 0,
            "name": "UTC"
        },
        webgl={
            "renderer": "Mesa OffScreen",
            "vendor": "Mesa/X.org",
            "extensions": [],
            "shadingLanguageVersion": "WebGL GLSL ES 1.0",
            "version": "WebGL 1.0"
        },
        interaction={
            "mouseMoves": 0,
            "scrollEvents": 0,
            "keyPresses": 0,
            "timeOnPage": 1000
        }
    )
    # Test with very small resolution
    fp.screen.width = 50
    fp.screen.height = 50
    # Should fail because of very small resolution
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_webdriver():
    """Test webdriver detection."""
    fp = BrowserFingerprint(
        userAgent="Mozilla/5.0",
        platform="MacIntel",
        language="en-US",
        screen={
            "width": 1920,
            "height": 1080,
            "availWidth": 1920,
            "availHeight": 1080,
            "colorDepth": 24,
            "pixelRatio": 1.0
        },
        window={
            "width": 1920,
            "height": 1080
        },
        timezone={
            "offset": 0,
            "name": "UTC"
        },
        webgl={
            "renderer": "Google Inc.",
            "vendor": "Google Inc.",
            "extensions": ["EXT_texture_filter_anisotropic"],
            "shadingLanguageVersion": "WebGL GLSL ES 1.0",
            "version": "WebGL 1.0"
        },
        botSignals=["webdriver.detected"],  # Explicit bot signal
        interaction={
            "mouseMoves": 10,
            "scrollEvents": 5,
            "keyPresses": 2,
            "timeOnPage": 2000
        }
    )
    # Should fail because of bot signals
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_webgl_renderer():
    """Test WebGL renderer detection (VM/Headless)."""
    fp = BrowserFingerprint(
        userAgent="Mozilla/5.0",
        platform="Linux x86_64",
        language="en-US",
        screen={
            "width": 1920,
            "height": 1080,
            "availWidth": 1920,
            "availHeight": 1080,
            "colorDepth": 24,
            "pixelRatio": 1.0
        },
        window={
            "width": 1920,
            "height": 1080
        },
        timezone={
            "offset": 0,
            "name": "UTC"
        },
        webgl={
            "renderer": "SwiftShader", # Software renderer
            "vendor": "Google Inc.",
            "extensions": [],
            "shadingLanguageVersion": "WebGL GLSL ES 1.0",
            "version": "WebGL 1.0"
        },
        interaction={
            "mouseMoves": 5,
            "scrollEvents": 2,
            "keyPresses": 1,
            "timeOnPage": 1500
        }
    )
    # Should fail because of software WebGL renderer
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_behavior():
    """Test valid behavior (no movement, fast) - should pass now."""
    fp = BrowserFingerprint(
        userAgent="Mozilla/5.0",
        platform="MacIntel",
        language="en-US",
        screen={
            "width": 1920,
            "height": 1080,
            "availWidth": 1920,
            "availHeight": 1080,
            "colorDepth": 24,
            "pixelRatio": 1.0
        },
        window={
            "width": 1920,
            "height": 1080
        },
        timezone={
            "offset": 0,
            "name": "UTC"
        },
        webgl={
            "renderer": "Google Inc.",
            "vendor": "Google Inc.",
            "extensions": ["EXT_texture_filter_anisotropic"],
            "shadingLanguageVersion": "WebGL GLSL ES 1.0",
            "version": "WebGL 1.0"
        },
        interaction={
            "mouseMoves": 0,
            "scrollEvents": 0,
            "keyPresses": 0,
            "timeOnPage": 100  # Very fast
        }
    )
    assert fp_validator.validate(fp) is False

def test_fingerprint_validation_platform_mismatch():
    """Test platform mismatch (Spoofed UA)."""
    fp = BrowserFingerprint(
        userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        platform="MacIntel", # Actual platform Mac, UA claims Windows
        language="en-US",
        screen={
            "width": 1920,
            "height": 1080,
            "availWidth": 1920,
            "availHeight": 1080,
            "colorDepth": 24,
            "pixelRatio": 1.0
        },
        window={
            "width": 1920,
            "height": 1080
        },
        timezone={
            "offset": 0,
            "name": "UTC"
        },
        webgl={
            "renderer": "Google Inc.",
            "vendor": "Google Inc.",
            "extensions": ["EXT_texture_filter_anisotropic"],
            "shadingLanguageVersion": "WebGL GLSL ES 1.0",
            "version": "WebGL 1.0"
        },
        interaction={
            "mouseMoves": 10,
            "scrollEvents": 5,
            "keyPresses": 2,
            "timeOnPage": 2000
        }
    )
    assert fp_validator.validate(fp) is False
