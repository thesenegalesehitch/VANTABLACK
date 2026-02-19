import requests
import json
import time
import os

# Configuration
PROXY_URL = "https://localhost:8443"
LOGIN_PATH = "/common/login"
TARGET_URL = f"{PROXY_URL}{LOGIN_PATH}"

# Victim Data
USERNAME = "victim@example.com"
PASSWORD = "P@ssw0rd123!"

def simulate_attack():
    print(f"[*] Starting simulated attack against {TARGET_URL}")
    
    session = requests.Session()
    session.verify = False # Ignore self-signed certs
    session.headers.update({
        "Host": "login.localhost",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    })
    
    # Step 1: Landing Page (GET)
    try:
        print("[*] Visiting landing page...")
        resp = session.get(TARGET_URL)
        print(f"[+] Landing page loaded. Status: {resp.status_code}")
        
        # Check if we got a session cookie
        if 'vanta_sid' in session.cookies:
            print(f"[+] Session ID established: {session.cookies['vanta_sid']}")
        else:
            print("[-] Warning: No vanta_sid cookie received yet.")
            
    except Exception as e:
        print(f"[-] Error visiting landing page: {e}")
        return

    # Step 2: Submit Username (POST)
    # Microsoft flow usually posts username first
    print("[*] Submitting username...")
    payload_user = {
        "loginfmt": USERNAME,
        "passwd": "", # Sometimes empty in first step
        "flowToken": "dummy_token" # Might be needed if strict
    }
    
    try:
        resp = session.post(TARGET_URL, data=payload_user)
        print(f"[+] Username submitted. Status: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error submitting username: {e}")

    # Step 3: Submit Password (POST)
    print("[*] Submitting password...")
    payload_pass = {
        "loginfmt": USERNAME,
        "passwd": PASSWORD,
        "flowToken": "dummy_token_2"
    }
    
    try:
        resp = session.post(TARGET_URL, data=payload_pass)
        print(f"[+] Password submitted. Status: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error submitting password: {e}")

    # Step 4: Verify Capture
    print("[*] Verifying capture in data/sessions.json...")
    time.sleep(2) # Allow async write
    
    try:
        with open("data/sessions.json", "r") as f:
            data = json.load(f)
            
        found = False
        for sid, s_data in data.items():
            creds = s_data.get("credentials", [])
            for c in creds:
                if c.get("username") == USERNAME and c.get("password") == PASSWORD:
                    print(f"[SUCCESS] Credentials captured for session {sid}!")
                    found = True
                    break
            if found: break
            
        if not found:
            print("[FAILURE] Credentials NOT found in sessions.json")
            # Debug: Print last session
            # print(json.dumps(list(data.values())[-1], indent=2))
            
    except Exception as e:
        print(f"[-] Error reading sessions.json: {e}")

if __name__ == "__main__":
    # Suppress insecure request warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    simulate_attack()
