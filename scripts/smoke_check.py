import os
import sys
import socket
import platform
from pathlib import Path
from time import time
from core.qr_link_system import QRLinkSystem, QRConfig


def print_header():
    print("Vantablack Smoke Check")
    print("=" * 48)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"CWD: {Path.cwd()}")


def check_imports():
    ok = True
    mods = ["fastapi", "qrcode", "PIL", "requests"]
    for m in mods:
        try:
            __import__(m)
            print(f"[OK] import {m}")
        except Exception as e:
            print(f"[FAIL] import {m}: {e}")
            ok = False
    return ok


def check_links(system: QRLinkSystem):
    targets = [
        ("LocalHealth", "http://localhost:8080/health"),
        ("Example", "https://example.com"),
        ("Invalid", "http://invalid.localdomain.test"),
        ("Malformed", "ht!tp://bad")
    ]
    for name, url in targets:
        start = time()
        ok, result, details = system.validate_url(url, timeout=3.0)
        dur = time() - start
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name} {url} {result.value} {dur:.2f}s")
    return True


def check_qr(system: QRLinkSystem):
    out = Path("qr_smoke.png")
    if out.exists():
        try:
            out.unlink()
        except Exception:
            pass
    cfg = QRConfig()
    ok, msg = system.generate_qr("https://example.com", str(out), cfg)
    if not ok:
        print(f"[FAIL] QR gen: {msg}")
        return False
    print(f"[OK] QR gen: {out} {out.stat().st_size} bytes")
    success, decoded = system.decode_qr(str(out))
    if success and decoded:
        print(f"[OK] QR decode: {decoded[0]}")
    else:
        print("[WARN] QR decode not available")
    return True


def check_ports():
    ports = [8080, 8000, 8888]
    for p in ports:
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", p))
            print(f"[OK] Port {p} reachable")
        except Exception:
            print(f"[INFO] Port {p} not reachable")
        finally:
            try:
                s.close()
            except Exception:
                pass
    return True


def main():
    print_header()
    imports_ok = check_imports()
    system = QRLinkSystem()
    check_links(system)
    check_qr(system)
    check_ports()
    if not imports_ok:
        sys.exit(1)
    print("Smoke check complete")


if __name__ == "__main__":
    main()
