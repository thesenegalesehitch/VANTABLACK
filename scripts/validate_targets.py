import subprocess
import sys
import time
import requests
import re

TARGETS = [
    "twitter","x","google","microsoft","linkedin","facebook","instagram",
    "amazon","apple","discord","dropbox","github","paypal","reddit","slack","tiktok","yahoo"
]

def wait_for_health(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if r.status_code == 200 and r.json().get("status") == "ok":
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False

def check_login(port):
    r = requests.get(f"http://127.0.0.1:{port}/login", timeout=5)
    return r.status_code == 200 and ("<html" in r.text.lower() or "<!doctype html" in r.text.lower())

def try_cloudflared(port):
    try:
        subprocess.run(["cloudflared","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        return None
    proc = subprocess.Popen(
        ["cloudflared","tunnel","--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    url = None
    start = time.time()
    while time.time() - start < 20:
        line = proc.stderr.readline()
        if not line:
            time.sleep(0.1)
            continue
        m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if m:
            url = m.group(0)
            break
    return (proc, url)

def main():
    port = 8090
    all_ok = True
    results = {}

    for target in TARGETS:
        cmd = [sys.executable, "phishing_server.py", "--target", target, "--port", str(port)]
        server = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        ok = wait_for_health(port)
        if not ok:
            results[target] = {"local":"down"}
            server.terminate()
            server.wait(timeout=5)
            all_ok = False
            continue
        page_ok = check_login(port)
        local_status = "ok" if page_ok else "fail"
        remote_status = "skipped"
        cf = try_cloudflared(port)
        if cf and cf[1]:
            cf_proc, url = cf
            try:
                r = requests.get(url + "/login", timeout=10)
                remote_status = "ok" if r.status_code == 200 else "fail"
            except Exception:
                remote_status = "fail"
            cf_proc.terminate()
        results[target] = {"local": local_status, "remote": remote_status}
        server.terminate()
        server.wait(timeout=5)
        time.sleep(0.5)

    print(results)
    if not all_ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
