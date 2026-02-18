import pytest
from core.mutation.engine import MutationEngine
from core.mutation.scanner import DetectionScanner

def test_html_mutation():
    engine = MutationEngine()
    original_html = '<div id="login" class="container form-group">Content</div>'
    
    mutated = engine.mutate_html(original_html)
    
    # Check that IDs and Classes are changed
    assert 'id="login"' not in mutated
    assert 'class="container form-group"' not in mutated
    
    # Check that structure is preserved (div still exists)
    assert '<div' in mutated

def test_js_mutation():
    engine = MutationEngine()
    original_js = "var secret = 'password123';"
    
    mutated = engine.mutate_js(original_js)
    
    # Check string splitting
    assert "'password123'" not in mutated
    assert "+" in mutated

def test_detection_scanner():
    scanner = DetectionScanner()
    
    # Test Risky Content
    risky_content = "<script>eval('bad_code'); document.write('hacked');</script>"
    result = scanner.scan_content(risky_content)
    
    assert result["status"] == "RISKY"
    assert "eval_usage" in result["matches"]
    assert "document_write" in result["matches"]
    assert result["score"] >= 0.4

    # Test Safe Content
    safe_content = "<div>Hello World</div>"
    result = scanner.scan_content(safe_content)
    
    assert result["status"] == "SAFE"
    assert result["score"] == 0.0
