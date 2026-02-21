import os
import sys
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
from phishing_server import app


def test_health_endpoint():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"


def test_generate_qr_cli(tmp_path):
    out = tmp_path / "tmp_qr.png"
    cmd = [sys.executable, "-m", "core.cli.main", "safe-qr", "--url", "http://localhost:9999/", "--out", str(out)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert p.returncode == 0
    assert out.exists()
    assert out.stat().st_size > 0

