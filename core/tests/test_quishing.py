import os
import subprocess
import sys
import tempfile

def test_quishing_generate(tmp_path):
    out = tmp_path / "q.png"
    r = subprocess.run([sys.executable, "quishing.py", "--url", "http://example.com", "--out", str(out)], capture_output=True, text=True)
    assert out.exists()
    assert r.returncode == 0

def test_qr_decode_optional(tmp_path):
    out = tmp_path / "q.png"
    subprocess.run([sys.executable, "quishing.py", "--url", "http://example.com", "--out", str(out)], check=True)
    p = subprocess.run([sys.executable, "scripts/qr_tools.py", str(out)], capture_output=True, text=True)
    assert p.returncode in (0,1)
